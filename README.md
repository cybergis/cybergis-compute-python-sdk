# CyberGIS-Compute Python SDK

![GitHub](https://img.shields.io/github/license/cybergis/cybergis-compute-python-sdk)
[![Docs](https://img.shields.io/badge/docs-site-blueviolet)](https://cybergis.github.io/cybergis-compute-python-sdk/reference.html)
[![PyPi Status](https://img.shields.io/pypi/v/cybergis-compute-client)](https://pypi.org/project/cybergis-compute-client/)

[![Docs Deployed](https://github.com/cybergis/cybergis-compute-python-sdk/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions/workflows/pages/pages-build-deployment)
[![PythonCodeQuality](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Quality/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)
[![PythonCodeTest](https://github.com/cybergis/cybergis-compute-python-sdk/workflows/Python%20Code%20Test/badge.svg)](https://github.com/cybergis/cybergis-compute-python-sdk/actions)

**CyberGIS-Compute** is a scalable middleware framework for enabling high-performance and data-intensive geospatial research and education on CyberGISX. This API can be used to send [supported jobs](https://github.com/cybergis/cybergis-compute-core#supported-git-projects) to various [supported HPC & computing resources](https://github.com/cybergis/cybergis-compute-core#supported-hpc--computing-resources).

***

## Installation

**Requirements**
- Python3 + pip3
- Jupyter server (Hub/Lab) with fixed domain
- System environment variables:
  - `JUPYTERHUB_API_TOKEN`: user access token, comes with JupyterHub/Lab.
  - `JUPYTER_INSTANCE_URL`: server url

From Pip:

```bash
pip install cybergis-compute-client
```

From Github:

```bash
git clone https://github.com/cybergis/cybergis-compute-python-sdk.git
cd cybergis-compute-python-sdk
python3 setup.py install
```

***

## Hello World Example

In this example, you will be using the SDK's **Pilot UI** to run the [hello world GitHub project](https://github.com/cybergis/cybergis-compute-hello-world) on the [Keeling Computing Cluster](https://cybergis.illinois.edu/infrastructure/hpc-user-guide/). 

1. Run the **Pilot UI**
```python
from cybergis_compute_client import CyberGISCompute

cybergis = CyberGISCompute(url="xxx") # replace xxx with CyberGIS-Compute server url
cybergis.show_ui() # run Pilot UI
```

2. Select `hello world` from **📦 Job Template**
3. Select `keeling_community` from **🖥 Computing Resource**
4. Configure the following, or leave it as default
	- Slurm Computing Configurations
	- Input Parameters
	- Receive Email
5. Select a file to upload under **Upload Data**
6. Click Submit

> ❓ If you wonder where the customized configuration options comes from, they are defined in the `manifest.json` file of each project. Please refer to https://github.com/cybergis/cybergis-compute-hello-world/blob/main/manifest.json

***
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
# CyberGISCompute.list_hpc -> prints a list of hpc resources that the server supports
cybergis.list_hpc()

# CyberGISCompute.list_git -> prints a list of Git projects that the server supports
cybergis.list_git()
```

3. Use Pilot UI
```python
# Renders a IPython Widget UI in Jupyter (async)
# CyberGISCompute.create_job_by_ui -> return None
cybergis.show_ui()

# Get the job submitted by the UI (after you press the submit button)
# CyberGISCompute.get_latest_created_job -> return Job object
cybergis.get_latest_created_job()
```

4. Submit job using programming style (in progress)
```python
# the Job object is an interface for a job
# CyberGISCompute.create_job -> return Job object & print the job's information
job = cybergis.create_job(hpc="some HPC")

# Job.submit -> print the job's information
job.submit()
```

***

## Related Documentation and Projects
- [CyberGIS-Compute Python SDK webpage](https://cybergis.github.io/cybergis-compute-python-sdk/)
    - [Using CyberGIS-Compute](https://cybergis.github.io/cybergis-compute-python-sdk/usage.html)
    - [Hello World Notebook](https://cybergis.github.io/cybergis-compute-python-sdk/notebooks/hello_world.html)
    - [Model Gallery](https://cybergis.github.io/cybergis-compute-python-sdk/models.html)
    - [Contributing Models](https://cybergis.github.io/cybergis-compute-python-sdk/model_contribution/index.html)
- [CyberGIS Compute Core - the server](https://github.com/cybergis/cybergis-compute-core)
- [CyberGIS Compute Example Hello World Project](https://github.com/cybergis/cybergis-compute-hello-world)