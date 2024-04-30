class ActionRule:
    def __init__(self, arguments, preconditions, effect):
        self.arguments = arguments
        self.preconditions = preconditions
        self.effect = effect

    def show(self):
        return "ActionRule(arguments=" + str(self.arguments) + ", preconditions=" + str(self.preconditions) + \
               ", effect=" + str(self.effect) + ")"


class TypeJudgementAct:
    def __init__(self, symbol, judged_type):
        self.symbol = symbol
        self.judged_type = judged_type


class CreationAct:
    def __init__(self, symbol, type_to_create):
        self.symbol = symbol
        self.type_to_create = type_to_create

    def __repr__(self):
        return "CreationAct(" + repr(self.symbol) + ", "  + repr(self.type_to_create) + ")"
