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

2. Initialize a Job
```python
from job_supervisor_client import *

# init job using community account
communitySummaJob = Job('summa')

# init job using personal account
personalSummaJob = Job('summa', user="zimox2", password="password")

# set job submission destination
summaJob = Job('summa', url="localhost", port=3000)

# if a job is already submitted, you can initialize 
```

3. Submit Job
```python
summaJob.submit(env={
    A: 1,
    B: 2
}, payload={
    examplePayload: "123"
})
```

4. Query Job Events
```python
# onetime check
result = summaJob.events()

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
summaJob.events(liveOutput=True)

"""
 types                      | message                                                                            | time
----------------------------+------------------------------------------------------------------------------------+--------------------------
 JOB_QUEUED                 | job [1597698079eu9N] is queued, waiting for registration                           | 2020-08-17T21:01:19.081Z
"""
```

5. Download Job Output as Zip File
```python
summaJob.download(dir='/dir/to/download')
```