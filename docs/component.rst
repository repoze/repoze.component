Using :mod:`repoze.component` as a Component System
===================================================

We've seen the basic registration and lookup facilities of a
:mod:`repoze.component` registry.  You can provide additional
functionality to your applications if you use it as an "component
registry".  Using a registry as a component registry makes it possible
to use the :mod:`repoze.component` registry for the same purposes as
something like :term:`zope.component`.

The extra method exposed by a :mod:`repoze.component` registry that
allow you to treat it as a component regstry is ``resolve``.  The
``resolve`` method simply accepts a provides value and a sequence of
*objects that supply component types*.  When called with a list of
objects that supply component types, ``resolve`` returns a matching
component.

"Requires" Objects Supply Component Types
-----------------------------------------

Objects used as "requires" arguments to the ``resolve`` method of a
component registry usually supply a component type.  This is done by
adding using the ``provides`` function against objects passed to these
methods.

The ``provides`` function may be used within a class definition, it
may be used as a class decorator, or it may be applied against an
instance. Within a class definition and as a class decorator, it
accepts as positional arguments the component types.

.. code-block:: python

   from repoze.component import provides

   class MyObject(object):
       provides('mytype')

The followng is also legal.

.. code-block:: python

   from repoze.component import provides

   class MyObject(object):
       provides('mytype', 'anothertype')

Likewise, it's also legal to do (in Python 2.6):

.. code-block:: python

   from repoze.component import provides

   @provides('mytype', 'anothertype')
   class MyObject(object):
       pass

You can also use the ``provides`` function against an instance, in
which case the first argument is assumed to be the object you're
trying to assign component types to:

.. code-block:: python

    from repoze.component import provides

    class MyObject(object):
        pass

    obj = MyObject()
    provides(obj, 'mytype', 'anothertype')

Note that objects don't explicitly need to have a ``provides``
attribute attribute for simple usage; the class of an object is an
implicit component type that can be used in registrations.

"Under the hood", the ``provides`` function sets the
``__component_types__`` attribute on a class or object.

How :mod:`repoze.component` Computes an Effective Component Type for a Requires Object
--------------------------------------------------------------------------------------

When a component type is computed for an object, the object is
searched in the following order.  All values are collected and used to
construct the final "requires" argument used.

- The object itself is checked for the ``__component_types__``
  attribute.

- If the object is a class, its base classes are checked in Python MRO
  order for a ``__component_types__`` attribute.

- If the object is an instance, its class then its base classes are
  checked in Python MRO order for a ``__component_types__`` attribute.

- The object's class is added as an unconditional component type.

We'll use the following set of objects as examples:

.. code-block:: python

    from repoze.component import provides

    class A(object):
        provides('a', 'hello')

    class B(A):
        provides('b')

    class C(B):
        provides('c')

    instance = C()
    provides(instance, 'i')

If "instance" is used as an argument to the ``resolve`` method of an
component registry:

- We first look at the instance to find a component type.  This
  finds component type ``i``.

- We look at its direct class ``C`` which finds component type ``c``.

- We look at the component type of the base classes of the ``C``
  class.  The B class provides component type ``b``, the ``A`` class
  provides component types (``a`` and ``hello``).

- We use the object's class.

- We use the value ``None``.

Thus our "requires" argument for this particular object is ``['i',
'c', 'b', 'a', 'hello', C, None]``.  Every object supplied as a
"requires" argument to the ``resolve`` method of a component registry
has its requires values computed this way.  We then find a component
based on the set of requires arguments passed in ala
:ref:`lookup_ordering`.

Comparing :mod:`repoze.component` to :term:`zope.component`
-----------------------------------------------------------

Zope and Twisted developers (and any other developer who has used
:term:`zope.component`) will find :mod:`repoze.component` familiar.
:mod:`repoze.component` steals concepts shamelessly from
:term:`zope.component`.  :mod:`repoze.component` differs primarily from
:term:`zope.component` by abandoning the high-level concept of an
:term:`interface`.  In :term:`zope.component`, component lookups and
registrations are done in terms of interfaces, which are very specific
kinds of Python objects.  In :mod:`repoze.component`, interfaces are not
used.  Instead, components (such as "adapters" and "utilities") are
registered using marker "component types", which are usually just
strings although they can be any hashable type.

One major difference between :mod:`repoze.component` and
:mod:`zope.component` is that :mod:`repoze.component` has no real
support for the concept of an "adapter".  The things that you register
into a component registry are simply components.  You can register a
callable against some set of arguments, but :mod:`repoze.component`
will not *call* it for you.  You have to retrieve it and call it
yourself.

.. note::

  In the examples below, where a :term:`zope.component` API might
  expect an interface object (e.g. the interface ``ISomething``), the
  :mod:`repoze.component` API expects a component type (e.g. the string
  ``something``).  Also, in the examples below, whereas
  :term:`zope.component` users typically rely on APIs that consult a
  "global registry", :mod:`repoze.component` provides no such facility.
  Thus examples that refer to ``registry`` below refer to a plugin
  registry created by parsing a configuration file (or constructed
  manually).

The :mod:`repoze.component` equivalent of ``utility =
zope.component.getUtility(ISomething)`` is the following:

.. code-block:: python

  utility = registry.lookup('something')

The :mod:`repoze.component` equivalent of ``implementation =
zope.component.getAdapter(context, ISomething, name='foo')`` is the
following:

.. code-block:: python

  adapter = registry.resolve('something', context, name='foo')
  implementation = adapter(context)

The :mod:`repoze.component` equivalent of ``implementation =
getMultiAdapter((context1, context2), ISomething, name='foo')`` is the
following:

.. code-block:: python

  adapter = registry.resolve('something', context1, context2, name='foo')
  implementation = adapter(context1, context2)

Likewise, the :mod:`repoze.component` equivalent of ``implementation =
getMultiAdapter((context1, context2, context3), ISomething,
name='foo')`` is the following:

.. code-block:: python

  adapter = registry.resolve('something', context1, context2, context3, 
                             name='foo')
  implementation = adapter(context1, context2, context3)

