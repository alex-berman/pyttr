class ActionRule:
    def __init__(self, kb):
        self.kb = kb

    def preconditions(self):
        raise NotImplementedError()

    def effects(self, **kwargs):
        raise NotImplementedError()


class SpecificTypeJudgementAct:
    def __init__(self, symbol, judged_type):
        self.symbol = symbol
        self.judged_type = judged_type


class CreationAct:
    def __init__(self, type_to_create):
        self.type_to_create = type_to_create

    def __repr__(self):
        return "CreationAct(" + repr(self.type_to_create) + ")"
