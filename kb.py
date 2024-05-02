class KnowledgeBase(object):
    def __init__(self):
        self.objects = set()
        self.named_objects = dict()

    def add(self, obj, symbol=None):
        self.objects.add(obj)
        if symbol is not None:
            if symbol in self.named_objects:
                raise Exception('Object with symbol ' + repr(symbol) + ' already in knowledge base')
            self.named_objects[symbol] = obj

    def get(self, symbol, default=None):
        if symbol in self.named_objects:
            return self.named_objects[symbol]
        else:
            return default

    def __getattr__(self, name):
        if name in self.named_objects:
            return self.named_objects[name]
        return object.__getattribute__(self, name)

    def __iter__(self):
        return iter(self.objects)

    def has_symbol(self, symbol):
        return symbol in self.named_objects

    def remove(self, symbol):
        obj = self.named_objects[symbol]
        self.objects.remove(obj)
        del self.named_objects[symbol]
