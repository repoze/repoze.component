Basic Usage
===========

Creating a Component Registry
-----------------------------

To make any use of :mod:`repoze.component`, you must create a
component registry.  Creating a component registry is straightforward.

.. code-block:: python

   >>> from repoze.component import Registry
   >>> registry = Registry()

Registering a :mod:`repoze.component` Component
-----------------------------------------------

A component is any Python object registered in a component registry.
It can be retrieved later via an API of the registry.

To register a :mod:`repoze.component`, component imperatively, developers
can use the ``register`` method of a component registry.  The simplest
form of registration takes a ``provides`` argument, and a component
argument.

.. code-block:: python

   >>> registry.register('a', 'somecomponent')

The component (in this case, the string ``somecomponent``) registered
using the first argument (``a``) can later be looked up using the
``lookup`` method of the registry.

.. code-block:: python

   >>> registry.register('a', 'somecomponent')
   >>> registry.lookup('a')
   'somecomponent'

A pattern like the above gives a registry the basic functionality of a
Python dictionary.  In fact, the registry can also be treated like a
dictionary API-wise (via ``__getitem__``, ``__setitem__``,
``__delitem__``, ``get``, ``update``, ``items``, ``setdefault``, etc)
for these sorts of simple registrations and lookups.

.. code-block:: python

   >>> registry['a'] = 'somecomponent'
   >>> registry['a']
   'somecomponent'
   >>> registry.get('a')
   'somecomponent'
   >>> registry.get('b', None)
   None

More Complicated Registrations and Lookups
------------------------------------------

More complicated registrations can include one or more "requires"
values in the call to ``register``.  A "requires" value is one that
needs to *also* match the registration in combination with the
"provides" value when it's later looked up.

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires1')

A component registered along with a "requires" value is looked up
using the ``lookup`` method of the registry.  To successfully get the
component back, the "requires" values passed to the ``lookup`` method
must match those it has been registered with.  If a component cannot
be found, a ``LookupError`` is raised unless a ``default`` argument
was supplied to the ``lookup`` or ``resolve`` method (in which case
the default value is returned).

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires1')
   >>> registry.lookup('a', default=None)
   None
   >>> registry.lookup('a', 'notrequires', default=None)
   None
   >>> registry.lookup('a', 'requires1')
   'somecomponent'

The dictionary getter APIs present on a registry will *not* return
components registered with any requires values.  The dictionary API
cannot be used to find registrations made with "requires" arguments.

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires')
   >>> registry.get('a')
   None

You can register an arbitrary number of "requires" elements for a
component.  They are all required (in the same order) to later look
the component up via ``lookup``.

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires1', 'requires2')
   >>> registry.lookup('a', 'requires1', default=None)
   None
   >>> registry.lookup('a', 'requires1', 'requires2')
   'somecomponent'

You can also pass sequences of values as "requires" elements to the
``lookup`` API; each element in each sequence is compared
left-to-right in order to find a match (see :ref:`lookup_ordering`).

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires1', 'requires2')
   >>> registry.lookup('a', ['requires1'], default=None)
   None
   >>> registry.lookup('a', ['requires1', 'somethingelse'], ['indeed', 'requires2'])
   'somecomponent'

Any requires element can be a sequence or a non-sequence:

.. code-block:: python

   >>> registry.register('a', 'somecomponent', 'requires1', 'requires2')
   >>> registry.lookup('a', ['requires1'], default=None)
   None
   >>> registry.lookup('a', ['requires1', 'somethingelse'], 'requires2')
   'somecomponent'

Use ``None`` as one of the "requires" elements to the ``register`` API
to create a registration that can later be resolved in ``lookup`` via
*any* requires element.  ``None`` as a requires element is essentially
a wildcard.

.. code-block:: python

   >>> registry.register('a', 'somecomponent', None, 'requires2')
   >>> registry.lookup('a', 'requires1', 'requires2')
   'somecomponent'
   >>> registry.lookup('a', 'whatever', 'requires2')
   'somecomponent'
   >>> registry.lookup('a', None, 'requires2')
   'somecomponent'

You can unregister an existing registration by using the
``unregister`` method:

.. code-block:: python

   >>> registry.unregister('a', 'somecomponent', None, 'requires2', name='foo')

.. _lookup_ordering:

Component Lookup Order When ``Requires`` Arguments are Specified
----------------------------------------------------------------

When the ``lookup`` method of a registry is supplied with a single
requires value, that requires value is used to attempt to locate a
component in conjunction with the provides value.  A ``requires``
value can be a single object or an iterable object (like a list).

When a single "requires" argument is provided, we try to resolve the
arguments to a component using a left-to-right algorithm.  This is
easiest to explain via a series of examples.

.. code-block:: python

   >>> registry.lookup('a', 'requires1')

The search ordering for the above lookup statement is as follows.  We
look for something providing ``a``:

- registered with the requires value ``requires1``

- registered with the requires value ``None``

A ``None`` value is always implied when using lookup directly in order
to match registration made with a ``None`` requires argument (the
wildcard).

When any "requires" value is a sequence, things become more complicated.

.. code-block:: python

   >>> registry.lookup('a', ['requires2', 'requires1'])

The search ordering for the above lookup statement is as follows.  In
this case, we look for something providing ``a``:

- registered with the requires value ``requires2``

- registered with the requires value ``requires1``

- registered with the requires value ``None``

If a match is found at any time during search, the search is abandoned
and the component is returned.  If a component cannot be found, a
``LookupError`` is raised unless a ``default`` argument was supplied
to the ``lookup`` or ``resolve`` method (in which case the default
value is returned).

When multiple "requires" arguments are supplied, things become
considerably more complicated.  In general, the algorithm can be
described as "left to right, most specific first".  In specific, an
ordered cartesian product of the combinations of requires values
provided are searched for a match.

When the ``lookup`` method of a registry is used, we check the
combinations (the product) of possible requires values in the a
most-speficic-to-least specific order.  For example, the following
``lookup`` call produces searches for "requires" values in the
following order:

.. code-block:: python

   >>> registry.lookup('z', ['i', 'one', 'two'], ['i', 'a', 'b'])

We look for something providing ``z``:

- with the first requires values ``i`` and the second requires value ``i``

- with the first requires values ``i`` and the second requires value ``a``

- with the first requires values ``i`` and the second requires value ``b``

- with the first requires values ``one`` and the second requires value ``i``

- with the first requires values ``one`` and the second requires value ``a``

- with the first requires values ``one`` and the second requires value ``b``

- with the first requires values ``two`` and the second requires value ``i``

- with the first requires values ``two`` and the second requires value ``a``

- with the first requires values ``two`` and the second requires value ``b``

- with the first requires values ``i`` and the second requires value ``None``

- with the first requires values ``one`` and the second requires value ``None``

- with the first requires values ``two`` and the second requires value ``None``

- with the first requires values ``None`` and the second requires value ``i``

- with the first requires values ``None`` and the second requires value ``a``

- with the first requires values ``None`` and the second requires value ``b``

- with the first requires values ``None`` and the second requires value ``None``

A similar lookup ordering happens for more than two requires
specifications, based on the cartesian product of all supplied
requires values.

As usual, the search is abandoned when any registration is found that
matches the provides and requires values.

Using ``ALL``
-------------

A special argument ``repoze.configuration.ALL`` may be passed as a
``name=`` argument to the ``unregister``, ``notify``, ``lookup``, and
``resolve`` methods of a registry.  This is an advanced feature which
very few people need to use, which essentially allows you to do a
wildcard match on registrations made under *any* ``name``.

- If you supply ``name=ALL`` to the ``unregister`` method, all named
  and unnamed registrations which match the other arguments supplied
  will be unregistered.

- If you supply ``name=ALL`` to the ``notify`` method, all subscribers
  without respect to their name will be notified (all named and
  unnamed subscribers which match the other arguments supplied to the
  method).

- If you supply ``name=ALL`` to the ``lookup`` method, you will be
  returned a list if any registration was made for the other arguments
  in the list; each element in the list will be the item registered
  under the requires args used, without respecting the ``name`` the
  item was registered under.

- If you supply ``name=ALL`` to the ``resolve`` method, you will be
  returned a list if any registration was made for the other arguments
  in the list; each element in the list will be the item registered
  under the requires objects passed, without respecting the ``name``
  each was registered under.

