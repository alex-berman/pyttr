from ttrtypes import BType, PType, Pred, ListType, SingletonType, RecType, Ty, Re, Fun
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


# Game of fetch, corresponding to Cooper (2023, p.55) (only first function)
pick_up = Pred('pick_up', [Ind, Ind])
attract_attention = Pred('attract_attention', [Ind, Ind])
f1 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [])}),
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(pick_up, ['a', 'c'])}
         ])}))
f2 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(pick_up, ['a', 'c'])}
         ])}),
         Fun('e',
             RecType({'e': PType(pick_up, ['a', 'c'])}),
             RecType({'agenda': SingletonType(ListType(Ty), [
                 {'e': PType(attract_attention, ['a', 'b'])}
             ])})))
state_0 = RecType({'agenda': SingletonType(ListType(Ty), [])}) # Initial state
state_1 = f1.app(state_0) # State after applying f1
state_2 = f2.app(state_1).app(RecType({'e': PType(pick_up, ['a', 'c'])})) # State after applying f2 and pick-up event
print(show(state_1))
print(show(state_2))

# TODO:
# - add more states?
# - replace manual invocation of state transitions above with action rule(s)
