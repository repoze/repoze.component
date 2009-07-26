Using ``repoze.component`` with ``repoze.configuration``
========================================================

:mod:`repoze.component` makes use of :term:`repoze.configuration` to
allow configurations to be expressed via :term:`YAML`.  It makes two
directives: ``component`` and ``subscriber`` available to systems
which use :mod:`repoze.configuration`.

.. _loading_from_a_config_file:

Loading Components from a Configuration File
--------------------------------------------

To load and execute a configuration file that contains
``repoze.component`` registrations, use the following pattern"

.. code-block:: python
   :linenos:

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

:mod:`repoze.component` has a built-in :mod:`repoze.configuration`
directive named "component".  Its usage allows you to populate the
registry with a key-value pair where the key (``provides``) is a
string and the value (``object``) is an importable Python object,
resolveable via a dotted name.  Optionally, the component can also
have a ``name``.  The ``object`` and ``provides`` keys are required.
The ``name`` argument defaults to the empty string.

.. code-block:: text
   :linenos:

   --- !component
   object: somepackage.hellomodule:hellofunc
   name: helloname
   provides: hello
   requires: - abc
             - def

If the ``object`` key value is a string that starts with a dot
(e.g. ``.foo``) or a colon (.e.g. ":foo") , the object's dottedname is
considered relative to the "current package".  The "current" package
is defined as the package in which the YAML file we're parsing
resides.  If we're not parsing a YAML file inside a package, it
defaults to the current working directory.  If the object value does
not start with a color or dot, it is considered a fully qualified
package path to a Python global object.

If the ``name`` is not specified or is empty, the eventual
registration performed by this directive is equivalent to:

.. code-block:: python
   :linenos:

   >>> registry.register('hello', object, 'abc', 'def')

Subseqent lookups for this unnamed component in the registry can be
accomplished via:

.. code-block:: python
   :linenos:

   >>> registry.lookup('hello', 'abc', 'def')

If the ``name`` *is* specified and nonempty, the eventual registration
performed by this directive in the registry is equivalent to:

.. code-block:: python
   :linenos:

   >>> registry.register('hello', object, 'abc', 'def', name='thename')

Subseqent lookups for this named component in the registry can be
accomplished via:

.. code-block:: python
   :linenos:

   >>> registry.lookup('hello', 'abc', 'def', name='thename')

The ``requires`` argument is optional.  If it exists, it must be a
list of "required" component types for this registration.

Note that the directive YAML also takes a boolean-style key named
``override``.  If this is specified, this registration will override
any earlier registration for the same component even if it conflicts
with that earlier registration.  For example:

.. code-block:: text
   :linenos:

   --- !component
   object: somepackage.hellomodule:hellofunc
   name: helloname
   provides: hello
   requires: - abc
             - def
   override: true


The Subscriber Directive
------------------------

:mod:`repoze.component` has a built-in :mod:`repoze.configuration`
directive named "subscriber".  Its usage allows you to populate the
registry with a subscriber which will be notified when a registry's
``notify`` method is called with appropriate arguments.  It is
identical to the ``component`` directive except:

-  it does not accept a ``provides`` value.

- The ``object`` that is registered must be a callable which will
  accept a number of arguments equal to the number of ``requires``
  values (it is an "adapter").

.. code-block:: text
   :linenos:

   --- !subscriber
   object: somepackage.subscribers:asubscriber
   name: helloname
   requires: - abc
             - def

The above registration assumes that the ``asubscriber`` callable
referred to above is a callable that accepts two arguments (the
objects being adapted by the subscriber).

Note that the directive YAML also takes a boolean-style key named
``override``.  If this is specified, this registration will override
any earlier registration for the same component even if it conflicts
with that earlier registration.  For example:

.. code-block:: text
   :linenos:

   --- !subscriber
   object: somepackage.subscribers:asubscriber
   name: helloname
   requires: - abc
             - def
   override: true
