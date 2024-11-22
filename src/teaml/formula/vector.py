"""
"""

class Vector(list):
    def __pow__(self, other):
        assert isinstance(other, (int, float))
        return Vector([x ** other for x in self])

    def __rpow__(self, other):
        assert isinstance(other, (int, float))
        return Vector([other ** x for x in self])

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector([x * other for x in self])
        if isinstance(other, Vector):
            assert len(self) == len(other), f"Vector lengths: {len(self)} != {len(other)}"
            return Vector([x * y for x, y in zip(self, other)])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector([x / other for x in self])
        if isinstance(other, Vector):
            assert len(self) == len(other), f"Vector lengths: {len(self)} != {len(other)}"
            return Vector([x / y for x, y in zip(self, other)])

    def __rtruediv__(self, other):
        return other / self

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Vector([x + other for x in self])
        if isinstance(other, Vector):
            assert len(self) == len(other), f"Vector lengths: {len(self)} != {len(other)}"
            return Vector([x + y for x, y in zip(self, other)])

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Vector([x - other for x in self])
        if isinstance(other, Vector):
            assert len(self) == len(other), f"Vector lengths: {len(self)} != {len(other)}"
            return Vector([x - y for x, y in zip(self, other)])

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Vector([other - x for x in self])
        if isinstance(other, Vector):
            assert len(self) == len(other), f"Vector lengths: {len(self)} != {len(other)}"
            return Vector([y - x for x, y in zip(self, other)])

    def __neg__(self):
        return Vector([-x for x in self])
