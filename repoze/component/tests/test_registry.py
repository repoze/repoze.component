import unittest

class TestRegistry(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.component import Registry
        return Registry
        
    def _makeOne(self, dict=None, **kw):
        return self._getTargetClass()(dict, **kw)

    def test_ctor(self):
        d = {'a':1}
        registry = self._makeOne(d, b=2)
        self.assertEqual(registry['a'], 1)
        self.assertEqual(registry['b'], 2)

    def test_cmp_againstreg(self):
        registry1 = self._makeOne()
        registry2 = self._makeOne()
        self.assertEqual(registry1.__cmp__(registry2), 0)
        self.assertEqual(registry2.__cmp__(registry1), 0)
        registry1['a'] = 1
        self.assertEqual(registry1.__cmp__(registry2), 1)
        self.assertEqual(registry2.__cmp__(registry1), -1)

    def test_len(self):
        d = {'a':1}
        registry = self._makeOne(d, b=2)
        self.assertEqual(len(registry), 2)

    def test_getitem(self):
        d = {'a':1}
        registry = self._makeOne(d)
        self.assertEqual(registry['a'], 1)
        
    def test_setitem(self):
        d = {'a':1}
        registry = self._makeOne(d)
        registry['a'] = 2
        self.assertEqual(registry['a'], 2)
        
    def test_delitem(self):
        d = {'a':1}
        registry = self._makeOne(d)
        del registry['a']
        self.assertEqual(registry.get('a'), None)
        
    def test_delitem_raises(self):
        registry = self._makeOne()
        self.assertRaises(KeyError, registry.__delitem__, 'b')

    def test_clear(self):
        d = {'a':1}
        registry = self._makeOne(d)
        registry.clear()
        self.assertEqual(len(registry), 0)

    def test_copy(self):
        d = {'a':1}
        registry = self._makeOne(d)
        registry2 = registry.copy()
        self.assertEqual(registry, registry2)

    def test_items(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.items()), [('a', 1), ('b', 2)])
        
    def test_keys(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.keys()), ['a', 'b'])
        
    def test_values(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.values()), [1, 2])

    def test_iteritems(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.iteritems()), [('a', 1), ('b', 2)])
        
    def test_iterkeys(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.iterkeys()), ['a', 'b'])
        
    def test_itervalues(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(sorted(registry.itervalues()), [1, 2])

    def test_contains(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.failUnless('a' in registry)
        
    def test_has_key(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.failUnless(registry.has_key('a'))

    def test_get(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertEqual(registry.get('a'), 1)

    def test_fromkeys(self):
        d = {'a':1, 'b':2}
        klass = self._getTargetClass()
        registry = klass.fromkeys(['a', 'b'], 2)
        self.assertEqual(registry['a'], 2)
        self.assertEqual(registry['b'], 2)

    def test_update(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        registry.update({'a':2, 'c':3})
        self.assertEqual(registry['a'], 2)
        self.assertEqual(registry['c'], 3)

    def test_updatekw(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        registry.update(None, a=2, c=3)
        self.assertEqual(registry['a'], 2)
        self.assertEqual(registry['c'], 3)

    def test_setdefault(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        val = registry.setdefault('c', 1)
        self.assertEqual(val, 1)
        self.assertEqual(registry['c'], 1)
        val = registry.setdefault('a', 2)
        self.assertEqual(val, 1)
        self.assertEqual(registry['a'], 1)
        self.assertEqual(registry['b'], 2)
        self.assertEqual(registry['c'], 1)

    def test_iter(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        iterator = iter(registry)
        self.assertEqual(sorted(list(iterator)), ['a', 'b'])

    def test_pop_toomanyargs(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertRaises(TypeError, registry.pop, 'a', 1, 2)

    def test_pop_default_missing(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        val = registry.pop('c', 1)
        self.assertEqual(val, 1)
        
    def test_pop_nodefault_missing(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        self.assertRaises(KeyError, registry.pop, 'c')

    def test_pop_succeds(self):
        d = {'a':1, 'b':2}
        registry = self._makeOne(d)
        val = registry.pop('a')
        self.assertEqual(val, 1)
        self.failIf('a' in registry)

    def test_popitem_empty(self):
        registry = self._makeOne()
        self.assertRaises(KeyError, registry.popitem)
        
    def test_popitem_ok(self):
        d = {'a':1}
        registry = self._makeOne(d)
        val = registry.popitem()
        self.assertEqual(val, ('a', 1))
        self.failIf('a' in registry)

    def test_register(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        registry._lkpcache = DummyLRUCache()
        registry.register('provides', 'component', 'a', 'b', 'c', name='foo')
        registered = registry.data[('a', 'b', 'c')]
        self.assertEqual(registered[('provides', 'foo')], 'component')
        self.assertEqual(registered[('provides', ALL)], ['component'])
        registry.register('provides', 'component2', 'a', 'b', 'c', name='bar')
        self.assertEqual(registered[('provides', 'bar')], 'component2')
        self.assertEqual(registered[('provides', ALL)],
                         ['component', 'component2'])
        self.assertEqual(registry._lkpcache.cleared, True)

    def test_register_all_name_fails(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        try:
            registry.register('provides',
                              'component', 'a', 'b', 'c', name=ALL)
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_unregister(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        registry._lkpcache = DummyLRUCache()
        registry.data[('a', 'b', 'c')] = {
            ('provides', 'foo'):'component',
            ('provides', 'bar'):'component2',
            ('provides', ALL):['component', 'component2'],
            }
        registry.unregister('provides', 'component', 'a', 'b', 'c', name='foo')
        self.assertEqual(registry._lkpcache.cleared, True)
        registered = registry.data[('a', 'b', 'c')]
        self.assertEqual(registered,
                         {('provides', 'bar'): 'component2',
                          ('provides', ALL): ['component2'],
                          }
                         )
        registry.unregister('provides', 'component2', 'a', 'b', 'c', name='bar')
        self.failIf(('a', 'b', 'c') in registry.data)

    def test_unregister_all(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        registry._lkpcache = DummyLRUCache()
        registry.data[('a', 'b', 'c')] = {
            ('provides', 'foo'):'component',
            ('provides', ALL):['component', 'component2'],
            }
        registry.unregister('provides', 'component', 'a', 'b', 'c', name=ALL)
        self.failIf(('a', 'b', 'c') in registry.data)
        self.assertEqual(registry._lkpcache.cleared, True)

    def test_subscribe(self):
        from repoze.component.registry import _subscribers
        def subscriber(what):
            pass
        registry = self._makeOne()
        registry.subscribe(subscriber, 'a', 'b', 'c', name='foo')
        result = registry.lookup(_subscribers, 'a', 'b', 'c', name='foo')
        self.assertEqual(result, [subscriber])

    def test_subscribe_all(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        try:
            registry.subscribe('subscriber', 'a', 'b', 'c', name=ALL)
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_unsubscribe(self):
        from repoze.component.registry import _subscribers
        def subscriber(what):
            pass
        registry = self._makeOne()
        registry.register(_subscribers, [subscriber], 'a', 'b', 'c', name='foo')
        result = registry.lookup(_subscribers, 'a', 'b', 'c', name='foo')
        self.assertEqual(result, [subscriber])
        registry.unsubscribe(subscriber, 'a', 'b', 'c', name='foo')
        result = registry.lookup(_subscribers, 'a', 'b', 'c', name='foo')
        self.assertEqual(result, [])

    def test_unsubscribe_all(self):
        from repoze.component.registry import ALL
        registry = self._makeOne()
        try:
            registry.unsubscribe('subscriber', 'a', 'b', 'c', name=ALL)
        except ValueError:
            pass
        else:
            raise AssertionError

    def test_unsubscribe_not_subscribed(self):
        def subscriber(what):
            pass
        registry = self._makeOne()
        registry.unsubscribe(subscriber, 'a', 'b', 'c', name='foo')
        # doesnt blow up
        
    def test_notify_noname(self):
        from repoze.component.registry import _subscribers
        def subscriber(what):
            what.called = True
        def subscriber2(what):
            what.called_again = True
        class What:
            __component_types__ = ('abc',)
        what = What()
        registry = self._makeOne()
        registry.register(_subscribers, [subscriber, subscriber2], 'abc')
        registry.notify(what)
        self.assertEqual(what.called, True)
        self.assertEqual(what.called_again, True)

    def test_notify_withname(self):
        from repoze.component.registry import _subscribers
        def subscriber(what):
            what.called = True
        def subscriber2(what):
            what.called_again = True
        class What:
            __component_types__ = ('abc',)
        what = What()
        registry = self._makeOne()
        registry.register(_subscribers, [subscriber, subscriber2], 'abc',
                          name='yup')
        registry.notify(what, name='yup')
        self.assertEqual(what.called, True)
        self.assertEqual(what.called_again, True)

    def test_notify_nolisteners(self):
        class What:
            __component_types__ = ('abc',)
        what = What()
        registry = self._makeOne()
        registry.notify(what)
        # doesn't blow up

    def test_notify_all(self):
        from repoze.component.registry import ALL
        from repoze.component.registry import _subscribers
        def subscriber(what):
            what.called += 1
        class What:
            def __init__(self):
                self.called = 0
            __component_types__ = ('abc',)
        what = What()
        registry = self._makeOne()
        registry.register(_subscribers, [subscriber, subscriber], 'abc',
                          name='yup')
        registry.register(_subscribers, [subscriber, subscriber], 'abc')
        registry.notify(what, name=ALL)
        self.assertEqual(what.called, 4)

    def test_lookup_default(self):
        registry = self._makeOne()
        result = registry.lookup('a', default=registry)
        self.assertEqual(result, registry)
        
    def test_lookup_nodefault(self):
        registry = self._makeOne()
        self.assertRaises(LookupError, registry.lookup, 'a')

    def test_lookup_named(self):
        registry = self._makeOne()
        registry.register('test', 'registered', 'abc', name='yup')
        result = registry.lookup('test', 'abc', name='yup')
        self.assertEqual(result, 'registered')

    def test_resolve_default(self):
        registry = self._makeOne()
        result = registry.resolve('a', default=registry)
        self.assertEqual(result, registry)
        
    def test_resolve_nodefault(self):
        registry = self._makeOne()
        self.assertRaises(LookupError, registry.resolve, 'a')

    def test_resolve_named(self):
        registry = self._makeOne()
        registry.register('test', 'registered', 'abc', name='yup')
        class ABC:
            __component_types__ = ('abc',)
        abc = ABC()
        result = registry.resolve('test', abc, name='yup')
        self.assertEqual(result, 'registered')


class TestRegistryFunctional(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.component import Registry
        return Registry
        
    def _makeOne(self, dict=None):
        return self._getTargetClass()(dict)

    def _makeRegistry(self, dict=None):
        registry = self._makeOne(dict)

        registry.register('bladerunner', 'deckardvalue' , None, 'deckard')
        registry.register('friend', 'luckmanvalue', 'luckman', name='name')
        registry.register('fight', 'barrisluckmanvalue', 'barris', 'luckman')

        return registry

    def test_as_mapping(self):
        d = {'a':1, 'b':2, 'c':3, 'd':4}
        registry = self._makeRegistry(d)
        self.failUnless(registry == d) # __cmp__
        self.assertEqual(len(registry), 4) # __len__
        self.assertEqual(registry['a'], 1)
        self.assertEqual(registry['b'], 2)
        registry['e'] = 4
        self.assertEqual(len(registry), 5) # __len__
        self.assertEqual(registry['e'], 4)
        del registry['e']
        self.assertEqual(len(registry), 4) # __len__
        self.assertRaises(KeyError, registry.__getitem__, 'e')
        copy = registry.copy()
        self.failUnless(copy == registry)
        self.assertEqual(sorted(registry.items()),
                         [('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(sorted(registry.keys()), ['a', 'b', 'c', 'd'])
        self.assertEqual(sorted(registry.values()), [1, 2, 3, 4])
        self.assertEqual(sorted(registry.iteritems()),
                         [('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(sorted(registry.iterkeys()), ['a', 'b', 'c', 'd'])
        self.assertEqual(sorted(registry.itervalues()), [1, 2, 3, 4])
        self.failUnless('a' in registry)
        self.failIf('z' in registry)
        self.failUnless(registry.has_key('a'))
        self.failIf(registry.has_key('z'))
        self.assertEqual(registry.get('a'), 1)
        self.assertEqual(registry.get('z', 0), 0)
        self.assertEqual(registry.get('z'), None)
        self.assertEqual(registry.fromkeys({'a':1}), {'a':None})
        registry.update({'e':5})
        self.assertEqual(len(registry), 5)
        self.assertEqual(registry['e'], 5)
        f = registry.setdefault('f', {})
        f['1'] = 1
        self.assertEqual(registry['f'], f)
        L = []
        for k in registry:
            L.append(k)
        self.assertEqual(sorted(L), ['a', 'b', 'c', 'd', 'e', 'f'])
        val = registry.pop('a')
        self.assertEqual(val, 1)
        self.assertEqual(len(registry), 5)
        item = registry.popitem()
        self.assertEqual(len(registry), 4)
        registry.clear()
        self.assertEqual(len(registry), 0)

    def test_register_and_lookup(self):
        registry = self._makeRegistry()
        look = registry.lookup
        eq = self.assertEqual

        eq(look('bladerunner', None, 'deckard'), 'deckardvalue')
        eq(look('bladerunner', None, ['inherits', 'deckard']), 'deckardvalue')
        eq(look('friend', 'luckman', name='name'), 'luckmanvalue')
        eq(look('fight', 'barris', 'luckman'), 'barrisluckmanvalue')
        eq(look('fight', ('inherits', 'barris'), 'luckman'),
           'barrisluckmanvalue')
        eq(look('fight', ('deckard', 'barris'), 'luckman'),
           'barrisluckmanvalue')
        eq(look('bladerunner', (None,), ('deckard', 'barris')), 'deckardvalue')
        eq(look('friend', 'luckman', default=None), None)
        eq(look('bladerunner', 'deckard', ('luckman',), default=None), None)
        eq(look('bladerunner', None, None, default=None), None)
        eq(look('bladerunner', 'barris', 'deckard'), 'deckardvalue')
        eq(look('bladerunner', 'luckman', 'deckard'), 'deckardvalue')

        registry.register('default', 'a', None, None)
        eq(look('default', None, None), 'a')

    def test_register_and_lookup_all(self):
        from repoze.component.registry import ALL
        registry = self._makeRegistry()
        look = registry.lookup
        eq = self.assertEqual
        result = registry.lookup('bladerunner', None, 'deckard', name=ALL)
        self.assertEqual(result, ['deckardvalue'])
        registry.register('bladerunner', 'deckardvalue2' , None, 'deckard',
                          name='another')
        result = registry.lookup('bladerunner', None, 'deckard', name=ALL)
        self.assertEqual(result, ['deckardvalue', 'deckardvalue2'])

    def test_register_and_resolve_classes(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual

        eq(resolve('bladerunner', None, Deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, InheritsDeckard), 'deckardvalue')
        eq(resolve('friend', Luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', Barris, Luckman), 'barrisluckmanvalue')
        eq(resolve('fight', InheritsBarris, Luckman), 'barrisluckmanvalue')
        eq(resolve('fight', DeckardBarris, Luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, DeckardBarris), 'deckardvalue')
        eq(resolve('friend', Luckman, default=None), None)
        eq(resolve('bladerunner', Deckard, Luckman, default=None), None)
        eq(resolve('bladerunner', Luckman, Deckard), 'deckardvalue')
        eq(resolve('bladerunner', Barris, Deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)
                            
    def test_register_and_resolve_instances(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual

        deckard = Deckard(None)
        inheritsdeckard = InheritsDeckard(None)
        luckman = Luckman(None)
        barris = Barris(None)
        inheritsbarris = InheritsBarris(None)
        deckardbarris = DeckardBarris(None, None)

        eq(resolve('bladerunner', None, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, inheritsdeckard), 'deckardvalue')
        eq(resolve('friend', luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', barris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', inheritsbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', deckardbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, deckardbarris), 'deckardvalue')
        eq(resolve('friend', luckman, default=None), None)
        eq(resolve('bladerunner', deckard, luckman, default=None), None)
        eq(resolve('bladerunner', luckman, deckard), 'deckardvalue')
        eq(resolve('bladerunner', barris, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)

    def test_register_and_resolve_instances_withdict(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual

        deckard = Deckard(None)
        provides(deckard, 'deckard')
        inheritsdeckard = InheritsDeckard(None)
        provides(inheritsdeckard, 'inherits')
        luckman = Luckman(None)
        provides(luckman, 'luckman')
        barris = Barris(None)
        provides(barris, 'barris')
        inheritsbarris = InheritsBarris(None)
        provides(inheritsbarris, 'inherits')
        deckardbarris = DeckardBarris(None, None)
        provides(deckardbarris, 'deckard', 'barris')

        eq(resolve('bladerunner', None, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, inheritsdeckard), 'deckardvalue')
        eq(resolve('friend', luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', barris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', inheritsbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', deckardbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, deckardbarris), 'deckardvalue')
        eq(resolve('friend', luckman, default=None), None)
        eq(resolve('bladerunner', deckard, luckman, default=None), None)
        eq(resolve('bladerunner', luckman, deckard), 'deckardvalue')
        eq(resolve('bladerunner', barris, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)

    def test_register_and_resolve_oldstyle_classes(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual
        
        eq(resolve('bladerunner', None, OSDeckard), 'deckardvalue')
        eq(resolve('bladerunner', None, InheritsDeckard), 'deckardvalue')
        eq(resolve('friend', Luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', Barris, Luckman), 'barrisluckmanvalue')
        eq(resolve('fight', InheritsBarris, Luckman), 'barrisluckmanvalue')
        eq(resolve('fight', DeckardBarris, Luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, DeckardBarris), 'deckardvalue')
        eq(resolve('friend', Luckman, default=None), None)
        eq(resolve('bladerunner', Deckard, Luckman, default=None), None)
        eq(resolve('bladerunner', Luckman, Deckard), 'deckardvalue')
        eq(resolve('bladerunner', Barris, Deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)

    def test_register_and_resolve_oldstyle_instances(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual
        
        deckard = OSDeckard(None)
        inheritsdeckard = OSInheritsDeckard(None)
        luckman = OSLuckman(None)
        barris = OSBarris(None)
        inheritsbarris = OSInheritsBarris(None)
        deckardbarris = OSDeckardBarris(None, None)

        eq(resolve('bladerunner', None, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, inheritsdeckard), 'deckardvalue')
        eq(resolve('friend', luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', barris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', inheritsbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', deckardbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, deckardbarris), 'deckardvalue')
        eq(resolve('friend', luckman, default=None), None)
        eq(resolve('bladerunner', deckard, luckman, default=None), None)
        eq(resolve('bladerunner', luckman, deckard), 'deckardvalue')
        eq(resolve('bladerunner', barris, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)

    def test_register_and_resolve_oldstyle_instances_withdict(self):
        registry = self._makeRegistry()
        resolve = registry.resolve
        eq = self.assertEqual
        from repoze.component import provides

        deckard = OSDeckard(None)
        provides(deckard, 'deckard')

        inheritsdeckard = OSInheritsDeckard(None)
        provides(inheritsdeckard, 'inhherits')

        luckman = OSLuckman(None)
        provides(luckman, 'luckman')

        barris = OSBarris(None)
        provides(barris, 'barris')

        inheritsbarris = OSInheritsBarris(None)
        provides(inheritsbarris, 'inherits')

        deckardbarris = OSDeckardBarris(None, None)
        provides(deckardbarris, 'deckard', 'barris')

        eq(resolve('bladerunner', None, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, inheritsdeckard), 'deckardvalue')
        eq(resolve('friend', luckman, name='name'), 'luckmanvalue')
        eq(resolve('fight', barris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', inheritsbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('fight', deckardbarris, luckman), 'barrisluckmanvalue')
        eq(resolve('bladerunner', None, deckardbarris), 'deckardvalue')
        eq(resolve('friend', luckman, default=None), None)
        eq(resolve('bladerunner', deckard, luckman, default=None), None)
        eq(resolve('bladerunner', luckman, deckard), 'deckardvalue')
        eq(resolve('bladerunner', barris, deckard), 'deckardvalue')
        eq(resolve('bladerunner', None, None, default=None), None)

    def test_register_and_resolve_all(self):
        from repoze.component.registry import ALL
        from repoze.component import provides

        deckard = OSDeckard(None)
        provides(deckard, 'deckard')

        registry = self._makeRegistry()
        eq = self.assertEqual
        result = registry.resolve('bladerunner', None, deckard, name=ALL)
        self.assertEqual(result, ['deckardvalue'])
        registry.register('bladerunner', 'deckardvalue2' , None, 'deckard',
                          name='another')
        result = registry.resolve('bladerunner', None, deckard, name=ALL)
        self.assertEqual(result, ['deckardvalue', 'deckardvalue2'])

    def test_register_Nones(self):
        from repoze.component import provides
        class Two(object):
            provides('two')

        class One(Two):
            provides('one')

        class B(object):
            provides('b')

        class A(B):
            provides('a')

        instance1 = One()
        provides(instance1, 'i')

        instance2 = A()
        provides(instance2, 'i')

        registry = self._makeOne()
        registry.register('foo', 'somevalue', None, None)

        result = registry.resolve('foo', instance1, instance2)
        self.assertEqual(result, 'somevalue')

    def test_lookup_2nd_time_returns_same(self):
        registry = self._makeOne()
        registry.register('foo', 'somevalue', 'a', 'b')
        result = registry.lookup('foo', 'a', 'b')
        self.assertEqual(result, 'somevalue')

        # this should come out of the lookup cache
        result = registry.lookup('foo', 'a', 'b')
        self.assertEqual(result, 'somevalue')

class TestSubscribers(unittest.TestCase):
    def _makeOne(self):
        from repoze.component.registry import Subscribers
        return Subscribers()

    def test_repr(self):
        inst = self._makeOne()
        self.assertEqual(repr(inst), '<subscriber>')

    def test_str(self):
        inst = self._makeOne()
        self.assertEqual(str(inst), '<subscriber>')

class TestProvidedBy(unittest.TestCase):
    def _callFUT(self, obj):
        from repoze.component import providedby
        return providedby(obj)

    def test_newstyle_class_with_provides(self):
        from repoze.component import provides
        class Foo(object):
            provides('a', 'b')
        result = self._callFUT(Foo)
        self.assertEqual(list(result), ['a', 'b', type(Foo), None])

    def test_newstyle_class_without_provides(self):
        class Foo(object):
            pass
        result = self._callFUT(Foo)
        self.assertEqual(list(result), [type(Foo), None])

    def test_oldstyle_class_with_provides(self):
        from repoze.component import provides
        class Foo:
            provides('a', 'b')
        result = self._callFUT(Foo)
        self.assertEqual(list(result), ['a', 'b', type(Foo), None])

    def test_oldstyle_class_without_provides(self):
        class Foo:
            pass
        result = self._callFUT(Foo)
        self.assertEqual(list(result), [type(Foo), None])

    def test_oldstyle_instance_withprovides(self):
        from repoze.component import provides
        class Foo:
            provides('a', 'b')
        foo = Foo()
        result = self._callFUT(foo)
        self.assertEqual(list(result), ['a', 'b', Foo, None])

    def test_oldstyle_instance_withoutprovides(self):
        class Foo:
            pass
        foo = Foo()
        result = self._callFUT(foo)
        self.assertEqual(list(result), [Foo, None])

    def test_newstyle_instance_withprovides(self):
        from repoze.component import provides
        class Foo(object):
            provides('a', 'b')
        foo = Foo()
        result = self._callFUT(foo)
        self.assertEqual(list(result), ['a', 'b', Foo, None])

    def test_newstyle_instance_withoutprovides(self):
        class Foo(object):
            pass
        foo = Foo()
        result = self._callFUT(foo)
        self.assertEqual(list(result), [Foo, None])

    def test_string(self):
        result = self._callFUT('foo')
        self.assertEqual(list(result), [str, None])

    def test_int(self):
        result = self._callFUT(1)
        self.assertEqual(list(result), [int, None])

    def test_bool(self):
        result = self._callFUT(True)
        self.assertEqual(list(result), [bool, None])

    def test_None(self):
        result = self._callFUT(None)
        self.assertEqual(list(result), [type(None), None])

class TestDirectlyProvidedBy(unittest.TestCase):
    def _callFUT(self, obj):
        from repoze.component import directlyprovidedby
        return directlyprovidedby(obj)

    def test_it_withtypes(self):
        class Dummy:
            pass
        inst = Dummy()
        inst.__component_types__ = ('123', '456')
        self.assertEqual(self._callFUT(inst), ('123', '456'))

    def test_it_notypes(self):
        class Dummy:
            pass
        inst = Dummy()
        self.assertEqual(self._callFUT(inst), ())
    

class TestProvidesAsFunction(unittest.TestCase):
    def _callFUT(self, obj, *types):
        from repoze.component import provides
        provides(obj, *types)

    def test_multiple_calls(self):
        class Foo(object):
            pass
        foo = Foo()
        self._callFUT(foo, 'abc', 'def')
        self._callFUT(foo, 'ghi')
        self.assertEqual(foo.__component_types__, ('ghi', 'abc', 'def'))

    def test_provide_no_types(self):
        from repoze.component import provides
        self.assertRaises(TypeError, provides)

class TestProvidesInsideClass(unittest.TestCase):
    def test_class_inheritance(self):
        from repoze.component import provides
        class Foo(object):
            provides('abc', 'def')
        class Foo2(Foo):
            provides('ghi')
        self.assertEqual(Foo2.__component_types__, ('ghi', 'abc', 'def'))

    def test_morethanonce(self):
        from repoze.component import provides
        class Foo(object):
            provides('abc', 'def')
            try:
                provides('ghi')
            except TypeError:
                pass
            else:
                raise AssertionError('wrong')
        
class TestAugmentedProduct(unittest.TestCase):
    def _callFUT(self, arg, default_list):
        from repoze.component.registry import augmented_product
        return augmented_product(arg, default_list)
    
    def test_withdefaults(self):
        expected = [(1, 4, 7),
                    (1, 4, 8),
                    (1, 4, 9),
                    (1, 5, 7),
                    (1, 5, 8),
                    (1, 5, 9),
                    (1, 6, 7),
                    (1, 6, 8),
                    (1, 6, 9),
                    (2, 4, 7),
                    (2, 4, 8),
                    (2, 4, 9),
                    (2, 5, 7),
                    (2, 5, 8),
                    (2, 5, 9),
                    (2, 6, 7),
                    (2, 6, 8),
                    (2, 6, 9),
                    (3, 4, 7),
                    (3, 4, 8),
                    (3, 4, 9),
                    (3, 5, 7),
                    (3, 5, 8),
                    (3, 5, 9),
                    (3, 6, 7),
                    (3, 6, 8),
                    (3, 6, 9),
                    (1, 4, 'class3'),
                    (1, 5, 'class3'),
                    (1, 6, 'class3'),
                    (2, 4, 'class3'),
                    (2, 5, 'class3'),
                    (2, 6, 'class3'),
                    (3, 4, 'class3'),
                    (3, 5, 'class3'),
                    (3, 6, 'class3'),
                    (1, 'class2', 7),
                    (1, 'class2', 8),
                    (1, 'class2', 9),
                    (2, 'class2', 7),
                    (2, 'class2', 8),
                    (2, 'class2', 9),
                    (3, 'class2', 7),
                    (3, 'class2', 8),
                    (3, 'class2', 9),
                    ('class1', 4, 7),
                    ('class1', 4, 8),
                    ('class1', 4, 9),
                    ('class1', 5, 7),
                    ('class1', 5, 8),
                    ('class1', 5, 9),
                    ('class1', 6, 7),
                    ('class1', 6, 8),
                    ('class1', 6, 9),
                    (1, 'class2', 'class3'),
                    (2, 'class2', 'class3'),
                    (3, 'class2', 'class3'),
                    ('class1', 4, 'class3'),
                    ('class1', 5, 'class3'),
                    ('class1', 6, 'class3'),
                    ('class1', 'class2', 7),
                    ('class1', 'class2', 8),
                    ('class1', 'class2', 9),
                    (1, None, None),
                    (2, None, None),
                    (3, None, None),
                    (None, 4, None),
                    (None, 5, None),
                    (None, 6, None),
                    (None, None, 7),
                    (None, None, 8),
                    (None, None, 9),
                    ('class1', 'class2', 'class3'),
                    ('class1', 'class2', None),
                    ('class1', None, 'class3'),
                    ('class1', None, None),
                    (None, 'class2', 'class3'),
                    (None, 'class2', None),
                    (None, None, 'class3'),
                    (None, None, None)]
        
        a = (1,2,3)
        b = (4,5,6)
        c = (7,8,9)
        defaults = (('class1', None), ('class2', None), ('class3', None))
        result = list(self._callFUT((a, b, c), defaults))
        self.assertEqual(result, expected)

    def test_nodefaults(self):
        expected = [(1, 4, 7),
                    (1, 4, 8),
                    (1, 4, 9),
                    (1, 5, 7),
                    (1, 5, 8),
                    (1, 5, 9),
                    (1, 6, 7),
                    (1, 6, 8),
                    (1, 6, 9),
                    (2, 4, 7),
                    (2, 4, 8),
                    (2, 4, 9),
                    (2, 5, 7),
                    (2, 5, 8),
                    (2, 5, 9),
                    (2, 6, 7),
                    (2, 6, 8),
                    (2, 6, 9),
                    (3, 4, 7),
                    (3, 4, 8),
                    (3, 4, 9),
                    (3, 5, 7),
                    (3, 5, 8),
                    (3, 5, 9),
                    (3, 6, 7),
                    (3, 6, 8),
                    (3, 6, 9),
                    ]
        a = (1,2,3)
        b = (4,5,6)
        c = (7,8,9)
        result = list(self._callFUT((a, b, c), None))
        self.assertEqual(result, expected)

from repoze.component import provides

class Deckard(object):
    provides('deckard')
    def __init__(self, context):
        self.context = context

class Luckman(object):
    provides('luckman')
    def __init__(self, context):
        self.context = context

class Barris(object):
    provides('barris')
    def __init__(self, context):
        self.context = context

class DeckardBarris(object):
    provides('deckard', 'barris')
    def __init__(self, context1, context2):
        self.context1 = context1 
        self.context2 = context2
   
class InheritsDeckard(Deckard):
    provides('inherits')
    def __init__(self, context):
        self.context = context
    
class InheritsBarris(Barris):
    provides('inherits')
    def __init__(self, context):
        self.context = context
    
class OSDeckard:
    provides('deckard')
    def __init__(self, context):
        self.context = context

class OSLuckman:
    provides('luckman')
    def __init__(self, context):
        self.context = context

class OSBarris:
    provides('barris')
    def __init__(self, context):
        self.context = context

class OSDeckardBarris:
    provides('deckard', 'barris')
    def __init__(self, context1, context2):
        self.context1 = context1 
        self.context2 = context2
    
class OSInheritsDeckard(OSDeckard):
    provides('inherits')
    def __init__(self, context):
        self.context = context
    
class OSInheritsBarris(OSBarris):
    provides('inherits')
    def __init__(self, context):
        self.context = context
    
class DummyLRUCache(dict):
    def clear(self):
        self.cleared = True
        dict.clear(self)
        
