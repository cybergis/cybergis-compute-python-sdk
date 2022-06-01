import pytest

from job_supervisor_client import UI

def test_secondsToTime():
    ui = UI()
    assert(ui.secondsToTime(5555) == '9:00')
    assert(ui.secondsToTime(5555) == '1:32:00')
    assert(ui.secondsToTime(5555555) == '64-7:12:00')

def test_unitTimeToSecond():
    ui = UI()
    assert(ui.unitTimeToSecond(12, 'Minutes') == 720)
    assert(ui.unitTimeToSecond(12, 'Hours') == 43200)
    assert(ui.unitTimeToSecond(12, 'Days') == 518400)