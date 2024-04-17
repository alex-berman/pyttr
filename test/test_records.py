from records import Rec
from utils import show


class TestRecords(object):
    def test_show(self):
        assert show(Rec({'a': {'b': 'c', 'd': 'e'}})) in [
            '{a = {b = c, d = e}}',
            '{a = {d = e, b = c}}']
