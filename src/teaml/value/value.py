import builtins

currencies = {'USD':'$'}

def wrap(other):
    if not isinstance(other, Value):
        other = Value(other)
    return other

def match_arrays(a, b):
    print("Match:", a, type(a))
    print("Match:", b, type(b))
    return a, b

def listify(f):
    def inner(*args):
        return Value(list(f(*args)))
    return inner
sandbox = {
    'range':listify(builtins.range),
}


class Value:
    def __init__(self, value, units=None, currency=None, thousands=True):
        self.value = value
        self.units = units
        self.currency = currency
        self.thousands = thousands

    @classmethod
    def new(cls, value):
        if isinstance(value, int):
            return ValueInt(value)
        if isinstance(value, float):
            return ValueFloat(value)
        if isinstance(value, ValueRange):
            return ValueRange(value)


        for kind in [ValueFloat]:
            result = kind.new(value)
            if result is not None:
                return result
        if value.endswith('%'):
            return ValuePercentage(value)
        return cls(float(value))

    def __mul__(self, other):
        return Value(self.value * wrap(other).value)

    def __add__(self, other):
        print("ADD", self, wrap(other).value)
        match_arrays(self, other)
        return Value(self.value + wrap(other).value)

    def __radd__(self, other):
        return wrap(other) + self

    def __pow__(self, other):
        print("POW", self, wrap(other).value)
        return Value(self.value ** wrap(other).value)

    def __rpow__(self, other):
        print("RPOW", self, other)
        return Value(wrap(other).value ** self.value)

    def compute(self):
        return self.value


    # TODO: MOVE

    @property
    def display(self):
        v = str(self.value)
        if v.endswith('.0'):
            v = v[:-2]
        return v

    @property
    def as_int(self):
        try:
            return int(self.value)
        except:
            return None

    @property
    def as_float(self):
        try:
            return float(self.value)
        except:
            return None

    @property
    def as_num(self):
        if self.as_int is not None:
            return self.as_int
        if self.as_float is not None:
            return self.as_float
        return None

    def __str__(self):
        units = '' if self.units is None else f' {self.units}'
        return f'{self.display}{units}'

    def __repr__(self):
        return str(self)

class ValueRange(Value):
    pass

class ValueErr(Value):
    pass

class ValuePercentage(Value):
    def __init__(self, value):
        if value.endswith('%'):
            value = value.rstrip('%')
            value = float(value) / 100
        value = float(value)
        super().__init__(value)

    def __repr__(self):
        v = str(self.value * 100)
        if v.endswith('.0'):
            v = v[:-2]
        return f'{v}%'

class ValueInt(Value):
    def __init__(self, value, units=None, currency=None, thousands=True):
        super().__init__(int(value), units, currency, thousands)

    @classmethod
    def accept(cls, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    @classmethod
    def from_string(cls, value):
        if cls.accept(value):
            return cls(value)
        return None

class ValueFloat(Value):
    def __init__(self, value, units=None, currency=None, thousands=True):
        super().__init__(float(value), units, currency, thousands)

    @classmethod
    def accept(cls, value):
        try:
            float(value)
        except ValueError:
            return False
        return True

    @classmethod
    def new(cls, value):
        if cls.accept(value):
            return cls(value)
        return None
