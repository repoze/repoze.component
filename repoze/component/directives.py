from repoze.component.registry import _subscribers

def component(declaration):
    expect_names = ['provides', 'requires', 'name', 'object']
    declaration.expect(dict, names=expect_names)

    provides = declaration.string('provides')
    if provides is None:
        declaration.error('Missing "provides" attribute')

    requires = declaration.getvalue('requires', typ=list)
    if requires is None:
        requires = ()

    requires = tuple(requires)

    component = declaration.string('object')
    if component is None:
        declaration.error('Missing "object" attribute')

    override = declaration.boolean('override', False)

    component = declaration.resolve(component)

    name = declaration.string('name', '')
    kw = dict(name=name)

    callback = declaration.call_later(declaration.registry.register,
                                      provides, component, *requires, **kw)
    discriminator = ('component', requires, provides, name)
    declaration.action(callback, discriminator, override=override)

def subscriber(declaration):
    expect_names = ['requires', 'name', 'object']
    diff = declaration.expect(dict, names=expect_names)

    declaration.structure['provides'] = _subscribers
    component(declaration)

    
    
