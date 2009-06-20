Using ``repoze.component`` with ``repoze.configuration``
=======================================================

:mod:`repoze.component` makes use of :term:`repoze.configuration` to
allow configurations to be expressed via :term:`YAML`.  It makes a
``component`` directive available to systems which use
:mod:`repoze.configuration`.

.. _loading_from_a_config_file:

Loading Components from a Configuration File
--------------------------------------------

To load and execute a configuration file that contains
``repoze.component`` registrations, use the following pattern"

.. code-block:: python

   from repoze.component import Registry

   from repoze.configuration import Context
   from repoze.configuration import execute

   registry = Registry()
   context = Context(registry)
   execute('somefile.yml', context=context)

At this point the registry (a :mod:`repoze.component` registry) will
be populated.

The Component Directive
-----------------------

:mod:`repoze.component` has a single built-in directive named
"component".  Its usage allows you to populate the registry with a
key-value pair where the key (``provides``) is a string and the value
(``component``) is an importable Python object, resolveable via a
dotted name.  Optionally, the component can also have a ``name``.  The
``component`` and ``provides`` keys are required.  The ``name``
argument defaults to the empty string.

.. code-block:: text

   --- !component
   component: somepackage.hellomodule:hellofunc
   name: helloname
   provides: hello
   requires: - abc
             - def

If the ``component`` key value is a string that starts with a dot
(e.g. ``.foo``) or a colon (.e.g. ":foo") , the component dottedname
is considered relative to the "current package".  The "current"
package is defined as the package in which the YAML file we're parsing
resides.  If we're not parsing a YAML file inside a package, it
defaults to the current working directory.  If the component value
does not start with a color or dot, it is considered a fully qualified
package path to a Python global object.

If the ``name`` is not specified or is empty, the eventual
registration performed by this directive is equivalent to:

.. code-block:: python

   >>> registry.register('hello', component, 'abc', 'def')

Subseqent lookups for this unnamed component in the registry can be
accomplished via:

.. code-block:: python

   >>> registry.lookup('hello', 'abc', 'def')

If the ``name`` *is* specified and nonempty, the eventual registration
performed by this directive in the registry is equivalent to:

.. code-block:: python

   >>> registry.register('hello', component, 'abc', 'def', name='thename')

Subseqent lookups for this named component in the registry can be
accomplished via:

.. code-block:: python

   >>> registry.lookup('hello', 'abc', 'def', name='thename')

The ``requires`` argument is optional.  If it exists, it must be a
list of "required" component types for this registration.
