from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from actionrules import ActionRule, CreationAct, SpecificTypeJudgementAct
from kb import KnowledgeBase
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
        RecType({
            'agenda': SingletonType(ListType(Ty), []),
            'current_events': SingletonType(ListType(Ty), [])
        }),
        RecType({
            'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, ['a', 'c'])})
            ]),
            'current_events': SingletonType(ListType(Ty), [])
        })),

    Fun('r',
        RecType({
            'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, ['a', 'c'])})
            ]),
            'current_events': SingletonType(ListType(Ty), [
                RecType({'e': PType(pick_up, ['a', 'c'])})
            ])
        }),
        RecType({
            'agenda': SingletonType(ListType(Ty), [
                RecType({'e': PType(attract_attention, ['a', 'b'])})
            ]),
            'current_events': SingletonType(ListType(Ty), [])
        })),

    # TODO: change below as above
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

kb = KnowledgeBase()
for f in update_functions:
    kb.add(f)

s0_type = RecType({
    'agenda': SingletonType(ListType(Ty), []),
    'current_events': SingletonType(ListType(Ty), []),
})
kb.add(s0_type.create(), 's_0')


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54
    def preconditions(self):
        s_symbols = [symbol for symbol in self.kb.get_symbols() if symbol[0:2] == 's_']
        if len(s_symbols) > 0:
            current_t = max([int(symbol[2:]) for symbol in s_symbols])
            current_state_symbol = 's_' + str(current_t)
            current_state = self.kb.get(current_state_symbol)
            if len(current_state.agenda) > 0:
                return {'current_state': current_state}

    def effects(self, current_state):
        return [CreationAct(RecType({'e': current_state.agenda[0].pathvalue('e')}))]


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        s_symbols = [symbol for symbol in self.kb.get_symbols() if symbol[0:2] == 's_']
        if len(s_symbols) > 0:
            current_t = max([int(symbol[2:]) for symbol in s_symbols])
            current_state_symbol = 's_' + str(current_t)
            current_state = self.kb.get(current_state_symbol)
            for obj in kb:
                if isinstance(obj, Fun) and isinstance(obj.body, RecType) and obj.validate_arg(current_state):
                    return {
                        'f': obj,
                        'current_state': current_state,
                        'current_t': current_t}

    def effects(self, f, current_state, current_t):
        next_t = current_t + 1
        return [SpecificTypeJudgementAct('s_' + str(next_t), f.app(current_state))]


action_rules = {EventCreation, TacitUpdate}


def update_kb():
    # Assumptions:
    # - Action rules are tried in arbitrary order.
    # - There is either no current event or exactly one current event.
    # - If the preconditions for an action rule hold, the rule is applied, unless the rule creates a current event and
    #   a current event already exists.

    for action_rule in action_rules:
        bindings = action_rule(kb).preconditions()
        if bindings is not None:
            print('preconditions hold for ' + action_rule.__name__ + ' with bindings ' + str(
                {key: show(value) for key, value in bindings.items()}))
            effects = action_rule(kb).effects(**bindings)
            for effect in effects:
                if isinstance(effect, CreationAct):
                    perceive(effect.type_to_create)
                else:
                    raise Exception("Don't know how to handle rule effect " + str(effect))
            return
    raise Exception('Failed to get next state')


def perceive(ty):
    # Perceive something as being of type ty
    if isinstance(ty, RecType):
        e = ty.pathvalue('e')
        if e:
            add_to_current_events(ty)


def show_kb():
    print('-' * 50)
    for symbol, obj in kb.named_objects.items():
        print(symbol + '=' + show(obj))


show_kb()
for _ in range(20):
    update_kb()
    show_kb()
