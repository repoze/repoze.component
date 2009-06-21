import unittest

class TestComponentDirective(unittest.TestCase):
    def _callFUT(self, context, structure):
        from repoze.component.directives import component
        return component(context, structure)

    def test_bad_structure(self):
        context = DummyContext()
        structure = 'abc'
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_bad_diffnames(self):
        context = DummyContext(['a'])
        structure = {}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_no_provides(self):
        context = DummyContext()
        structure = {}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_no_requires(self):
        context = DummyContext()
        structure = {'provides':'abc'}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_no_factory(self):
        context = DummyContext()
        structure = {'provides':'abc', 'requires':'a'}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_ok(self):
        context = DummyContext()
        structure = {'provides':'provides',
                     'requires':['requires'],
                     'object':'object',
                     'name':'name'}
        info = self._callFUT(context, structure)[0]
        self.assertEqual(info['discriminator'],
                         ('component', ('requires',), 'provides', 'name') )
        callback = info['callback']
        self.assertEqual(callback['func'], context.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'object', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})

    def test_ok_norequires(self):
        context = DummyContext()
        structure = {'provides':'provides',
                     'object':'object',
                     'name':'name'}
        info = self._callFUT(context, structure)[0]
        self.assertEqual(info['discriminator'],
                         ('component', (), 'provides', 'name') )
        callback = info['callback']
        self.assertEqual(callback['func'], context.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'object'))
        self.assertEqual(callback['kw'], {'name':'name'})

class TestSubscriberDirective(unittest.TestCase):
    def _callFUT(self, context, structure):
        from repoze.component.directives import subscriber
        return subscriber(context, structure)

    def test_bad_structure(self):
        context = DummyContext()
        structure = 'abc'
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_bad_diffnames(self):
        context = DummyContext(['a'])
        structure = {}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_ok(self):
        from repoze.component.registry import _subscribers
        context = DummyContext()
        structure = {'requires':['requires'],
                     'object':'object',
                     'name':'name'}
        info = self._callFUT(context, structure)[0]
        self.assertEqual(info['discriminator'],
                         ('component', ('requires',), _subscribers, 'name') )
        callback = info['callback']
        self.assertEqual(callback['func'], context.registry.register)
        self.assertEqual(callback['arg'], (_subscribers, 'object', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})
                         
class DummyRegistry:
    def register(self):
        pass

class DummyContext:
    def __init__(self, diff=None):
        self.registry = DummyRegistry()
        if diff is None:
            diff = []
        self.diff = diff

    def resolve(self, name):
        return name

    def getvalue(self, structure, name, type=None):
        return structure.get(name)

    def diffnames(self, s1, s2):
        return self.diff

    def call_later(self, func, *arg, **kw):
        return {'func':func, 'arg':arg, 'kw':kw}

    
