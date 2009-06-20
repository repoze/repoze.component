import sys

from repoze.lru import lru_cache
from repoze.lru import LRUCache

from repoze.component.advice import addClassAdvisor

ALL = object()
_marker = object()
_notfound = object()
_missing = object()

class Subscribers:
    def __repr__(self):
        return '<subscriber>'
    __str__ = __repr__

_subscribers = Subscribers()

try:
    from itertools import product # 2.6+
except ImportError:
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

def augmented_product(args, default_list):
    direct = product(*args)
    # product out our directly supplied args
    for combo in direct:
        yield combo
    # defaults come after any directly supplied product combo
    if default_list:
        ldef = len(default_list[0])
        largs = len(args)
        enumerated = list(enumerate(default_list))
        rev_enumerated = reversed(enumerated)
        # we replace holes in the supplied with the default, e.g.
        # one, two, <default>
        # one, <default>, three
        # <default>, two, three
        for i in range(ldef):
            for num, defaults in rev_enumerated:
                default = defaults[i]
                newargs = list(args)
                newargs[num] = (default,)
                for combo in product(*newargs):
                    yield combo
        # we replace holes in the defaults with the supplied, e.g.
        # one, <default>, <default>
        # <default>, two, <default>
        # <default>, <default>, three
        for i in range(ldef):
            defaultargs = [ (default[i],) for default in default_list ]
            for j in range(largs):
                newargs = list(defaultargs)
                newargs[j] = args[j]
                for combo in tuple(product(*newargs)):
                    yield combo
        # we product out all the defaults at the end
        for combo in product(*default_list):
            yield combo

@lru_cache(1000)
def cached_augmented_product(args, default_list):
    return tuple(augmented_product(args, default_list))

class Registry(object):
    """ A component registry.  The component registry supports the
    Python mapping interface and can be used as you might a regular
    dictionary.  It also support more advanced registrations and
    lookups that include a ``requires`` argument and a ``name`` via
    its ``register`` and ``lookup`` methods.  It may be treated as an
    component registry by using its ``resolve`` method."""
    def __init__(self, dict=None, **kwargs):
        self.data = {}
        self._lkpcache = LRUCache(1000)
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)
        self.listener_registered = False # at least one listener registered

    @property
    def _dictmembers(self):
        D = {}
        norequires = self.data.get((), {})
        for k, v in norequires.items():
            provides, name = k
            if name == '':
                D[provides] = v
        return D

    def __cmp__(self, dict):
        if isinstance(dict, Registry):
            return cmp(self.data, dict.data)
        else:
            return cmp(self._dictmembers, dict)

    def __len__(self):
        return len(self._dictmembers)

    def __getitem__(self, key):
        notrequires = self.data.get((), {})
        return notrequires[(key, '')]

    def __setitem__(self, key, val):
        self.register(key, val)

    def __delitem__(self, key):
        self._lkpcache.clear()
        notrequires = self.data.get((), {})
        try:
            del notrequires[(key, '')]
        except KeyError:
            raise KeyError(key)

    def clear(self):
        self._lkpcache.clear()
        notrequires = self.data.get((), {})
        for k, v in notrequires.items():
            provides, name = k
            if name == '':
                del notrequires[k]

    def copy(self):
        import copy
        return copy.copy(self)

    def items(self):
        return self._dictmembers.items()

    def keys(self):
        return self._dictmembers.keys()
    
    def values(self):
        return self._dictmembers.values()

    def iteritems(self):
        return iter(self.items())
    
    def iterkeys(self):
        return iter(self.keys())
    
    def itervalues(self):
        return iter(self.values())

    def __contains__(self, key):
        return key in self._dictmembers

    has_key = __contains__

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def update(self, dict=None, **kw):
        if dict is not None:
            for k, v in dict.items():
                self.register(k, v)
        for k, v in kw.items():
            self.register(k, v)

    def setdefault(self, key, failobj=None):
        self._lkpcache.clear()
        val = self.get(key, default=failobj)
        if val is failobj:
            self[key] = failobj
        return self[key]

    def __iter__(self):
        return iter(self._dictmembers)

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError, "pop expected at most 2 arguments, got "\
                              + repr(1 + len(args))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise
        del self[key]
        return value

    def popitem(self):
        try:
            k, v = self.iteritems().next()
        except StopIteration:
            raise KeyError, 'container is empty'
        del self[k]
        return (k, v)

    def register(self, provides, component, *requires, **kw):
        """ Register a component """
        name = kw.get('name', '')
        if name is ALL:
            raise ValueError('ALL cannot be used in a registration as a name')
        self._lkpcache.clear()
        if provides is _subscribers:
            self.listener_registered = True
        info = self.data.setdefault(requires, {})
        info[(provides, name)] =  component
        all = info.setdefault((provides, ALL), [])
        all.append(component)

    def unregister(self, provides, component, *requires, **kw):
        self._lkpcache.clear()
        name = kw.get('name', '')
        if name is ALL:
            del self.data[requires]
            return
        info = self.data.get(requires, {})
        del info[(provides, name)]
        all = info.get((provides, ALL), [])
        all.remove(component)
        if not all:
            del self.data[requires]

    def subscribe(self, fn, *requires, **kw):
        name = kw.get('name', '')
        if name is ALL:
            raise ValueError('ALL may not be used as a name to subscribe')
        newkw = {'name':name, 'default':_marker}
        subscribers = self.lookup(_subscribers, *requires, **newkw)
        if subscribers is _marker:
            subscribers = []
        subscribers.append(fn)
        self.register(_subscribers, subscribers, *requires, **kw)

    def unsubscribe(self, fn, *requires, **kw):
        name = kw.get('name', '')
        if name is ALL:
            raise ValueError('ALL may not be used as a name to unsubscribe')
        newkw = {'name':name, 'default':_marker}
        subscribers = self.lookup(_subscribers, *requires, **newkw)
        if subscribers is _marker:
            subscribers = []
        if fn in subscribers:
            subscribers.remove(fn)

    def notify(self, *objects, **kw):
        if not self.listener_registered:
            return # optimization
        subscribers = self.resolve(_subscribers, *objects, **kw)
        name = kw.get('name', '')
        if subscribers is not None:
            if name is ALL:
                for subscriberlist in subscribers:
                    for subscriber in subscriberlist:
                        subscriber(*objects)
            else:
                for subscriber in subscribers:
                    subscriber(*objects)

    def _lookup(self, provides, name, default, requires, default_requires):
        # the requires and default_requires arguments *must* be
        # hashable sequences of tuples composed of hashable objects
        reg = self.data

        cachekey = (provides, requires, name, default_requires)
        cached = self._lkpcache.get(cachekey, _marker)

        if cached is _marker:
            combinations = cached_augmented_product(requires, default_requires)
            regkey = (provides, name)
            for combo in combinations:
                try:
                    result = reg[combo][regkey]
                    self._lkpcache.put(cachekey, result)
                    return result
                except KeyError:
                    pass

            self._lkpcache.put(cachekey, _notfound)
            cached = _notfound
            
        if cached is _notfound:
            if default is _missing:
                raise LookupError(
                    "Couldn't find a component providing %s for requires "
                    "args %r with name `%s`" % (provides, list(requires), name))
            return default

        return cached

    def lookup(self, provides, *requires, **kw):
        req = []
        for val in requires:
            if not hasattr(val, '__iter__'):
                req.append((val,))
            else:
                req.append(tuple(val))
        name = kw.get('name', '')
        extras = ((None,),) * len(req)
        default = kw.get('default', _missing)
        return self._lookup(provides, name, default, tuple(req), extras)

    def resolve(self, provides, *objects, **kw):
        requires = tuple([directlyprovidedby(obj) for obj in objects])
        extras = tuple([alsoprovidedby(obj) for obj in objects])
        name = kw.get('name', '')
        default = kw.get('default', _missing)
        return self._lookup(provides, name, default, requires, extras)

def directlyprovidedby(obj):
    try:
        return obj.__component_types__
    except AttributeError:
        return ()

def alsoprovidedby(obj):
    try:
        return (obj.__class__, None)
    except AttributeError:
        # probably an oldstyle class
        return (type(obj), None)

def providedby(obj):
    """ Return a sequence of component types provided by obj ordered
    most specific to least specific.  """
    return directlyprovidedby(obj) + alsoprovidedby(obj)

def provides(*types):
    """ Decorate an object with one or more types.

    May be used as a function to decorate an instance:

    provides(ob, 'type1', 'type2')

    .. or as a class decorator (Python 2.6+):

    @provides('type1', type2')
    class Foo:
        pass

    .. or inside a class definition:

    class Foo(object):
        provides('type1', 'type2')
    """
    frame = sys._getframe(1)
    locals = frame.f_locals
    if (locals is frame.f_globals) or ('__module__' not in locals):
        # not called from within a class definition
        # (as a class decorator or to decorate an instance)
        if not types:
            raise TypeError('provides must be called with an object')
        ob, types = types[0], types[1:]
        _add_types(ob, *types)
        return ob
    else:
        # called from within a class definition
        if '__implements_advice_data__' in locals:
            raise TypeError(
                "provides can be used only once within a class definition.")
        locals['__implements_advice_data__'] = types
        addClassAdvisor(_classprovides_advice, depth=2)

def _add_types(obj, *types):
    alreadyprovides = directlyprovidedby(obj)
    alreadyprovides = tuple([ x for x in alreadyprovides if x not in types ])
    obj.__component_types__ = types + alreadyprovides

def _classprovides_advice(cls):
    types = cls.__dict__['__implements_advice_data__']
    del cls.__implements_advice_data__
    _add_types(cls, *types)
    return cls

