import io
import sys
import os
from unittest.mock import patch
import pytest
import socket

from cybergis_compute_client.CyberGISCompute import *
from cybergis_compute_client.Job import *
from cybergis_compute_client.Zip import *

"""
Ensures zipping is working as intended
"""
def test_Zip():
    zip = Zip()
    zip.mkdir('x')
    b1 = zip.read()
    zip.append('x','1')
    b2 = zip.read()
    assert (len(b2) - len(b1)) == 81  
    zip.write('y')
    assert len(open('y','rb').read()) == len(zip.read())
    os.remove("y")

"""
Confirms that without necessary information, socket exceptions occur
"""
def test_CyberGISCompute():
    destination_Name = "summa"  # can fetch from Session.destinations()
    community_Summa_Session = CyberGISCompute(destination_Name)
    community_Summa_Session.jupyterhubApiToken="xxxxxxx"
    assert isinstance(community_Summa_Session, CyberGISCompute)
    assert community_Summa_Session.job == None
    assert community_Summa_Session.client.url == 'summa:443'
    assert community_Summa_Session.client.protocol == 'HTTPS'
    assert community_Summa_Session.isJupyter == True
    assert community_Summa_Session.recentDownloadPath == None

    # Checks that output is being returned
    with patch("cybergis_compute_client.CyberGISCompute.login") as patched_function:
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

    # Checks that socket exception is occuring
    with pytest.raises(Exception) as exc_info:
        community_Summa_Session.list_info()
    exception_raised = exc_info.value
    assert isinstance(exception_raised,socket.gaierror)

   
    # Checks that socket exception is occuring
    with pytest.raises(Exception) as exc_info:
        community_Summa_Session.get_job_by_id()
    exception_raised = exc_info.value
    assert isinstance(exception_raised,socket.gaierror)

    
    # Checks that socket exception is occuring
    with pytest.raises(Exception) as exc_info:
        community_Summa_Session.create_job()
    exception_raised = exc_info.value
    assert isinstance(exception_raised,socket.gaierror) 
