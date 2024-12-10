"""
"""

from collections import namedtuple
from copy import deepcopy
from pathlib import Path
from typing import List
import yaml

from teaml.container import find_container
from teaml.node import Node, NodeDict, NodeNone, NodeRange
from teaml.formula.tea_parser import computer, create_namedtuples, filter_bases
from teaml.formula.vector import Vector
from teaml.utils import single_type, munge

class Teaml:
    @classmethod
    def loads(cls, yaml_str):
        # TODO: run validations
        return cls(yaml.safe_load(yaml_str))

    @classmethod
    def load(cls, filename):
        return cls.loads(open(filename).read())

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.dumps())

    @classmethod
    def samples(self):
        return {
            "finance101": Path(__file__).parent / "Finance101.yaml",
        }

    @classmethod
    def sample(cls, name):
        if not name in cls.samples():
            raise ValueError(f"Unknown sample: {name}")
        return Teaml.load(cls.samples()[name])

    def dumps(self):
        return yaml.dump(self.root)

    def find(self, node):
        if isinstance(node, Node):
            return node
        result = find_container(self.root, node)
        return Node.new(result.value, path=result.path)

    def find_container(self, key):
        if isinstance(key, Node):
            key = key.key
        return find_container(self.root, key)

    def raw(self, key):
        container = self.find_container(key)
        return container.value

    def get_value(self, key):
        try:
            node = self.find(key)
        except KeyError:
            return f'#error(Key:{key})'
        except AmbigousNameError as e:
            return f'#error(Ambigous:{e})'
        return node.value

    def __getitem__(self, key):
        return self.find(key)

    def __setitem__(self, key, value):
        container = self.find_container(key)
        container.container[container.key] = value


    @property
    def formula_nodes(self):
        return [node for node in walk_nodes(self.root) if node.formula is not None]

    # def set_value(self, key, value):
    #     if isinstance(value, Node):
    #         raise ValueError(f"Node: {value}")
    #     container = self.find_container(key)
    #     existing = container.container[container.key]
    #     container.container[container.key] = value

    def compute(self, key=None):
        if key is not None:
            return self.compute_node(key)
        for node in self.formula_nodes:
            if isinstance(node, NodeNone):
                self.compute_node(node.key)
        if self.errors:
            return self.errors

    def compute_node(self, key):
        container = self.find_container(key)
        existing_node = Node.new(container.value)

        for name in existing_node.references:
            try:
                child = self.find(name)
            except KeyError:
                return f'#error(key: {name})'
            if isinstance(child, NodeNone):
                self.compute_node(name)

        context = self.build_context(key)
        formula = existing_node.formula
        if not formula:
            return existing_node.value
        formula = munge(formula) # TODO replace with code specific to formula
        result = computer.compute(formula, context)
        # TODO: Move this
        self[key] = f'={formula} ={result}'
        return result

    TraceReport = namedtuple('TraceReport', ['key', 'value', 'depth', 'references'])
    def trace(self, node, seen=None, depth=0, report=None):
        if not isinstance(node, Node) and isinstance(node, str):
            node = self.find(node)
        seen = seen or set()
        report = report or []

        if node.key in seen:
            return
        refs = tuple(sorted(set(node.references)))
        refs = {k:1 for k in refs}
        refs = filter_bases(refs)
        refs = tuple(sorted(refs.keys()))

        seen.add(node.key)
        report.append(self.TraceReport(node.key, node.value, depth, refs))

        for ref in refs:
            try:
                source = self.find(ref)
            except KeyError:
                report.append(self.TraceReport(ref, '#error(Key)', depth + 1, []))
                continue
            self.trace(source, seen=seen, depth=depth + 1, report=report)
        return report

    @property
    def errors(self):
        return [node for node in walk_nodes(self.root) if node.is_error]

    def unmet_references(self, node):
        if not isinstance(node, Node) and isinstance(node, str):
            node = self.find(node)
        return [name for name in node.references if isinstance(self.find(name), NodeNone)]

    def references(self, node):
        refs = getattr(node, 'references', [])
        refs = refs or self.find(node).references
        refs = [self.find(name) for name in refs]
        return refs

    def build_context(self, node):
        if not isinstance(node, Node) and isinstance(node, str):
            node = self.find(node)
        context = {name: self.find(name).value for name in node.references}
        # TODO: move this
        for k in context:
            if isinstance(context[k], list):
                context[k] = Vector(context[k])
        context = create_namedtuples(context)
        return context

    def can_compute(self, node, context):
        needs = [self.find(name).key for name in node.references]
        return all([n in context for n in needs])

    def __init__(self, root):
        self.root = deepcopy(root)

    def copy(self):
        return Teaml(deepcopy(self.root))

    def reset(self):
        tea = self.copy()
        data = transform(tea.root, reset_value_transformer)
        return Teaml(data)

    def df(self, key, index=None):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("Pandas is required for this feature")

        node = self.find(key)
        if isinstance(node, NodeRange):
            return pd.DataFrame(node.value)
        df = pd.DataFrame(self.as_columns(key))
        if index:
            df = df.set_index(index)
        return df

    def as_columns(self, key):
        parent = self.find(key)
        if not isinstance(parent, NodeDict):
            raise ValueError(f"Can't make columns of {type(parent)}")
        range_nodes = [n for n in walk_nodes(parent) if isinstance(n, NodeRange)]
        lengths = [len(n.value) for n in range_nodes]
        if len(set(lengths)) > 1:
            raise ValueError(f"Unequal lengths: {lengths}")
        return {n.key: n.value for n in range_nodes}

    def __iter__(self):
        return iter(walk_nodes(self.root))

    def __repr__(self):
        node_count = len(list(iter(self)))
        return f"Teaml: {node_count} nodes"

def load(filename):
    return Teaml.load(filename)

def sample(name):
    return Teaml.sample(name)

def unnest(name):
    parts = name.split('.', 2)
    first = parts[0]
    rest = parts[1] if len(parts) > 1 else None
    return first, rest

def can_match(path, partial):
    # print("CAN MATCH", path, partial)
    if not path:
        return False
    name = munge(path[-1])
    partial = munge(partial)
    # print("CAN MATCH", name, partial)
    return name.startswith(partial)

def sort_candidates(candidates):
    # TODO: refine multi-match scoring, for now take the shortest
    return sorted(candidates, key=lambda c: len(c[1]))

def find(node, partial, path=None):
    assert isinstance(node, dict), f"Expected dict, got {type(node)}"
    assert isinstance(partial, str), f"Expected str, got {type(partial)}"
    path = path or []
    first, rest = unnest(munge(partial))
    candidates = [(c, p) for (c, p) in walk(node) if can_match(p, first)]
    candidates = sort_candidates(candidates)
    if len(candidates) == 0:
        raise ValueError(f'No match for {repr(first)}')
    if len(candidates) > 1:
        for c, p in candidates:
            # honor exact matches
            if munge(p[-1]) == first:
                candidates = [(c, p)]
                break
        else:
            raise ValueError(f"Ambiguous: {partial}")
    candidate = candidates[0] # only one now

    candidate, subpath = candidate
    path.extend(subpath)
    if not rest:
        candidate = Node.new(candidate, key=munge(path), path=path)
        return candidate
    return find(candidate, rest, path)

def walk_nodes(root):
    for (node, path) in walk(root):
        if node is not None:
            try:
                yield Node.new(node, key=path)
            except Exception as e:
                print(f"Error: {e}")
                print(f"Node: {node}")
                print(f"Path: {path}")
                raise e

def walk(node, path=None):
    path = path or []
    if isinstance(node, dict):
        if path:
            yield (node, path)
        for key, value in node.items():
            yield from walk(value, path + [key])
    elif isinstance(node, list):
        data_type = single_type(node)
        if data_type in (int, float, str):
            # Treat a list of scalars as a single range
            yield (node, path)
        elif data_type in (dict, list):
            # Continue to walk lists of objects
            if path:
                yield (node, path)
            for index, value in enumerate(node):
                yield from walk(value, path + [index])
        else:
            raise ValueError(f"Unrecognized list type: {data_type}")
    else:
        yield (node, path)

def transform(data, fn):
    if isinstance(data, dict):
        return {key: transform(value, fn) for key, value in data.items()}
    elif isinstance(data, list):
        return [transform(item, fn) for item in data]
    else:
        return fn(data)

def reset_value_transformer(data):
    if not isinstance(data, str):
        return data
    node = Node.new(data)
    if not node.formula:
        return data
    return node.formula
