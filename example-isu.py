from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from records import Rec
from actionrules import ActionRule, CreationAct, ConsumeAct
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

kb = KnowledgeBase()
for f in update_functions:
    kb.add(f)
kb.add(RecType({'agenda': SingletonType(ListType(Ty), [])}).create(), 'current_state')


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54
    def preconditions(self):
        if not kb.has_symbol('current_event') and len(self.kb.current_state.agenda) > 0:
            return {}

    def effects(self):
        return [CreationAct('current_event', RecType({'e': self.kb.current_state.agenda[0].pathvalue('e')}))]


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        if self.kb.has_symbol('current_event'):
            for obj in kb:
                if isinstance(obj, Fun) and isinstance(obj.body, Fun) and obj.validate_arg(self.kb.current_state) \
                        and obj.body.validate_arg(self.kb.current_event):
                    return {'f': obj}

    def effects(self, f):
        return [
            CreationAct('current_state', f.app(self.kb.current_state).app(self.kb.current_event)),
            ConsumeAct('current_event')
        ]


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for obj in kb:
            if isinstance(obj, Fun) and isinstance(obj.body, RecType) and obj.validate_arg(self.kb.current_state):
                return {'f': obj}

    def effects(self, f):
        return [CreationAct('current_state', f.app(self.kb.current_state))]


action_rules = {EventCreation, EventBasedUpdate, TacitUpdate}


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
                    obj = effect.type_to_create.create()
                    if kb.has_symbol(effect.symbol):
                        kb.remove(effect.symbol)
                    kb.add(obj, effect.symbol)
                elif isinstance(effect, ConsumeAct):
                    kb.remove(effect.symbol)
                else:
                    raise Exception("Don't know how to handle rule effect " + str(effect))
            return
    raise Exception('Failed to get next state with current_state=' + show(kb.current_state) +
                    ', current_event=' + show(kb.get('current_event', None)))


def show_kb():
    print('-' * 50)
    for symbol, obj in kb.named_objects.items():
        print(symbol + '=' + show(obj))


show_kb()
for _ in range(20):
    update_kb()
    show_kb()
