from teaml.formula.vector import Vector

def test_pow():
    v = Vector([1, 2, 3])
    assert v ** 2 == [1, 4, 9]
    assert 2 ** v == [2, 4, 8]

def test_mul():
    a = Vector([1, 2, 4])
    b = Vector([4, 2, 1])
    assert a * b == [4, 4, 4]
    assert b * a == [4, 4, 4]
    assert a * 2 == [2, 4, 8]
    assert a * 2.5 == [2.5, 5, 10]

def test_div():
    a = Vector([1, 2, 4])
    b = Vector([4, 2, 1])
    assert a / b == [0.25, 1, 4]
    assert b / a == [4, 1, 0.25]
    assert a / 2 == [0.5, 1, 2]
    assert a / 2.5 == [0.4, 0.8, 1.6]

def test_add():
    a = Vector([1, 2, 3])
    b = Vector([3, 2, 1])
    assert a + b == [4, 4, 4]
    assert b + a == [4, 4, 4]
    assert a + 1 == [2, 3, 4]
    assert a + 1.5 == [2.5, 3.5, 4.5]

def test_sub():
    a = Vector([1, 2, 3])
    b = Vector([3, 2, 1])
    assert a - b == [-2, 0, 2]
    assert b - a == [2, 0, -2]
    assert a - 1 == [0, 1, 2]
    assert a - 1.5 == [-0.5, 0.5, 1.5]

def test_multi():
    a = Vector([1, 2, 3])
    assert a * 2 * 4 == [8, 16, 24]

def test_negative():
    a = Vector([1, 2, 3])
    assert -a == [-1, -2, -3]
