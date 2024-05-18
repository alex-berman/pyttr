from utils import show


class CreateAct:
    # Create witness of type 'ty'
    def __init__(self, ty):
        self.ty = ty

    def __str__(self):
        return 'CreateAct(' + show(self.ty) + ')'