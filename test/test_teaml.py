import yaml

import teaml as tml

def tea1():
    return tml.loads('''\
outer:
  inputs:
    mixed level:
      capacity: 300
      capacity value: 100
  outputs:
    capacity: 200
    label: one
    total: =mixed.capacity + mixed.capacity value
    broken: =total + label
''')

def computed1():
    tea = tea1()
    tea.compute()
    return tea

def test_plain():
    tea = computed1()
    assert tea['total'].value == 400

def test_str_add():
    tea = computed1()
    # assert str(tea['broken']) == "=total + label=#error(type: unsupported operand type(s) for +: 'int' and 'str')"
    print("TYPE",type(tea['broken'].detail))
    print("TYPE",isinstance(tea['broken'], tml.node.Node))
    print("VALUE",tea['broken'].value)
    assert tea['broken'].detail == {
    }
    assert tea['broken'].formula == '=total+label'
    assert tea['broken'] == "#error(type: unsupported operand type(s) for +: 'int' and 'str')"
    assert tea.errors == ["#error(type: unsupported operand type(s) for +: 'int' and 'str')"]
