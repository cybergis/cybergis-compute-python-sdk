# Job Supervisor Python SDK
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

2. Create A User Object

> 👩‍💻 A user owns HPC jobs on the Job Supervisor, certified by a `secretToken`. 
> 
> A `User` object interface can submit new jobs or create `Job` objects for already submitted jobs. There are several ways to initialize an `User` object interface. 
```python
from job_supervisor_client import *

# create a new user object

# 1. init user using community account
destinationName = "summa" # can fetch from User.destinations()
communitySummaUser = User(destinationName)

# 2. init user using personal account
personalSummaUser = User('summa', user="zimox2", password="password")
```
> ⚠️ For security reasons, after initialization, this SDK will generate a `job_supervisor_constructor_*.json ` constructor file that can be used to recreate the same `User` object. 
> 
> After initializing a new user, please change your code to use the constructor file for regenerating the `User` object, especially when you entered your personal account's password. 

```python
# 3. recreate the User object using constructor file
recreatedSummaUser = User('summa', useFileConstructor=True)
```

```python
# other options:

# Jupyter styling options
demoUser = User('spark', isJupyter=True, useFileConstructor=True)

# change Job Supervisor server destination
demoUser = User('spark', url="localhost", port=3000, useFileConstructor=True)

# other usages:

# fetch events/logs all running jobs under this user
demoUser.events()
demoUser.logs()

# fetch destination information
demoUser.destinations()
```

3. Initialize A Job
```python
# create a new job
demoJob = demoUser.job()

# if a job is already submitted to the Job Supervisor server
# enter its JobID to recreate the same job
# you can check all your jobs using User.events()
recreateJob = demoUser.job("1599621894O9Op")
```

4. Upload Your Code/Model
> 📃 Please place all your files under a folder. Different destinations (services) have different requirements for uploaded files. You can use `User.destinations()` to check upload requirements.

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