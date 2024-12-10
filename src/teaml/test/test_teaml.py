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
    bad_ref: =total + missing
    ambiguous_ref: =cap + 2
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
    broken = tea['broken']
    raw = tea.raw('broken')
    assert raw == broken.raw
    assert tea.errors == [
        "#error(type unsupported operand type(s) for +:int and str)",
        '#error(Key:missing)',
        '#error(Ambigous:cap matches outer.inputs.mixed level.capacity, outer.inputs.mixed level.capacity value, outer.outputs.capacity)',
    ]

def test_copy():
    # https://linear.app/airelabs/issue/AIR-238/teaml-init-should-deepcopy-dicts
    data = computed1().root
    tea = tml.Teaml(data)
    assert tea['capacity value'].value == 100
    tea['capacity value']= 200
    tea = tml.Teaml(data)
    assert tea['capacity value'].value == 100

def test_key_error():
    tea = computed1()
    assert tea['bad_ref'].value == '#error(Key:missing)'
    assert tea['ambiguous_ref'].value == '#error(Ambigous:cap matches outer.inputs.mixed level.capacity, outer.inputs.mixed level.capacity value, outer.outputs.capacity)'
