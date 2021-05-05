from job_supervisor_client import *
import os
import tempfile
resource_id = '13d6b84a9553410297a67fa366a56cb2'
base_dir = os.getcwd() + '/examples'
download_dir = os.path.join(base_dir, 'Downloads')
model_folder_name = "SummaModel_ReynoldsAspenStand_StomatalResistance_sopron"
workspace_dir = os.path.join(base_dir, 'workspace')
unzip_dir = os.path.join(workspace_dir, 'tmp6iw03qeg')
model_source_folder_path = os.path.join(unzip_dir, model_folder_name)

job = Job(maintainer="SUMMA", hpc="keeling_community", url="localhost", port=3000, protocol='HTTP')
job.upload(model_source_folder_path)
job.submit()
