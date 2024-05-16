class ActionRule:
    def __init__(self, agent):
        self.agent = agent

    def preconditions(self):
        raise NotImplementedError()

    def apply_effects(self, **kwargs):
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
