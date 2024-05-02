class ActionRule:
    def __init__(self, frame):
        self.frame = frame

    def preconditions(self):
        raise NotImplementedError()

    def effect(self, **kwargs):
        raise NotImplementedError()


class SpecificTypeJudgementAct:
    def __init__(self, symbol, judged_type):
        self.symbol = symbol
        self.judged_type = judged_type


class CreationAct:
    def __init__(self, symbol, type_to_create):
        self.symbol = symbol
        self.type_to_create = type_to_create

    def __repr__(self):
        return "CreationAct(" + repr(self.symbol) + ", "  + repr(self.type_to_create) + ")"
