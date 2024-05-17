from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from records import Rec
from actionrules import ActionRule
from utils import show


# Game of fetch, corresponding to Cooper (2023, p.60)
Ind = BType('Ind')
pick_up = Pred('pick_up', [Ind, Ind])
attract_attention = Pred('attract_attention', [Ind, Ind])
throw = Pred('throw', [Ind, Ind])
run_after = Pred('run_after', [Ind, Ind])
return_pred = Pred('return', [Ind, Ind, Ind])


def update_functions(r):
    return {
        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, [r.h, r.s])})
            ])})),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, [r.h, r.s])})
            ])}),
            Fun('e',
                RecType({'e': PType(pick_up, [r.h, r.s])}),
                RecType({'agenda': SingletonType(ListType(Ty), [
                    RecType({'e': PType(attract_attention, [r.h, r.d])})
                ])}))),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(attract_attention, [r.h, r.d])})
            ])}),
            Fun('e',
                RecType({'e': PType(attract_attention, [r.h, r.d])}),
                RecType({'agenda': SingletonType(ListType(Ty), [
                    RecType({'e': PType(throw, [r.h, r.s])})
                ])}))),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(throw, [r.h, r.s])})
            ])}),
            Fun('e',
                RecType({'e': PType(throw, [r.h, r.s])}),
                RecType({'agenda': SingletonType(ListType(Ty), [
                    RecType({'e': PType(run_after, [r.d, r.s])})
                ])}))),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(run_after, [r.d, r.s])})
            ])}),
            Fun('e',
                RecType({'e': PType(run_after, [r.d, r.s])}),
                RecType({'agenda': SingletonType(ListType(Ty), [
                    RecType({'e': PType(pick_up, [r.d, r.s])})
                ])}))),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, [r.d, r.s])})
            ])}),
            Fun('e',
                RecType({'e': PType(pick_up, [r.d, r.s])}),
                RecType({'agenda': SingletonType(ListType(Ty), [
                    RecType({'e': PType(return_pred, [r.d, r.s, r.h])})
                ])}))),

        Fun('r',
            RecType({'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(return_pred, [r.d, r.s, r.h])})
            ])}),
            Fun('e',
                RecType({'e': PType(return_pred, [r.d, r.s, r.h])}),
                RecType({'agenda': SingletonType(ListType(Ty), [])}))),
    }


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54
    def preconditions(self):
        if self.agent.current_event is None and len(self.agent.states[-1].agenda) > 0:
            return {}

    def apply_effects(self):
        create_event_in_world(RecType({'e': self.agent.states[-1].agenda[0].pathvalue('e')}))


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        if self.agent.current_event is not None:
            for f in self.agent.update_functions:
                if isinstance(f.body, Fun) and f.validate_arg(self.agent.states[-1]) \
                        and f.body.validate_arg(self.agent.current_event):
                    return {'f': f}

    def apply_effects(self, f):
        self.agent.states.append(f.app(self.agent.states[-1]).app(self.agent.current_event).create())
        self.agent.current_event = None


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for f in self.agent.update_functions:
            if isinstance(f.body, RecType) and f.validate_arg(self.agent.states[-1]):
                return {'f': f}

    def apply_effects(self, f):
        self.agent.states.append(f.app(self.agent.states[-1]).create())


action_rules = {EventCreation, EventBasedUpdate, TacitUpdate}


class Agent:
    def __init__(self, update_functions, action_rules, initial_state):
        self.update_functions = update_functions
        self.action_rules = action_rules
        self.states = [initial_state]
        self.current_event = None

    def update_state(self):
        for action_rule in self.action_rules:
            bindings = action_rule(self).preconditions()
            if bindings is not None:
                # print('preconditions hold for ' + action_rule.__name__ + ' with bindings ' + str(
                #     {key: show(value) for key, value in bindings.items()}))
                action_rule(self).apply_effects(**bindings)
                return
        raise Exception('Failed to get next state')


r = Rec({
    # A record containing individuals in the roles of human, dog and stick
    'h': 'h1',
    'd': 'd1',
    's': 's1'
})
initial_state = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
agents = [Agent(update_functions(r), action_rules, initial_state) for _ in range(2)]


def create_event_in_world(ty):
    # We here assume that when a event is created in the world, all agents immediately perceive it.
    event = ty.create()
    for agent in agents:
        agent.current_event = event


def print_agent_internals():
    for n, agent in enumerate(agents):
        print('agent ' + str(n) + ':')
        print('  current state: ' + show(agent.states[-1]))
        print('  current event: ' + show(agent.current_event))
        print()
    print('-' * 70)


def main():
    print_agent_internals()
    for _ in range(20):
        for agent in agents:
            agent.update_state()
        print_agent_internals()


main()
