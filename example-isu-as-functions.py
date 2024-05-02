from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Fun
from utils import show


Ind = BType('Ind')
run = Pred('run', [Ind])


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


def event_creation(current_state):
    # Corresponds to Cooper (2023, p. 61), 54
    if len(current_state.pathvalue('agenda')) > 0:
        type_of_event_to_create = RecType({'e': current_state.pathvalue('agenda')[0].pathvalue('e')})
        print('creating event of type ' + show(type_of_event_to_create))
        return type_of_event_to_create.create()


def event_based_update(f, current_state, current_event):
    # Corresponds to Cooper (2023, p. 61), 55a
    if isinstance(f.body, Fun) and f.validate_arg(current_state) and f.body.validate_arg(current_event):
        print('applying event-based update for function ' + show(f))
        return f.app(current_state).app(current_event).create()


def tacit_update(f, current_state):
    # Corresponds to Cooper (2023, p. 61), 55b
    if isinstance(f.body, RecType) and f.validate_arg(current_state):
        print('applying tacit update for function ' + show(f))
        return f.app(current_state).create()


def get_next_state(current_state, current_event=None):
    for f in update_functions:
        next_state = tacit_update(f, current_state)
        if next_state is not None:
            return next_state
        next_state = event_based_update(f, current_state, current_event)
        if next_state is not None:
            return next_state
    if current_event is None:
        current_event = event_creation(current_state)
        if current_event is not None:
            return get_next_state(current_state, current_event)
    raise Exception('Failed to get next state')


state = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
print('state', show(state))
for _ in range(10):
    state = get_next_state(state)
    print('state', show(state))
