Documentation for repoze.component
==================================

Introduction
------------

:mod:`repoze.component` is a package that software developers can use to
provide configurability and pluggability to their applications.
:mod:`repoze.component` provides a generalized indirection mechanism
which can be used to provide plugin points to integrators or other
developers who may wish to provide alternate implementations of
application logic or configuration values.

The :mod:`repoze.component` registry can help provide a highly general
application configuration system.  If logic in your application
indirects lookups through a :mod:`repoze.component` "component registry",
other developers or integrators can supply your application with
configuration values and, possibly, implementation objects.  You can
expose a :mod:`repoze.component` configuration file to an end user to
configure or customize the application as necessary.

:mod:`repoze.component` also provides a generic event subscription and
notification system.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   basic
   component
   event
   directives
   glossary

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
