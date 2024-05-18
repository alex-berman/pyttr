from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Fun
from records import Rec
from actionrules import ActionRule
from typeacts import CreateAct
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
        if self.agent.current_perceived_object is None and len(self.agent.state[-1].agenda) > 0:
            return {}

    def apply_effects(self):
        self.agent.pending_actions.insert(0, CreateAct(self.agent.state[-1].agenda[0]))


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        if self.agent.current_perceived_object is not None:
            for f in self.agent.update_functions:
                if isinstance(f.body, Fun) and f.validate_arg(self.agent.state[-1]) \
                        and f.body.validate_arg(self.agent.current_perceived_object):
                    return {'f': f}

    def apply_effects(self, f):
        self.agent.state.append(f.app(self.agent.state[-1]).app(self.agent.current_perceived_object).create())


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for f in self.agent.update_functions:
            if isinstance(f.body, RecType) and f.validate_arg(self.agent.state[-1]):
                return {'f': f}

    def apply_effects(self, f):
        self.agent.state.append(f.app(self.agent.state[-1]).create())


action_rules = {EventCreation, EventBasedUpdate, TacitUpdate}


class Agent:
    # Generic class for an agent performing any activity characterized by update functions, action rules and an
    # initial state.
    def __init__(self, update_functions, action_rules, initial_state):
        self.update_functions = update_functions
        self.action_rules = action_rules
        self.state = initial_state
        self.pending_perceptions = []
        self.pending_actions = []
        self.current_perceived_object = None

    def update_state(self):
        for obj in self.pending_perceptions:
            self.pending_perceptions.pop()
            self.current_perceived_object = obj
            self.apply_rules()
        self.current_perceived_object = None
        self.apply_rules()

    def apply_rules(self):
        print('  current perceived object: ' + show(self.current_perceived_object))
        for action_rule in self.action_rules:
            bindings = action_rule(self).preconditions()
            if bindings is not None:
                action_rule(self).apply_effects(**bindings)
                print('  applying ' + action_rule.__name__)
                print_agent_internals(self)
                return

    def perceive(self, obj):
        self.pending_perceptions.append(obj)

    def get_pending_actions(self):
        result = [ty for ty in self.pending_actions]
        self.pending_actions = []
        return result


class InformationStateHistory(list):
    def __str__(self):
        # Only show the latest state (if any)
        if len(self) == 0:
            return []
        elif len(self) == 1:
            return '[' + show(self[0]) + ']'
        else:
            return '[..., ' + show(self[-1]) + ']'


r = Rec({
    # A record containing individuals in the roles of human, dog and stick
    'h': 'h1',
    'd': 'd1',
    's': 's1'
})


def initial_state():
    return InformationStateHistory([
        RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
    ])


agents = [Agent(update_functions(r), action_rules, initial_state()) for _ in range(2)]


def handle_action(action):
    if isinstance(action, CreateAct):
        create_event_in_world(action.ty)


def create_event_in_world(ty):
    # We assume that any event can be created at any time, regardless of the state of the world. We also assume that
    # when a event is created in the world, all agents immediately perceive it.
    event = ty.create()
    for agent in agents:
        agent.perceive(event)


def print_agent_internals(agent):
    print('  state: ' + str(agent.state))
    print('  pending_actions: [' + ', '.join([str(action) for action in agent.pending_actions]) + ']')


def main():
    for t in range(20):
        for n, agent in enumerate(agents):
            print('agent ' + str(n) + ':')
            if t == 0:
                print_agent_internals(agent)
            agent.update_state()
            for action in agent.get_pending_actions():
                handle_action(action)
        print('-' * 70)


main()
