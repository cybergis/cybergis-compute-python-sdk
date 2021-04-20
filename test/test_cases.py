from job_supervisor_client import Session


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
