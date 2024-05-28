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
infostate_type_empty = RecType({'agenda': SingletonType(ListType(Ty), [])})


def update_functions(r):
    infostate_type_pick_up_human = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(pick_up, [r.h, r.s])})
    ])})
    infostate_type_attract_attention = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(attract_attention, [r.h, r.d])})
    ])})
    infostate_type_throw = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(throw, [r.h, r.s])})
    ])})
    infostate_type_run_after = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(run_after, [r.d, r.s])})
    ])})
    infostate_type_pick_up_dog = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(pick_up, [r.d, r.s])})
    ])})
    infostate_type_return = RecType({'agenda': SingletonType(ListType(Ty), [
        RecType({'e': PType(return_pred, [r.d, r.s, r.h])})
    ])})

    return {
        Fun('r',
            infostate_type_empty,
            infostate_type_pick_up_human),

        Fun('r',
            infostate_type_pick_up_human,
            Fun('e',
                RecType({'e': PType(pick_up, [r.h, r.s])}),
                infostate_type_attract_attention)),

        Fun('r',
            infostate_type_attract_attention,
            Fun('e',
                RecType({'e': PType(attract_attention, [r.h, r.d])}),
                infostate_type_throw)),

        Fun('r',
            infostate_type_throw,
            Fun('e',
                RecType({'e': PType(throw, [r.h, r.s])}),
                infostate_type_run_after)),

        Fun('r',
            infostate_type_run_after,
            Fun('e',
                RecType({'e': PType(run_after, [r.d, r.s])}),
                infostate_type_pick_up_dog)),

        Fun('r',
            infostate_type_pick_up_dog,
            Fun('e',
                RecType({'e': PType(pick_up, [r.d, r.s])}),
                infostate_type_return)),

        Fun('r',
            infostate_type_return,
            Fun('e',
                RecType({'e': PType(return_pred, [r.d, r.s, r.h])}),
                infostate_type_empty)),
    }


class InformationStateTimeStep(object):
    def __init__(self, ty, i):
        # An information-state timestep contains a type (of information state) and an uninstantiated witness of that
        # type. The witness is represented by a timestep-specific string serving as a logical variable.
        self.ty = ty
        self.uninstantiated_witness = 'uninstantiated_witness_' + str(i)
        ty.judge(self.uninstantiated_witness)


class InformationStateHistory(list):
    def __str__(self):
        # Only show the latest state (if any)
        if len(self) == 0:
            return []
        elif len(self) == 1:
            return '[T=' + show(self[0].ty) + ']'
        else:
            return '[..., T=' + show(self[-1].ty) + ']'


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54, but with the difference that the creation act uses the information state
    # type rather than the state as such. (s_{i,A} : T   T=[agenda:...] ~ : T.agenda.fst!)
    def preconditions(self):
        if self.agent.current_perceived_object is None:
            agenda = self.agent.state[-1].ty.pathvalue('agenda').comps.obj
            if len(agenda) > 0:
                return {'agenda': agenda}

    def apply_effects(self, agenda):
        self.agent.perform_type_act(CreateAct(agenda[0]))


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        if self.agent.current_perceived_object is not None:
            for f in self.agent.update_functions:
                if isinstance(f.body, Fun) and f.validate_arg(self.agent.state[-1].uninstantiated_witness) \
                        and f.body.validate_arg(self.agent.current_perceived_object):
                    return {'f': f}

    def apply_effects(self, f):
        self.agent.state.append(
            InformationStateTimeStep(
                f.app(self.agent.state[-1].uninstantiated_witness).app(self.agent.current_perceived_object),
                len(self.agent.state)))


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for f in self.agent.update_functions:
            if isinstance(f.body, RecType) and f.validate_arg(self.agent.state[-1].uninstantiated_witness):
                return {'f': f}

    def apply_effects(self, f):
        self.agent.state.append(
            InformationStateTimeStep(
                f.app(self.agent.state[-1].uninstantiated_witness),
                len(self.agent.state)))


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
            self.apply_rules(obj)
        self.apply_rules(None)

    def apply_rules(self, current_perceived_object):
        self.current_perceived_object = current_perceived_object
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

    def perform_type_act(self, type_act):
        self.pending_actions.insert(0, type_act)

    def get_pending_actions(self):
        result = [ty for ty in self.pending_actions]
        self.pending_actions = []
        return result


roles = Rec({
    'h': 'h1',
    'd': 'd1',
    's': 's1'
})


def initial_agent_state():
    return InformationStateHistory([InformationStateTimeStep(infostate_type_empty, 0)])


agents = [Agent(update_functions(roles), action_rules, initial_agent_state()) for _ in range(2)]


def handle_action(action):
    if isinstance(action, CreateAct):
        create_object_in_world(action.ty)


def create_object_in_world(ty):
    # We assume that any object (e.g. event) can be created at any time, regardless of the state of the world. We also
    # assume that when an object is created in the world, all agents immediately perceive it.
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
