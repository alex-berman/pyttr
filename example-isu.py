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
f1 = Fun('r',
         RecType({'agenda': SingletonType(ListType(Ty), [])}),
         RecType({'agenda': SingletonType(ListType(Ty), [
             {'e': PType(pick_up, ['a', 'c'])}
         ])}))
state_0 = RecType({'agenda': SingletonType(ListType(Ty), [])})
print(show(f1.app(state_0)))
