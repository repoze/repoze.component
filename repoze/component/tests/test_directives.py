import unittest

class TestAdapterDirective(unittest.TestCase):
    def _callFUT(self, context, structure):
        from repoze.component.directives import adapter
        return adapter(context, structure)

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
                     'factory':'factory',
                     'name':'name'}
        info = self._callFUT(context, structure)
        self.assertEqual(info['discriminator'],
                         ('adapter', ('requires',), 'provides', 'name') )
        callback = info['callback']
        self.assertEqual(callback['func'], context.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'factory', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})
                         
class TestUtilityDirective(unittest.TestCase):
    def _callFUT(self, context, structure):
        from repoze.component.directives import utility
        return utility(context, structure)

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

    def test_no_component(self):
        context = DummyContext()
        structure = {'provides':'abc'}
        self.assertRaises(ValueError, self._callFUT, context, structure)

    def test_ok(self):
        context = DummyContext()
        structure = {'provides':'provides',
                     'component':'component',
                     'factory':'factory',
                     'name':'name'}
        info = self._callFUT(context, structure)
        discriminator = info['discriminator']
        callback = info['callback']
        self.assertEqual(discriminator, ('utility', 'provides', 'name'))
        self.assertEqual(callback['func'], context.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'component'))
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

    
