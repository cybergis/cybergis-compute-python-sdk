Deploying CyberGIS-Compute Core
===============================

.. attention::
    This part of the documentation refers to deploying the `CyberGIS-Compute Core <https://github.com/cybergis/cybergis-compute-core>`_ server. This is not required for typical users.



Running CyberGIS-Compute Core
-----------------------------

Basic instructions for deploying CyberGIS-Compute Core can be found on the `README for the Github repo <https://github.com/cybergis/cybergis-compute-core#server-setup>`_. Deployment has only been tested on Ubuntu 20.04, but should be possible on any system with Docker, Docker Compose, and npm.

We also have a development repo `cybergis/cybergis-compute-local-hpc <https://github.com/cybergis/cybergis-compute-local-hpc>`_ which allows you to deploy a self-contained environment for testing and developing on CyberGIS-Compute. The instructions launch the Core server, as well as a MySQL server, JupyterHub, and a small SLURM cluster. It is not recommended that you use this SLURM cluster for running computationally heavy jobs and instead get access to a real HPC environment through your local university, through `NFS ACCESS <https://access-ci.org/>`_, or cloud computing providers.

Scalability Considerations
--------------------------

CyberGIS-Compute Core is capable of running many jobs simultaneously (`with jobs not running stored in the Queue <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/src/Queue.ts>`__), with a few important configurations available to those deploying their own Core.

* Note that many HPC systems will impose a maximum number of running jobs through their SLURM configuration. CyberGIS-Compute Core configutations are not able to override these settings.
* For each HPC configured (in ``configs/hpc.json``), you are able to specify a ``job_pool_capacity`` which is the maximum number of jobs that Core will submit simultaneously on a given HPC resource. `See example <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/configs/hpc.example.json#L19>`__.
* The speed at which the job Queue is checked can be increased for Core servers which are expected to have high throughput in `the config.json file <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/config.example.json#L26>`__.

We have yet to find the maximum number of concurrent jobs running on CyberGIS-Compute, but if you run into these problems, please `file an issue on the Github repository <https://github.com/cybergis/cybergis-compute-core/issues>`__.



Resource Limitations
--------------------

HPC/Compute Limitations
^^^^^^^^^^^^^^^^^^^^^^^

Generally, CyberGIS-Compute Core does not affect the resources used by models and you are limited only by the HPCs you have access to. Core will create a SLURM batch script and the HPC you submit it to will handle this resource request.

The main exception to this rule is the ``defaultSlurmCeiling`` in ``src/lib/JobUtil.ts`` (`see example <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/src/lib/JobUtil.ts#L210>`__). ::

    var defaultSlurmCeiling = {
      num_of_node: 50,
      num_of_task: 50,
      cpu_per_task: 50,
      memory_per_cpu: "10G",
      memory_per_gpu: "10G",
      memory: "50G",
      gpus: 20,
      gpus_per_node: 20,
      gpus_per_socket: 20,
      gpus_per_task: 20,
      time: "10:00:00",
    };

This provides global caps for SLURM resources. We use these default ceiling values because we allow many outside of our lab to utilize our CyberGIS-Compute Core server. If your CyberGIS-Compute Core server is limited to only trusted users (i.e. if only trusted users have access to your JupyterHub), you can safely increase these values.

Data Limitations
^^^^^^^^^^^^^^^^

There are a few practical limitations when it comes to dealing with big data.

* Models are stored in Github which provides a limitation on the data size stored there. 
* Data transfers from the user to the HPC are limited by a few bottlenecks:
    * Globus transfers for very large amounts of data will add additional time to running a model because data transfers must complete before a job can run. 
    * HPCs generally limit your data storage capacity, but generally CyberGIS-Compute Core is configured to download this data to scratch (temporary storage) directories which have looser restrictions with the understanding that the data may be removed without notice in the future.


There are a few simple workarounds:
    * **For Model Developers:** One simple workaround for model developers is to have your first stage of a model download any necessary data.
    * **For Core Server Admins:** You can store big data on HPC systems and configure additional mounts for model containers on the `by-HPC basis <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/configs/hpc.example.json#L25>`__ or the `by-container basis <https://github.com/cybergis/cybergis-compute-core/blob/v2.2/configs/container.example.json#L11>`__. This eliminates the need to store duplicate copies of data and the time needed to transfer the data when a model is run.


Known Issues
------------

The CyberGIS-Compute Core server has a few known issues that can cause crashes/jobs to fail silently.

Connection Issues 
^^^^^^^^^^^^^^^^^

Occasionally, the Core server will run into intermittent connection issues when attempting to connect to HPCs causing a crash. A fix for this is currently being developed. You can leave additional feedback on `Issues #85 <https://github.com/cybergis/cybergis-compute-core/issues/85>`__.

Globus Server Down/Failing
^^^^^^^^^^^^^^^^^^^^^^^^^^

If a job has been stuck in the ``JOB_REGISTERED`` stage or results take a very long time to download, we recommend checking the Globus server for the appropriate JupyterHub/HPC for errors. Errors in Globus are outside of the CyberGIS-Compute Core codebase.