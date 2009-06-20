def component(context, structure):

    if not isinstance(structure, dict):
        raise ValueError('Bad structure for component directive')

    diff = context.diffnames(structure, ['provides', 'requires', 'name',
                                         'component'])
    if diff:
        raise ValueError('Unknown key(s) in "adapter" directive: %r' % diff)

    provides = context.getvalue(structure, 'provides')
    if provides is None:
        raise ValueError('Missing "provides" attribute')

    requires = context.getvalue(structure, 'requires', type=list)
    if requires is None:
        requires = ()

    requires = tuple(requires)

    component = context.getvalue(structure, 'component')
    if component is None:
        raise ValueError('Missing "component" attribute')

    component = context.resolve(component)

    name = structure.get('name', '')
    kw = dict(name=name)

    callback = context.call_later(context.registry.register,
                                  provides, component, *requires, **kw)
    discriminator = ('component', requires, provides, name)
    return [ {'discriminator':discriminator, 'callback':callback} ]
