Release Notes
=============

Release notes for the CyberGISX platform can be found here: `https://cybergisxhub.cigi.illinois.edu/release-notes/ <https://cybergisxhub.cigi.illinois.edu/release-notes/>`_

For details and full changelogs, check out the releases on Github: `https://github.com/cybergis/cybergis-compute-python-sdk/releases <https://github.com/cybergis/cybergis-compute-python-sdk/releases>`_

[v0.2.4] - 2023-03-02
---------------------

Added
^^^^^

* Allow users to name folders in the UI in `#62 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/62>`_

Updated
^^^^^^^

* Minor Fixes to Site and Docstrings in `#59 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/59>`_
* update JSON login to avoid silent fails, confusing errors in `#61 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/61>`_
* Updated tests and fixed bug in Zip.py in `#63 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/63>`_


[v0.2.3] - 2022-10-06
---------------------

Added
^^^^^

* "Past Results" Tab with download buttons `#37 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/37>`_
* ``list_jupyter_host()`` functionality to see the Core whitelist `#55 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/55>`_

Updated
^^^^^^^

* Fix for broken ``list_job()`` function `#51 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/51>`_ 
* Fix for "error displaying widget: model not found" when using --force-install without --no-deps `#57 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/57>`_ 
* Minor UI bug fixes and QOL changes `#54 <https://github.com/cybergis/cybergis-compute-python-sdk/pull/54>`_

[v0.2.2] - 2022-09-08
---------------------

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