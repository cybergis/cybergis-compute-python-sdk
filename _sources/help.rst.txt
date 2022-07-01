Getting Help
============

First, you want to try to identify what exactly you need help with. The CyberGIS-Compute SDK is part of an integrated ecosystem, so it's common for people to be confused about what exactly isn't working. 

The problem is with CyberGISX or CyberGISX Hub
----------------------------------------------

Did you experience a problem when using CyberGISX or CyberGISX Hub and not specifically when you were using CyberGIS-Compute? The issue may be with with the system that you are running the code on.

* Check out the `Get Started <https://cybergisxhub.cigi.illinois.edu/get-started/>`_ page on CyberGISX Hub.
* The `FAQ <https://cybergisxhub.cigi.illinois.edu/faq/>`_ and `Knowledge Base <https://cybergisxhub.cigi.illinois.edu/knowledge-base/>`_ are also very helpful resources.
* If nothing else works, the CyberGISX Hub has a `Problem Report Form <https://cybergisxhub.cigi.illinois.edu/problem-report/>`_. Please reach out so that we can make the experience better for everyone!

The problem is specific to the model/job template
-------------------------------------------------

Did your job exit with errors? Are you able to run other jobs like the Hello World model? If so, the issue may be with the specific model you are running. We do not directly maintain every model and instead rely on an amazing community, so to identify the Github repository that corresponds to the model you are running, you can use the line::

    cybergis.list_git()

This assumes that your CyberGISCompute object is named "cybergis" so if it is not, call "list_git()" on the object. You should see an output like the one below:

.. figure:: _static/img/ListGit.png

Identify the model you are using in the "name" column and go to the Git repository ("repository") of the model. You can interact with the model developers there including searching issues and opening an issue if necessary.

The problem is with CyberGIS-Compute
------------------------------------

If you are having a problem using CyberGIS-Compute and it is not with a specific model/job template, check out the :doc:`usage` page.

If you are having a problem developing a model with CyberGIS-Compute, check the :doc:`model_contribution/index` page which has a guide on model development and an FAQ.

If those do not solve your problems, debugging get's a bit more complicated because CyberGIS-Compute has two main components: The SDK (the code you interact with to submit jobs) and the Core (the the server that manages jobs). The next steps would be:

* Head over to the `SDK repository <https://github.com/cybergis/cybergis-compute-python-sdk>`_ or `Core repository <https://github.com/cybergis/cybergis-compute-core>`_ and search the issues to see if others have run into this problem before.
* If none of the above works, feel free to open an issue on whichever repository. Do your best to figure out which repo would be more appropriate, but we understand that it is often hard to identify which part of the stack is causing the issue. We will do our best to respond and fix the problem!



Unsure what is causing your problem
-----------------------------------

* Check out the `FAQ <https://cybergisxhub.cigi.illinois.edu/faq/>`_ and `Knowledge Base <https://cybergisxhub.cigi.illinois.edu/knowledge-base/>`_ on CyberGISX Hub. These resources are designed to help you solve some common problems and answer questions that users run into.
