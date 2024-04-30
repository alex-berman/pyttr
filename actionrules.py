class ActionRule:
    @staticmethod
    def argument_names():
        return []

    @staticmethod
    def preconditions(*args):
        return False

    @staticmethod
    def effect(*args):
        pass


class TypeJudgementAct:
    def __init__(self, symbol, judged_type):
        self.symbol = symbol
        self.judged_type = judged_type


class CreationAct:
    def __init__(self, symbol, type_to_create):
        self.symbol = symbol
        self.type_to_create = type_to_create
