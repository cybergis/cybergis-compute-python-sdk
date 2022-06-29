import io
import sys
import os
from unittest.mock import patch
import pytest
import socket

from cybergis_compute_client.CyberGISCompute import *
from cybergis_compute_client.Job import *
from cybergis_compute_client.GlobusUtil import *
from cybergis_compute_client.Zip import *

def test_Session_event(mocker):
    mocker.patch(
        'cybergis_compute_client.Job.status',
        return_value={'events': {'new_event': 'my_event'}, 'logs': {}}
    )

    expected_failure = {'events': {}, 'logs': {}}
    expected_pass = {'new_event': 'my_event'}
    destination_Name = "summa"  # can fetch from Session.destinations()
    community_Summa_Session = CyberGISCompute(destination_Name)
    actual = community_Summa_Session.job()
    # assert expected_failure == actual
    assert expected_pass == actual

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

def test_CyberGISCompute():
    destination_Name = "summa"  # can fetch from Session.destinations()
    community_Summa_Session = CyberGISCompute(destination_Name)
    assert isinstance(community_Summa_Session, CyberGISCompute)
    assert community_Summa_Session.job == None
    assert community_Summa_Session.client.url == 'summa:443'
    assert community_Summa_Session.client.protocol == 'HTTPS' 
    assert community_Summa_Session.jupyterhubApiToken == None
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


def test_Session_destinations():
    with patch("cybergis_compute_client.Client.request") as patched_function:
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        patched_function.return_value = {'destinations': {
            'summa': {'ip': 'keeling.earth.illinois', 'port': 22, 'maintainer': 'SUMMAMaintainer', 'jobPoolCapacity': 20,
                      'isCommunityAccount': True, 'useUploadedFile': True,
                      'uploadFileConfig': {'ignore': [], 'mustHave': ['summa_options.json', 'installTestCases_local.sh',
                                                                      'data', 'output', 'settings'],
                                           'ignoreEverythingExceptMustHave': True}}}}

        destination_Name = "summa"
        community_Summa_Session = CyberGISCompute(destination_Name)
        community_Summa_Session.client

        sys.stdout = sys.__stdout__  # Reset redirect.
        std_output = capturedOutput.getvalue()
        output_message = std_output.split('\n')[2].split("|")[0].strip(" ")
        # print('Captured \n', std_output)

        assert "summa" == output_message

