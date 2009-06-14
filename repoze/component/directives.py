def adapter(context, structure):

    if not isinstance(structure, dict):
        raise ValueError('Bad structure for adapter directive')

    diff = context.diffnames(structure, ['provides', 'requires', 'name',
                                         'factory'])
    if diff:
        raise ValueError('Unknown key(s) in "adapter" directive: %r' % diff)

    provides = context.getvalue(structure, 'provides')
    if provides is None:
        raise ValueError('Missing "provides" attribute')

    requires = context.getvalue(structure, 'requires', type=list)
    if requires is None:
        raise ValueError('Missing "requires" attribute')

    factory = context.getvalue(structure, 'factory')
    if factory is None:
        raise ValueError('Missing "factory" attribute')

    factory = context.resolve(factory)

    name = structure.get('name', '')
    kw = dict(name=name)

    callback = CallLater(context.registry.register,
                         provides, factory, *requires, **kw)
    discriminator = ('adapter', requires, provides, name)
    return discriminator, callback

def utility(context, structure):
    if not isinstance(structure, dict):
        raise ValueError('Bad structure for utility directive')

    diff = context.diffnames(structure, ['provides', 'component', 'name'])
    if diff:
        raise ValueError('Unknown key(s) in "utility" directive: %r' % diff)

    provides = context.getvalue(structure, 'provides')
    if provides is None:
        raise ValueError('Missing "provides" attribute')

    component = context.getvalue(structure, 'component')
    if component is None:
        raise ValueError('Missing "component" attribute')

    component = context.resolve(component)

    name = context.getvalue(structure, 'name', '')
    kw = dict(name=name)

    discriminator = ('utility', provides, name)
    callback = CallLater(context.registry.register,
                         provides, component, **kw)

    return discriminator, callback

class CallLater(object):
    def __init__(self, func, *arg, **kw):
        self.func = (func,)
        self.arg = arg
        self.kw = kw

    def __call__(self):
        return self.func[0](*self.arg, **self.kw)

