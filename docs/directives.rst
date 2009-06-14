Using ``repoze.component`` with ``repoze.configuration``
=======================================================

:mod:`repoze.component` makes use of :mod:`repoze.configuration` to
allow configurations to be expressed via :term:`YAML`.  It makes
``utility`` and ``adapter`` directives available to systems which use
:mod:`repoze.configuration`.

Loading
-------

To load and execute a configuration file that contains
``repoze.component`` registrations, use the following pattern"

.. code-block:: python

   from repoze.component import Registry

   from repoze.configuration import Context
   from repoze.configuration import execute

   registry = Registry()
   context = Context(registry)
   execute('somefile.yml', context=context)

The Utility Directive
---------------------

:mod:`repoze.component` has a built-in directive named "utility".  Its
usage allows you to populate the registry with a key-value pair where
the key (``provides``) is a string and the value (``component``) is an
importable Python object, resolveable via a dotted name.  Optionally,
the utility can also have a "name".  The ``component`` and
``provides`` keys are required.  The ``name`` argument defaults to the
empty string.

.. code-block:: text

   --- !utility
   provides: hello
   component: somepackage.hellomodule:hellofunc
   name: helloname

If the ``component`` key value is a string that starts with a dot
(e.g. ``.foo``), the component dottedname is considered relative to
the "current package".  The "current" package is defined as the
package in which the YAML file we're parsing resides.  If we're not
parsing a YAML file inside a package, it defaults to the current
working directory.

If the ``name`` is not specified or is empty, the eventual
registration performed by this directive is equivalent to:

.. code-block:: python

   >>> registry['hello'] = component

Subseqent lookups for this unnamed utility in the registry can be
accomplished via:

.. code-block:: python

   >>> registry['hello']

If the ``name`` *is* specified and nonempty, the eventual registration
performed by this directive in the registry is equivalent to:

.. code-block:: python

   >>> registry.register(component, 'hello', name='helloname')

Subseqent lookups for this named utility in the registry can be
accomplished via:

.. code-block:: python

   >>> registry.lookup('hello', name='helloname')

The Adapter Directive
---------------------

XXX not yet documented

