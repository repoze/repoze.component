import unittest

class TestComponentDirective(unittest.TestCase):
    def _callFUT(self, declaration):
        from repoze.component.directives import component
        return component(declaration)

    def test_bad_structure(self):
        declaration = DummyDeclaration(badstructure=True)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_bad_diffnames(self):
        declaration = DummyDeclaration(diff=True)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_no_provides(self):
        declaration = DummyDeclaration()
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_no_requires(self):
        structure = {'provides':'abc'}
        declaration = DummyDeclaration(structure=structure)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_no_factory(self):
        structure = {'provides':'abc', 'requires':'a'}
        declaration = DummyDeclaration(structure=structure)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_ok(self):
        structure = {'provides':'provides',
                     'requires':['requires'],
                     'object':'object',
                     'name':'name'}
        declaration = DummyDeclaration(structure=structure)
        self._callFUT(declaration)
        actions = declaration.actions
        self.assertEqual(len(actions), 1)
        callback, discriminator, override = actions[0]
        self.assertEqual(discriminator,
                         ('component', ('requires',), 'provides', 'name') )
        self.assertEqual(callback['func'], declaration.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'object', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})
        self.assertEqual(override, False)

    def test_ok_norequires(self):
        structure = {'provides':'provides',
                     'object':'object',
                     'name':'name'}
        declaration = DummyDeclaration(structure=structure)
        self._callFUT(declaration)
        actions = declaration.actions
        self.assertEqual(len(actions), 1)
        callback, discriminator, override = actions[0]
        self.assertEqual(discriminator,
                         ('component', (), 'provides', 'name') )
        self.assertEqual(callback['func'], declaration.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'object'))
        self.assertEqual(callback['kw'], {'name':'name'})
        self.assertEqual(override, False)

    def test_with_override(self):
        structure = {'provides':'provides',
                     'object':'object',
                     'name':'name',
                     'override':True}
        declaration = DummyDeclaration(structure=structure)
        self._callFUT(declaration)
        actions = declaration.actions
        self.assertEqual(len(actions), 1)
        callback, discriminator, override = actions[0]
        self.assertEqual(discriminator,
                         ('component', (), 'provides', 'name') )
        self.assertEqual(callback['func'], declaration.registry.register)
        self.assertEqual(callback['arg'], ('provides', 'object'))
        self.assertEqual(callback['kw'], {'name':'name'})
        self.assertEqual(override, True)

class TestSubscriberDirective(unittest.TestCase):
    def _callFUT(self, declaration):
        from repoze.component.directives import subscriber
        return subscriber(declaration)

    def test_bad_structure(self):
        declaration = DummyDeclaration(badstructure=True)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_bad_diffnames(self):
        declaration = DummyDeclaration(diff=True)
        self.assertRaises(ValueError, self._callFUT, declaration)

    def test_ok(self):
        from repoze.component.registry import _subscribers
        structure = {'requires':['requires'],
                     'object':'object',
                     'name':'name'}
        declaration = DummyDeclaration(structure=structure)
        self._callFUT(declaration)
        actions = declaration.actions
        self.assertEqual(len(actions), 1)
        callback, discriminator, override = actions[0]
        self.assertEqual(discriminator,
                         ('component', ('requires',), _subscribers, 'name') )
        self.assertEqual(callback['func'], declaration.registry.register)
        self.assertEqual(callback['arg'], (_subscribers, 'object', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})
        self.assertEqual(override, False)

    def test_with_override(self):
        from repoze.component.registry import _subscribers
        structure = {'requires':['requires'],
                     'object':'object',
                     'name':'name',
                     'override':True}
        declaration = DummyDeclaration(structure=structure)
        self._callFUT(declaration)
        actions = declaration.actions
        self.assertEqual(len(actions), 1)
        callback, discriminator, override = actions[0]
        self.assertEqual(discriminator,
                         ('component', ('requires',), _subscribers, 'name') )
        self.assertEqual(callback['func'], declaration.registry.register)
        self.assertEqual(callback['arg'], (_subscribers, 'object', 'requires'))
        self.assertEqual(callback['kw'], {'name':'name'})
        self.assertEqual(override, True)
                         
class DummyRegistry:
    def register(self):
        pass

class DummyDeclaration:
    def __init__(self, **kw):
        self.registry = DummyRegistry()
        self.actions = []
        self.diff = kw.get('diff', False)
        self.badstructure = kw.get('badstructure', False)
        self.structure = kw.get('structure', {})

    def resolve(self, name):
        return name

    def string(self, name, default=None):
        return self.getvalue(name, default)

    def boolean(self, name, default=None):
        return bool(self.getvalue(name, default))

    def getvalue(self, name, default=None, typ=None):
        return self.structure.get(name)

    def expect(self, typ, names=()):
        if self.diff:
            raise ValueError
        if self.badstructure:
            raise ValueError

    def call_later(self, func, *arg, **kw):
        return {'func':func, 'arg':arg, 'kw':kw}

    def error(self, msg):
        raise ValueError(msg)

    def action(self, callback, discriminator=None, override=False):
        self.actions.append((callback, discriminator, override))

    
