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


# Game of fetch, corresponding to Cooper (2023, p.55)
pick_up = Pred('pick_up', [Ind, Ind])
attract_attention = Pred('attract_attention', [Ind, Ind])
throw = Pred('throw', [Ind, Ind])
run_after = Pred('run_after', [Ind, Ind])
return_pred = Pred('return', [Ind, Ind, Ind])

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

f3 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(attract_attention, ['a', 'b'])}
         ])}),
         Fun('e',
             RecType({'e': PType(attract_attention, ['a', 'b'])}),
             RecType({'agenda': SingletonType(ListType(Ty), [
                 {'e': PType(throw, ['a', 'c'])}
             ])})))

f4 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(run_after, ['b', 'c'])}
         ])}),
         Fun('e',
             RecType({'e': PType(run_after, ['b', 'c'])}),
             RecType({'agenda': SingletonType(ListType(Ty), [
                 {'e': PType(pick_up, ['b', 'c'])}
             ])})))

f5 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(return_pred, ['b', 'c', 'a'])}
         ])}),
         Fun('e',
             RecType({'e': PType(return_pred, ['b', 'c', 'a'])}),
             RecType({'agenda': SingletonType(ListType(Ty), [])})))

# Updated states with new functions
state_0 = RecType({'agenda': SingletonType(ListType(Ty), [])})  # Initial state
state_1 = f1.app(state_0)
state_2 = f2.app(state_1).app(RecType({'e': PType(pick_up, ['a', 'c'])}))
state_3 = f3.app(state_2).app(RecType({'e': PType(attract_attention, ['a', 'b'])}))
state_4 = f4.app(state_3).app(RecType({'e': PType(run_after, ['b', 'c'])}))
state_5 = f5.app(state_4).app(RecType({'e': PType(return_pred, ['b', 'c', 'a'])}))

# Printing states
print(show(state_1))
print(show(state_2))
print(show(state_3))
print(show(state_4))
print(show(state_5))


# TODO:
# - replace manual invocation of state transitions above with action rule(s)
