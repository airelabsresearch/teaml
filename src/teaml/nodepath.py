from pathlib import PurePath

class NodePath(PurePath):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __repr__(self):
        return f'{str(self)}'

