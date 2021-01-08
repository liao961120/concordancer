from m2r import parse_from_file

README = '../README.md'

readme_rst = parse_from_file(README)

index_template = '''
Searching Medium-Sized Corpus with Corpus Query Language (CQL)
==============================================================

Installation
------------

.. code-block:: bash

   pip install -U concordancer


.. toctree::
   :maxdepth: 2
   :caption: Contents
   :numbered:

   concordancer
   server
   kwic_print
   demo


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''