Frequently Asked Questions
==========================


How does the Compute job access X?
----------------------------------

CyberGIS Compute creates a `job.json` file that includes::


    {
        "job_id": string,
        "user_id": string,
        "hpc": string,
        // user parameters input
        "param": {
            "param_a": 1,
            "param_b": "value"
        },
        "executable_folder": string, // path to the executable code
        "data_folder": string, // path to the uploaded data
        "result_folder": string // path to the download data folder
    }

You can access these parameters and values through system environment variables::

    import os
    os.environ['job_id']
    os.environ['param_param_a'] # access param['param_a']

What do the Job Events Mean?
----------------------------

The job events in the "Your Job Status" gives you real-time information on what is happening with your job. Here is a brief description on what each means:

* ``JOB_QUEUED`` means that the job has entered the CyberGIS-Compute Core's queue of jobs.
* ``JOB_REGISTERED`` means that the job has been sent to the HPC resource.
* ``GLOBUS_TRANSFER_INIT_SUCCESS`` means that we are able to transfer any uploaded data to the HPC resource with Globus.
* ``JOB_INIT`` means that the job has begun running on the HPC resource.
* ``JOB_ENDED`` means that the job has completed on the HPC resource.

Why are my Results not Downloading?
-----------------------------------

Note that CyberGIS-Compute only downloads the from the result folder. You can get the path to this with the “result_folder” environment variable (os.environ[“result_folder”] in Python).

.. tip::
    If your code doesn't allow you specify an output path for your data, a common approach is to use the post-processing script to copy whatever you need to the result folder.
