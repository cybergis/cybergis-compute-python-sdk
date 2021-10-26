# Job Supervisor Python SDK

[![PythonCodeQuality](https://github.com/cybergis/job-supervisor-python-sdk/workflows/Python%20Code%20Quality/badge.svg)](https://github.com/cybergis/job-supervisor-python-sdk/actions)
[![PythonCodeTest](https://github.com/cybergis/job-supervisor-python-sdk/workflows/Python%20Code%20Test/badge.svg)](https://github.com/cybergis/job-supervisor-python-sdk/actions)
![GitHub](https://img.shields.io/github/license/cybergis/job-supervisor-python-sdk)

Python SDK client for submitting HPC job to CyberGIS Job Supervisor

## Basic Usage
0. Requirements
- Python3 + pip3

1. Install Package
```bash
git clone https://github.com/cybergis/job-supervisor-python-sdk.git
cd job-supervisor-python-sdk
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
