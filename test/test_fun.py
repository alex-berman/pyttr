from ttrtypes import Fun, RecType, SingletonType, ListType, Ty, PType, Pred, BType


class TestFun(object):
    def test_validate_arg_for_rec_type_with_empty_value(self):
        Ind = BType('Ind')
        pick_up = Pred('pick_up', [Ind, Ind])
        fun = Fun('r',
             RecType({'agenda': SingletonType(ListType(Ty), [])}),
             'mock_body')
        valid_arg = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
        invalid_arg = RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})])}).create()
        assert fun.validate_arg(valid_arg)
        assert not fun.validate_arg(invalid_arg)

    def test_validate_arg_for_rec_type_with_non_empty_value(self):
        Ind = BType('Ind')
        pick_up = Pred('pick_up', [Ind, Ind])
        fun = Fun('r',
             RecType({'agenda': SingletonType(ListType(Ty), [RecType({'e': PType(pick_up, ['a', 'c'])})])}),
             'mock_body')
        valid_arg = RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})])}).create()
        invalid_arg = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
        assert fun.validate_arg(valid_arg)
        assert not fun.validate_arg(invalid_arg)
