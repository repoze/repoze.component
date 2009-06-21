from repoze.component.registry import _subscribers

def component(context, structure):

    if not isinstance(structure, dict):
        raise ValueError('Bad structure for component directive')

    diff = context.diffnames(structure, ['provides', 'requires', 'name',
                                         'object'])
    if diff:
        raise ValueError('Unknown key(s) in "adapter" directive: %r' % diff)

    provides = context.getvalue(structure, 'provides')
    if provides is None:
        raise ValueError('Missing "provides" attribute')

    requires = context.getvalue(structure, 'requires', type=list)
    if requires is None:
        requires = ()

    requires = tuple(requires)

    component = context.getvalue(structure, 'object')
    if component is None:
        raise ValueError('Missing "object" attribute')

    component = context.resolve(component)

    name = structure.get('name', '')
    kw = dict(name=name)

    callback = context.call_later(context.registry.register,
                                  provides, component, *requires, **kw)
    discriminator = ('component', requires, provides, name)
    return [ {'discriminator':discriminator, 'callback':callback} ]

def subscriber(context, structure):
    if not isinstance(structure, dict):
        raise ValueError('Bad structure for component directive')

    diff = context.diffnames(structure, ['requires', 'name', 'object'])
    if diff:
        raise ValueError('Unknown key(s) in "subscriber" directive: %r' % diff)

    structure['provides'] = _subscribers
    return component(context, structure)

    
    
