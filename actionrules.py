class ActionRule:
    def __init__(self, agent):
        self.agent = agent

    def preconditions(self):
        raise NotImplementedError()

    def apply_effects(self, **kwargs):
        raise NotImplementedError()
