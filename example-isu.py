from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from actionrules import ActionRule
from utils import show


# Game of fetch, corresponding to Cooper (2023, p.55)
Ind = BType('Ind')
pick_up = Pred('pick_up', [Ind, Ind])
attract_attention = Pred('attract_attention', [Ind, Ind])
throw = Pred('throw', [Ind, Ind])
run_after = Pred('run_after', [Ind, Ind])
return_pred = Pred('return', [Ind, Ind, Ind])

update_functions = {
    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [])}),
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})
        ])})),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})
        ])}),
        Fun('e',
            RecType({'e': PType(pick_up, ['a', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(attract_attention, ['a', 'b'])})
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(attract_attention, ['a', 'b'])})
        ])}),
        Fun('e',
            RecType({'e': PType(attract_attention, ['a', 'b'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(throw, ['a', 'c'])})
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(throw, ['a', 'c'])})
        ])}),
        Fun('e',
            RecType({'e': PType(throw, ['a', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(run_after, ['b', 'c'])})
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(run_after, ['b', 'c'])})
        ])}),
        Fun('e',
            RecType({'e': PType(run_after, ['b', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, ['b', 'c'])})
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['b', 'c'])})
        ])}),
        Fun('e',
            RecType({'e': PType(pick_up, ['b', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(return_pred, ['b', 'c', 'a'])})
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(return_pred, ['b', 'c', 'a'])})
        ])}),
        Fun('e',
            RecType({'e': PType(return_pred, ['b', 'c', 'a'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [])}))),
}


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54
    def preconditions(self):
        if self.agent.current_event is None and len(self.agent.current_state.agenda) > 0:
            return {}

    def apply_effects(self):
        create_event_in_world(RecType({'e': self.agent.current_state.agenda[0].pathvalue('e')}))


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        if self.agent.current_event is not None:
            for f in self.agent.update_functions:
                if isinstance(f.body, Fun) and f.validate_arg(self.agent.current_state) \
                        and f.body.validate_arg(self.agent.current_event):
                    return {'f': f}

    def apply_effects(self, f):
        self.agent.current_state = f.app(self.agent.current_state).app(self.agent.current_event).create()
        self.agent.current_event = None


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for f in self.agent.update_functions:
            if isinstance(f.body, RecType) and f.validate_arg(self.agent.current_state):
                return {'f': f}

    def apply_effects(self, f):
        self.agent.current_state = f.app(self.agent.current_state).create()


action_rules = {EventCreation, EventBasedUpdate, TacitUpdate}


class Agent:
    def __init__(self, update_functions, action_rules, initial_state):
        self.update_functions = update_functions
        self.action_rules = action_rules
        self.current_state = initial_state
        self.current_event = None

    def update_state(self):
        for action_rule in self.action_rules:
            bindings = action_rule(self).preconditions()
            if bindings is not None:
                print('preconditions hold for ' + action_rule.__name__ + ' with bindings ' + str(
                    {key: show(value) for key, value in bindings.items()}))
                action_rule(self).apply_effects(**bindings)
                return
        raise Exception('Failed to get next state')


def create_event_in_world(ty):
    # We here assume that when a event is created in the world, the agent immediately perceives it
    agent.current_event = ty.create()


def print_agent_internals():
    print('state: ' + show(agent.current_state))
    print('current_event: ' + show(agent.current_event))
    print()


initial_state = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
agent = Agent(update_functions, action_rules, initial_state)
print_agent_internals()
for _ in range(20):
    agent.update_state()
    print_agent_internals()
