from records import Rec
from ttrtypes import RecType, SingletonType, ListType, Ty, PType, Pred, BType
from utils import show


class TestRecords(object):
    def test_show(self):
        assert show(Rec({'a': {'b': 'c', 'd': 'e'}})) in [
            '{a = {b = c, d = e}}',
            '{a = {d = e, b = c}}']

    def test_query_with_empty_value(self):
        Ind = BType('Ind')
        pick_up = Pred('pick_up', [Ind, Ind])
        rec_type = RecType({'agenda': SingletonType(ListType(Ty), [])})
        valid_arg = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
        invalid_arg = RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})])}).create()
        assert rec_type.query(valid_arg)
        assert not rec_type.query(invalid_arg)

    def test_query_with_non_empty_value(self):
        Ind = BType('Ind')
        pick_up = Pred('pick_up', [Ind, Ind])
        rec_type = RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})])})
        valid_arg = RecType({'agenda': SingletonType(ListType(Ty), [
            RecType({'e': PType(pick_up, ['a', 'c'])})])}).create()
        invalid_arg = RecType({'agenda': SingletonType(ListType(Ty), [])}).create()
        assert rec_type.query(valid_arg)
        assert not rec_type.query(invalid_arg)
