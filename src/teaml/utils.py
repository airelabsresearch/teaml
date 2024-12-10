import re

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

def sanitize_formula(expression):
    """
    Sanitizes Excel formulas by:
    1. Replacing single-quoted sheet references with valid Python variable names.
    2. Replacing '!' with '.' outside of quotes.
    """
    # Step 1: Sanitize single-quoted sheet references
    def sanitize_sheet(match):
        sheet_name = match.group(1)
        print("SHEET NAME", sheet_name)
        sanitized_name = re.sub(r"[^a-zA-Z0-9_]", "", sheet_name)
        while sanitized_name and sanitized_name[0].isdigit():
            sanitized_name = sanitized_name[1:]
        return sanitized_name

    # Replace single-quoted sheet names followed by '!'
    sanitized_expression = re.sub(r"'([^']*)'(?=!)", sanitize_sheet, expression)

    # Step 2: Replace all '!' with '.' outside of quotes
    def replace_exclamation(match):
        part = match.group(0)
        print("PART", part)
        if part.startswith("'") or part.startswith('"'):
            # Preserve quoted parts as is
            return part
        else:
            # Replace '!' with '.' in non-quoted parts
            # return part.replace("!", ".")
            return (part
                .replace("!", ".")
                .replace(" ", "")
            )

    # Match quoted strings and other parts of the formula
    pattern = r"((?:'[^']*'|\"[^\"]*\")|[^'\"!]+|!)"
    final_expression = re.sub(pattern, replace_exclamation, sanitized_expression)

    return final_expression
