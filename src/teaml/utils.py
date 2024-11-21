
def single_type(items):
    types = set(type(x) for x in items)
    if len(types) == 1:
        return type(items[0])
    if types == {int, float}:
        return float
    return None

def munge(key):
    if not key:
        return key
    if isinstance(key, list):
        key = [name.replace('.', '') for name in key]
        key = '.'.join(key)
    return key.replace(' ', '').lstrip('=')
