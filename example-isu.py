from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
from actionrules import ActionRule, TypeJudgementAct, CreationAct
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
            {'e': PType(pick_up, ['a', 'c'])}
        ])})),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            {'e': PType(pick_up, ['a', 'c'])}
        ])}),
        Fun('e',
            RecType({'e': PType(pick_up, ['a', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                {'e': PType(attract_attention, ['a', 'b'])}
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            {'e': PType(attract_attention, ['a', 'b'])}
        ])}),
        Fun('e',
            RecType({'e': PType(attract_attention, ['a', 'b'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                {'e': PType(throw, ['a', 'c'])}
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            {'e': PType(run_after, ['b', 'c'])}
        ])}),
        Fun('e',
            RecType({'e': PType(run_after, ['b', 'c'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [
                {'e': PType(pick_up, ['b', 'c'])}
            ])}))),

    Fun('r',
        RecType({'agenda': SingletonType(ListType(Ty), [
            {'e': PType(return_pred, ['b', 'c', 'a'])}
        ])}),
        Fun('e',
            RecType({'e': PType(return_pred, ['b', 'c', 'a'])}),
            RecType({'agenda': SingletonType(ListType(Ty), [])}))),
}


event_creation = ActionRule(
    # Corresponds to Cooper (2023, p. 61), 54
    arguments=['current_state'],
	preconditions=lambda current_state: len(current_state.pathvalue('agenda')) > 0,
	effect=lambda current_state: CreationAct('current_event', RecType({'e': current_state.pathvalue('agenda')[0]['e']}))
)

event_based_update = ActionRule(
    # Corresponds to Cooper (2023, p. 61), 55a
    arguments=['f', 'current_state', 'current_event'],
    preconditions=lambda f, current_state, current_event:\
        current_event is not None and isinstance(f.body, Fun) and f.validate_arg(current_state) and \
        f.body.validate_arg(current_event),
    effect=lambda f, current_state, current_event: TypeJudgementAct(
        'next_state', f.app(current_state).app(current_event))
)

tacit_update = ActionRule(
    # Corresponds to Cooper (2023, p. 61), 55b
    arguments=['f', 'current_state'],
    preconditions=lambda f, current_state: isinstance(f.body, RecType) and f.validate_arg(current_state),
    effect=lambda f, current_state: TypeJudgementAct('next_state', f.app(current_state))
)

action_rules = {event_creation, event_based_update, tacit_update}


def get_next_state(current_state, update_functions, action_rules, current_event=None):
    # Assumptions:
    # - Action rules are tried in arbitrary order.
    # - There is either no current event or exactly one current event.
    # - If the preconditions for an action rule hold, the rule is applied, unless the rule creates a current event and
    #   a current event already exists.

    for update_function in update_functions:
        def get_args(action_rule):
            def get_arg(argument_name):
                if argument_name == 'f':
                    return update_function
                elif argument_name == 'current_state':
                    return current_state
                elif argument_name == 'current_event':
                    return current_event
            return [get_arg(argument_name) for argument_name in action_rule.arguments]

        for action_rule in action_rules:
            args = get_args(action_rule)
            if action_rule.preconditions(*args):
                print('preconditions hold for ' + show(action_rule) + ' with update function ' +
                      show(update_function))
                effect = action_rule.effect(*args)
                if isinstance(effect, TypeJudgementAct):
                    if effect.symbol == 'next_state':
                        return effect.judged_type.create()
                elif isinstance(effect, CreationAct):
                    if effect.symbol == 'current_event' and current_event is None:
                        print('creating current event of type ' + show(effect.type_to_create))
                        current_event = RecType({'e': effect.type_to_create.create()})
                        return get_next_state(current_state, update_functions, action_rules, current_event)
                else:
                    raise Exception("Don't know how to handle rule effect " + str(effect))

    raise Exception('Failed to get next state')


state = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
print('state', show(state))
for _ in range(10):
    state = get_next_state(state, update_functions, action_rules)
    print('state', show(state))
