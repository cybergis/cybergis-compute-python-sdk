# CyberGIS-Compute Python SDK
[![PythonCodeQuality](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Quality/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)
[![PythonCodeTest](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Test/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)
![GitHub](https://img.shields.io/github/license/cybergis/cybergis-compute-python-sdk)

**CyberGIS-Compute** is a scalable middleware framework for enabling high-performance and data-intensive geospatial research and education on CyberGISX. This API can be used to send [supported jobs]() to various [supported HPC & computing resources]().

## Installation
1. **Requirements**
- Python3 + pip3
- Jupyter server (Hub/Lab) with fixed domain
- System environment variables:
  - `JUPYTERHUB_API_TOKEN`: user access token, comes with JupyterHub/Lab.
  - `JUPYTER_INSTANCE_URL`: server url


2. **Install/Update Package**
```bash
git clone https://github.com/cybergis/cybergis-compute-python-sdk.git
cd cybergis-compute-python-sdk
python3 setup.py install
```

## Hello World Example

In this example, you will be using the SDK's **Pilot UI** to run the [hello world GitHub project](https://github.com/cybergis/cybergis-compute-hello-world) on the [Keeling Computing Cluster](https://cybergis.illinois.edu/infrastructure/hpc-user-guide/). 

1. Run the **Pilot UI**
```python
from cybergis_compute_client import CyberGISCompute

cybergis = CyberGISCompute(url="xxx") # replace xxx with CyberGIS-Compute server url
cybergis.create_job_by_ui() # run Pilot UI
```

2. Select `hello world` from **📦 Job Template**
3. Select `keeling_community` from **🖥 Computing Recourse**
4. Configure the following, or leave it as default
	- Slurm Computing Configurations
	- Input Parameters
	- Receive Email
5. Select a file to upload under **Upload Data**
6. Click Submit

> ❓ If you wonder where does the customized configuration options comes from, they are defined in the `manifest.json` file of each project. Please refer to https://github.com/cybergis/cybergis-compute-hello-world/blob/main/manifest.json

## SDK Usage
```python
cybergis = CyberGISCompute(url="xxx")
```

1. Query and resume jobs that you own. 
```python
# CyberGISCompute.list_job -> return a list of jobs that you submitted
cybergis.list_job()

# CyberGISCompute.get_job_by_id -> return a Job object referred by that id
cybergis.get_job_by_id(id)
```

2. Query CyberGIS-Compute server support information
```python
# CyberGISCompute.list_hpc -> return a list of hpc resources that the server supports
cybergis.list_hpc()

# CyberGISCompute.list_git -> return a list of Git projects that the server supports
cybergis.list_git()
```



# Job Supervisor Python SDK

[![PythonCodeQuality](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Quality/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)
[![PythonCodeTest](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Test/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)
![GitHub](https://img.shields.io/github/license/cybergis/cybergis-compute-python-sdk)

RIF meeting iPyWidget demo notebooks: [Open With CyberGISX](https://cybergisx.cigi.illinois.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fcybergis%2Fcybergis-compute-python-sdk&branch=v2&urlpath=tree%2Fcybergis-compute-python-sdk%2FRIF_UI_NBK%2FiPython%20Widget.ipynb)

Python SDK client for submitting HPC job to CyberGIS Job Supervisor

## Basic Usage
0. Requirements
- Python3 + pip3

1. Install Package
```bash
git clone https://github.com/cybergis/cybergis-compute-python-sdk.git
cd cybergis-compute-python-sdk
python3 setup.py install
```

2. Create A Session Object

> 👩‍💻 A session owns HPC jobs on the Job Supervisor, certified by a `secretToken`. 
> 
> A `Session` object interface can submit new jobs or create `Job` objects for already submitted jobs. There are several ways to initialize a `Session` object interface. 
```python
from job_supervisor_client import *

# create a new Session object

# 1. init session using community account
destinationName = "summa" # can fetch from Session.destinations()
communitySummaSession = Session(destinationName)

# 2. init session using personal account
personalSummaSession = Session('summa', user="zimox2", password="password")
```
> ⚠️ For security reasons, after initialization, this SDK will generate a `job_supervisor_constructor_*.json ` constructor file that can be used to recreate the same `Session` object. 
> 
> After initializing a new session, please change your code to use the constructor file for regenerating the `Session` object, especially when you entered your personal account's password. 

```python
# 3. recreate the Session object using constructor file
recreatedSummaSession = Session('summa', useFileConstructor=True)
```

```python
# other options:

# Jupyter styling options
demoSession = Session('spark', isJupyter=True, useFileConstructor=True)

# change Job Supervisor server destination
demoSession = Session('spark', url="localhost", port=3000, useFileConstructor=True)

# other usages:

# fetch events/logs all running jobs under this Session
demoSession.events()
demoSession.logs()

# fetch destination information
demoSession.destinations()
```

3. Initialize A Job
```python
# create a new job
demoJob = demoSession.job()

# if a job is already submitted to the Job Supervisor server
# enter its JobID to recreate the same job
# you can check all your jobs using Session.events()
recreateJob = demoSession.job("1599621894O9Op")
```

4. Upload Your Code/Model
> 📃 Please place all your files under a folder. Different destinations (services) have different requirements for uploaded files. You can use `Session.destinations()` to check upload requirements.

```python
folder_path = '/path/to/your/file_folder'
demoJob.upload(folder_path)
```

1. Submit A New Job
```python
# simple submission
demoJob.submit()

# full submission
demoJob.submit(env={
    A: 1,
    B: 2
}, payload={
    examplePayload: "123"
})
```

4. Query Job Events
```python
# onetime check
events = demoJob.events()
logs = demoJob.logs()

"""
result returns an array of events, example:
[
	{
		'type': 'JOB_QUEUED',
		'message': 'job [1597698079eu9N] is queued, waiting for registration',
		'at': '2020-08-17T21:01:19.081Z'
	},
    ...
]
"""

# live output
demoJob.events(liveOutput=True)

"""
 types                      | message                                                                            | time
----------------------------+------------------------------------------------------------------------------------+--------------------------
 JOB_QUEUED                 | job [1597698079eu9N] is queued, waiting for registration                           | 2020-08-17T21:01:19.081Z
"""

demoJob.logs(liveOutput=True)
```

5. Download Job Output as Zip File
```python
demoJob.download(dir='/dir/to/download_folder')
```
