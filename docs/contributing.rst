Contributing to CyberGIS-Compute
================================

Contributing to the SDK
-----------------------

First, consider if the change requires changes to the SDK (this repo), the Core (the server/backend) or both. We welcome contributions, but before you send a pull request, please check that your code meets our standards. Specifically:

Code Quality
^^^^^^^^^^^^

We recommend using flake8 and you can check the Github workflow (`.github/workflows/PythonQualityCheck.yml`) to see any errors/warning you can safely ignore. Some resources for linting:

* `flake8 <https://flake8.pycqa.org/en/latest/>`_.
* `Linting Python in Visual Studio Code <https://code.visualstudio.com/docs/python/linting>`_.

Code Tests
^^^^^^^^^^

We have limited code tests to check for changes that break the SDK. Please check that your code passes our checks before submitting. If the changes you have made break our tests for a good reason, feel free submit the Pull Request and let us know!

We are also hoping to grow our test cases and welcome help on that end!


Tools for Testing Github Actions Locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We prefer that contributions pass our Github actions, so here are some tips on checking they pass locally.

`act <https://github.com/nektos/act>`_
""""""""""""""""""""""""""""""""""""""

There are a variety of ways to install act, and once installed it offers a flexible tool for testing that your code passes Github actions. All commands should be run from the root of the repository. 

* List Github actions::

    > act -l
    Stage  Job ID       Job name             Workflow name        Workflow file            Events
    0      build        build                Python Code Test     PythonCodeTestCases.yml  push  
    0      flake8-lint  Python Code Quality  Python Code Quality  PythonQualityCheck.yml   push 


* Run a specific action locally::

    > act -j <Jpb string>


* Run all actions::

    > act

Contributing to the Docs
------------------------

We welcome contributions to the documentation! Please ensure that any contributions are appropriate for this repository and not the many related projects: :doc:`/external`

Our documentation is build with `Sphinx <https://www.sphinx-doc.org/en/master/index.html>`_ and written in `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ (`Quick reference for RST <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_).

After making changes, you can see what the site will look like by running `make html` from the `docs/` folder.