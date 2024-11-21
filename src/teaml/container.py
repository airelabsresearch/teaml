"""
Container utilities for nested dictionaries
"""

from collections import namedtuple

from teaml.utils import munge

def child_dicts(parent:dict):
    return [(k,v) for (k,v) in parent.items() if isinstance(v, dict)]

def find_container(node:dict, search:str):
    """
    Find the best match for a search pattern

    Args:
        node (dict): a nested dictionary
        search (str): a search pattern

    Search can be separated by periods to indicate nested keys, and nesting may jump levels.

    Returns:
        (container, key, value, path): the container and key of the best match

    Raises:
        ValueError: if no, or multiple matches are found
    """
    Result = namedtuple('Result', ['container', 'key', 'value', 'path'])
    leaves = walk_containers(node, search)
    if not leaves:
        raise KeyError(search)

    if len(leaves) > 1 and leaves[0].matches.score == leaves[1].matches.score:
        paths = [l.path for l in leaves]
        raise ValueError(f"Multiple matches for {search}: {paths}")

    container, key, path, _ = leaves[0]
    return Result(container, key, container[key], path)

def walk_containers(node:dict, search:str):
    """
    Walks a nested dictionary `node`

    Args:
        node (dict): a nested dictionary
        search (str): a search pattern

    Returns:
        list: a list of (container, key, path, matches) tuples
    """
    Result = namedtuple('Result', ['container', 'key', 'path', 'matches'])
    parts = munge(search).split('.')
    # first pass, find any match on the last key part
    leaves = list(_walk_containers(node, parts[-1]))
    # second pass, compare full dotted paths
    leaves = [(container, key, path, PathMatch(path=path, search=parts)) for (container, key, path) in leaves]

    # third pass, filter out conflicting key parts
    leaves= [l for l in leaves if l[3].score]
    leaves = sorted(leaves, key=lambda x: x[3].score, reverse=True)
    leaves = [Result(*l) for l in leaves]
    return leaves

def key_matches(key:str, search:str):
    """
    Returns True if `key` matches `search` pattern

    Args:
        key (str): a key to match
        search (str): a search pattern

    Returns:
        bool: True if `key` matches `search`
    """
    return munge(key).startswith(munge(search))

class PathMatch:
    def marker(self, key, search):
        """
        Returns a marker for the pair
        """
        key = munge(key)
        search = munge(search)
        if key == search:
            return '='
        if key.startswith(search):
            return '/'
        return '_'

    def __init__(self, path:list, search:list):
        self.path = path
        self.search = search

    @property
    def last_word_score(self):
        """
        Returns the score of the last word
        """
        if not self.pattern:
            return 0
        last = self.pattern[-1]
        if last == '=':
            return 200
        if last == '/':
            return 100
        if last == '_':
            return 0
        raise ValueError(f"Unknown pattern: {last}")

    @property
    def inner_jumps(self):
        """
        Returns the number of inner jumps

        These are gaps between matches, but exclude open left sides
        """
        return self.pattern.lstrip('_').count('_')

    @property
    def score(self):
        """
        Returns the score of matches
        """
        return self.last_word_score - self.inner_jumps * 10

    @property
    def pattern(self):
        """
        Returns the pattern of matches
        """
        # Require that the last key matches
        if not self.marker(self.path[-1], self.search[-1]):
            return ''

        path = self.path[:]
        search = self.search[:]
        pattern = []
        while path and search:
            elem = self.marker(path[-1], search[-1])
            if elem in ('=', '/'):
                search.pop()
            pattern.insert(0, elem)
            path.pop()
        if search:
            return ''
        pattern = ['_'] * len(path) + pattern
        pattern = ''.join(pattern)
        return pattern

    def __repr__(self):
        return f"'{self.pattern}':{self.score}"

def path_matches(path:list, search:list):
    """
    Returns the list of keys that fit the search pattern.

    Args:
        path (list): a list of keys
        search (list): a list of keys to search for

    Returns:
        list: a list of matching keys from `path`
    """
    # Require that the last key matches
    if not key_matches(path[-1], search[-1]):
        return []
    path = path[:]
    search = search[:]
    matches = []
    while path and search:
        if key_matches(path[-1], search[-1]):
            matches.insert(0, search.pop())
        path.pop()
    if search:
        return []
    return matches

def _walk_containers(node:dict, search:str, path:list=None):
    """
    Walks a nested dictionary `node`
    looks for keys that partially match `search`

    yields (container, key, path) tuples
    """
    path = path or []
    if not search:
        return
    for key in node:
        if key_matches(key, search):
            yield (node, key, path + [key])
    for (key, child) in child_dicts(node):
        yield from _walk_containers(child, search, path + [key])
