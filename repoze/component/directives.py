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

    requires = tuple(requires)

    factory = context.getvalue(structure, 'factory')
    if factory is None:
        raise ValueError('Missing "factory" attribute')

    factory = context.resolve(factory)

    name = structure.get('name', '')
    kw = dict(name=name)

    callback = context.call_later(context.registry.register,
                                  provides, factory, *requires, **kw)
    discriminator = ('adapter', requires, provides, name)
    return {'discriminator':discriminator, 'callback':callback}

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
    callback = context.call_later(context.registry.register,
                                  provides, component, **kw)

    return {'discriminator':discriminator, 'callback':callback}

