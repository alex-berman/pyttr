from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from records import Rec
from actionrules import ActionRule, SpecificTypeJudgementAct, CreationAct
from utils import show


Ind = BType('Ind')
run = Pred('run', [Ind])
T1 = RecType({'agenda': SingletonType(ListType(Ty), [RecType({'e': PType(run, ['j'])})]),
              'latest_move': SingletonType(ListType(Re), [])})
T2 = RecType({'agenda': SingletonType(ListType(Ty), []),
              'latest_move': RecType({'e': PType(run, ['j'])})})
print(
    show(
        T1.amerge(T2)
        )
        )


# Game of fetch, corresponding to Cooper (2023, p.55)
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


frame = Rec({
    'current_state': RecType({'agenda': SingletonType(ListType(Ty), [])}).create(),
    'current_event': RecType({'e': Ty}).create()
})


class EventCreation(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 54
    def preconditions(self):
        if len(frame.current_state.agenda) > 0:
            return {}

    def effect(self):
        return CreationAct('current_event', RecType({'e': frame.current_state.agenda[0].pathvalue('e')}))


class EventBasedUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55a
    def preconditions(self):
        for f in update_functions:
            if isinstance(f.body, Fun) and f.validate_arg(frame.current_state) \
                    and f.body.validate_arg(frame.current_event):
                return {'f': f}

    def effect(self, f):
        return SpecificTypeJudgementAct('next_state', f.app(self.frame.current_state).app(self.frame.current_event))


class TacitUpdate(ActionRule):
    # Corresponds to Cooper (2023, p. 61), 55b
    def preconditions(self):
        for f in update_functions:
            if isinstance(f.body, RecType) and f.validate_arg(self.frame.current_state):
                return {'f': f}

    def effect(self, f):
        return SpecificTypeJudgementAct('next_state', f.app(self.frame.current_state))


action_rules = {EventCreation, EventBasedUpdate, TacitUpdate}


def update_frame():
    # Assumptions:
    # - Action rules are tried in arbitrary order.
    # - There is either no current event or exactly one current event.
    # - If the preconditions for an action rule hold, the rule is applied, unless the rule creates a current event and
    #   a current event already exists.

    for action_rule in action_rules:
        bindings = action_rule(frame).preconditions()
        if bindings is not None:
            print('preconditions hold for ' + action_rule.__name__ + ' with bindings ' + str(
                {key: show(value) for key, value in bindings.items()}))
            effect = action_rule(frame).effect(**bindings)
            if isinstance(effect, SpecificTypeJudgementAct) and effect.symbol == 'next_state':
                next_state = effect.judged_type.create()
                return Rec({
                    'current_state': next_state,
                    'current_event': RecType({'e': Ty}).create()
                })
            elif isinstance(effect, CreationAct) and effect.symbol == 'current_event':
                if RecType({'e': Ty}).query(frame.current_event):
                    print('creating current event of type ' + show(effect.type_to_create))
                    current_event = effect.type_to_create.create()
                    return Rec({
                        'current_state': frame.current_state,
                        'current_event': current_event
                    })
            else:
                raise Exception("Don't know how to handle rule effect " + str(effect))
    raise Exception('Failed to get next state with current_state=' + show(frame.current_state) +
                    ', current_event=' + show(frame.current_event))


print('state', show(frame.current_state))
for _ in range(20):
    frame = update_frame()
    print('state', show(frame.current_state))
