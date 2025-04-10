.. Epilepsy Tools documentation master file, created by
   sphinx-quickstart on Fri Mar 21 11:35:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Epilepsy Tools documentation
============================

Documentation for the ``epilepsy_tools`` Python package, which contains pre-written function to handle data from the various connected wearables used in the epilepsy research lab at CRCHUM.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   cometa
   hexoskin
   epidatavault
   examples

Installation
------------

To install the package in your project, you have two options:

With ``uv``
^^^^^^^^^^^
.. code-block:: bash

   # if the project does not already exist
   uv init my-project
   cd my-project

   uv add git+https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools.git

With ``pip``
^^^^^^^^^^^^
.. code-block:: bash

   pip install git+https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools.git

Logging
-------

Enable logging for the module with:

.. code-block:: python

   import logging

   logger = logging.get_Logger("epilepsy_tools")
   logger.setLevel(logging.DEBUG)
   logger.addHandler(logging.StreamHandler())


Links
-----
- `GitHub Repository <https://github.com/CRCHUM-Epilepsy-Group/epilepsy_tools>`_
