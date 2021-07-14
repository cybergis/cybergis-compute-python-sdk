import io
import sys
from unittest.mock import patch

from job_supervisor_client import Session, Job


def test_Session_event(mocker):
    mocker.patch(
        'job_supervisor_client.Session.status',
        return_value={'events': {'new_event': 'my_event'}, 'logs': {}}
    )

    expected_failure = {'events': {}, 'logs': {}}
    expected_pass = {'new_event': 'my_event'}
    destination_Name = "summa"  # can fetch from Session.destinations()
    community_Summa_Session = Session(destination_Name)
    actual = community_Summa_Session.events()
    # assert expected_failure == actual
    assert expected_pass == actual


def test_Session_job():
    destination_Name = "summa"  # can fetch from Session.destinations()
    community_Summa_Session = Session(destination_Name)
    actual = community_Summa_Session.job()
    assert isinstance(actual, Job)


def test_Session_destinations():
    with patch("job_supervisor_client.Client.request") as patched_function:
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        patched_function.return_value = {'destinations': {
            'summa': {'ip': 'keeling.earth.illinois', 'port': 22, 'maintainer': 'SUMMAMaintainer', 'jobPoolCapacity': 20,
                      'isCommunityAccount': True, 'useUploadedFile': True,
                      'uploadFileConfig': {'ignore': [], 'mustHave': ['summa_options.json', 'installTestCases_local.sh',
                                                                      'data', 'output', 'settings'],
                                           'ignoreEverythingExceptMustHave': True}}}}

        destination_Name = "summa"
        community_Summa_Session = Session(destination_Name)
        community_Summa_Session.destinations()

        sys.stdout = sys.__stdout__  # Reset redirect.
        std_output = capturedOutput.getvalue()
        output_message = std_output.split('\n')[2].split("|")[0].strip(" ")
        # print('Captured \n', std_output)

        assert "summa" == output_message
