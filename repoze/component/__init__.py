from repoze.lru import lru_cache

import inspect
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

@lru_cache(1000)
def cached_product(*args, **kwds):
    return tuple(product(*args, **kwds))
    
_marker = object()

class Registry(object):
    """ A component registry.  The component registry supports the
    Python mapping interface and can be used as you might a regular
    dictionary.  It also support more advanced registrations and
    lookups that include a ``requires`` argument and a ``name`` via
    its ``register`` and ``lookup`` methods.  It may be treated as an
    adapter registry by using its ``resolve`` and ``adapt`` methods."""
    def __init__(self, dict=None, **kwargs):
        self.data = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

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
        result = self.lookup(key, default=_marker)
        if result is _marker:
            raise KeyError(key)
        return result

    def __setitem__(self, key, val):
        self.register(key, val)

    def __delitem__(self, key):
        notrequires = self.data.get((), {})
        try:
            del notrequires[(key, '')]
        except KeyError:
            raise KeyError(key)

    def clear(self):
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
        return self.lookup(key, default=default)

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
        val = self.lookup(key, default=failobj)
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
        info = self.data.setdefault(tuple(requires), {})
        info[(provides, name)] =  component

    def lookup(self, provides, *requires, **kw):
        name = kw.get('name', '')
        default = kw.get('default', None)
 
        req = []
        for val in requires:
            if not hasattr(val, '__iter__'):
                req.append((val, None))
            else:
                req.append(tuple(val) + (None,))

        def _resolve(r):
            result = reg.get(r, _marker)
            if result is not _marker:
                key = (provides, name)
                val = result.get(key, _marker)
                if val is not _marker:
                    return val
            return _marker

        combinations = cached_product(*req)
        reg = self.data
        defer = []

        for combo in combinations:
            if None in combo:
                defer.append(combo)
                continue
            val = _resolve(combo)
            if val is not _marker:
                return val

        for combo in defer:
            val = _resolve(combo)
            if val is not _marker:
                return val

        return default

    def resolve(self, provides, *objects, **kw):
        requires = [ providedby(obj) for obj in objects ]
        return self.lookup(provides, *requires, **kw)

    def adapt(self, provides, *objects, **kw):
        factory = self.resolve(provides, *objects, **kw)
        return factory(*objects)

def providedby(obj):
    """ Return a sequence of component types provided by obj ordered
    most specific to least specific.  A special case exists: if
    ``obj`` is None, the sequence ``[None]`` is returned"""
    if obj is None:
        return [None]

    if inspect.isclass(obj):
        lookup = inspect.getmro(obj)
    else:
        lookup = (obj,) + inspect.getmro(obj.__class__)

    provides = []

    for base in lookup:
        val = getattr(base, '__component_type__', _marker)

        if val is not _marker:
            if not hasattr(val, '__iter__'):
                val = [val]
            for item in val:
                if not item in provides:
                    provides.append(item)

    if hasattr(obj, '__class__'):
        provides.append(obj.__class__)
    else:
        provides.append(type(obj))

    return provides

