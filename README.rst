CamelParser
=============

.. image:: https://img.shields.io/pypi/l/camel-tools.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

Introduction
------------

CAMel CoNLL is a suite of tools that helps improve CoNLL-X file quality for annotators.
It is designed specifically for Arabic, but some of the tools are language independent.

Current tools:

* CATiB enrichment: converts CATiB part-of-speech tags and dependency relation labels to traditional Arabic tags and labels.
* Comma fixer: fixes incorrectly attached commas while preserving attachment and projectivity rules of CoNLL files.
* CoNLL evaluation: compares parsed CoNLL file(s) with gold CoNLL files(s).
* CoNLL statistics: gets general statistics of one or more CoNLL files.
* Well-formedness checker: checks if one or more CoNLL files adhere to a set of rules.

Installation
------------
1. Clone this repo

2. Set up a virtual environment. The tools have been tested using Python 3.11.13.

3. Install the required packages:

.. code-block:: bash

    pip install -r requirements.txt

Tools
--------------------

CATiB enrichment
^^^^^^^^^^^^^^^^

Convert the part-of-speech tags and dependency relation labels from CATiB to traditional Arabic tags and labels.

This conversion is done using a set of rules found in the latest map file, catib_enrichment/patterns_[version_number].

To run CATiB enrichment:

.. code-block:: bash
    python catib_enrichment.py -i path/to/file(s) -o path/to/output

The -m parameter is optional, as the latest stable map file will be used by default.


Comma fixer
^^^^^^^^^^^

After running files through a dependency parser, some trees may contain commas that have incorrect attachments. 
The comma fix script is used on a CoNLL file or directory of CoNLL files in order to make these fixes by attaching the comma to
a token behind it that is not the root, and does not cause non-projectivity.

To run the comma fixer:

.. code-block:: bash

    python comma_fix.py -i [path/to/file/or/dir] -o [output/path/]

Note that if the input and output directories are the same, the fixed CoNLL files will will have 'comma_fixed' attached to the end.

CoNLL evaluation
^^^^^^^^^^^^^^^^

See the `CoNLL evaluation README <https://github.com/CAMeL-Lab/camel_conll/tree/main/conll_evaluation/README.md>`_ for details of the tool and how to run it.

CoNLL statistics
^^^^^^^^^^^^^^^^

See the `CoNLL statistics README <https://github.com/CAMeL-Lab/camel_conll/tree/main/conll_stats/README.md>`_ for details of the tool and how to run it.

Well-formedness checker
^^^^^^^^^^^^^^^^^^^^^^^

You can pass a CoNLL file or directory of CoNLL files:

.. code-block:: bash
    python wellformedness_checker.py -i [path/to/file/or/dir] -o [output/path/]

The checker uses the r13 database by default, but you can pass calima-msa-s31. See the Databases section for details.

.. _Other Morph DB:
Using another morphology database
---------------------------------

Curently, the Well-formedness checker uses CAMeLTools' default morphology database, the morphology-db-msa-r13.

You can use the calima-msa-s31 database by first installing it.
follow these steps (note that you need an account with the LDC):

1. Install camel_tools v1.5.2 or later (you can check this using camel_data -v)

2. Download the camel data for the BERT unfactored (MSA) model, as well as the morphology database:

.. code-block:: bash

    camel_data -i morphology-db-msa-s31 
    camel_data -i disambig-bert-unfactored-msa

3. Download the LDC2010L01 from the ldc downloads:
    - go to https://catalog.ldc.upenn.edu/organization/downloads
    - search for LDC2010L01.tgz and download it

4. DO NOT EXTRACT LDC2010L01.tgz! We'll use the following command from camel tools to install the db:

.. code-block:: bash

    camel_data -p morphology-db-msa-s31 /path/to/LDC2010L01.tgz

5. When running the Well-formedness checker script, use -b and pass calima-msa-s31.