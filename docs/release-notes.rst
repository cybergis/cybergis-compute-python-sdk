Release Notes
=============

[v0.2.2] - Ongoing
------------------

Added
^^^^^

* Released on PyPi! `https://pypi.org/project/cybergis-compute-client/ <https://pypi.org/project/cybergis-compute-client/>`_
* Added ``input_params`` argument to ``show_ui`` to allow users to programmatically pass in model specific parameters.

Updated
^^^^^^^

* Minor tweaks and fixes to the UI

Removed
^^^^^^^

* Removed some unnecessary files (``RIF_UI_NBK/``, ``example_output/``, and ``spatial_accessibility.ipynb``).


[v2.1] - 2022-08-15
-------------------

Added
^^^^^

* Adds remote folders, more work needed to integrate them into the UI and documentation on their use.

Updated
^^^^^^^

* Small changes to our Jupyter-based authentication (closes `#27 <https://github.com/cybergis/cybergis-compute-python-sdk/issues/27>`_)
* Small bug fixes to the UI.

Removed
^^^^^^^

* Removed the Job Access Token (JAT) authentication method

[2.0] - 2022-07-25
------------------

Added
^^^^^

* Added user interface (UI) using Jupyter widgets.
* Added Jupyter-based authentication, using both Job Access Token (JAT) and Jupyter.
* Released public webpage for documentation: `https://cybergis.github.io/cybergis-compute-python-sdk/ <https://cybergis.github.io/cybergis-compute-python-sdk/>`_
* Added a "Your Jobs" tab and  "Refresh" button to restore jobs after the UI dies (closes `#15 <https://github.com/cybergis/cybergis-compute-python-sdk/issues/15>`_ and `#16 <https://github.com/cybergis/cybergis-compute-python-sdk/issues/16>`_).

Updated
^^^^^^^

* Named changed from ``job_supervisor_client`` to ``cybergis_compute_client``.
* Verified to be working on JupyterLab (closes `#6 <https://github.com/cybergis/cybergis-compute-python-sdk/issues/6>`_).


[v1] - 2021-10-26
-----------------

This version is on the branch v1: https://github.com/cybergis/cybergis-compute-python-sdk/tree/v1. The current deployment has been substantially reworked.