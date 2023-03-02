import pytest

from cybergis_compute_client import UI
from cybergis_compute_client import CyberGISCompute
cybergis = CyberGISCompute(url="cgjobsup.cigi.illinois.edu", isJupyter=True, protocol="HTTPS", port=443, suffix="v2")

"""
Tests that seconds are being converted to days/hours/minutes correctly
"""
def test_secondsToTime():
    ui = UI.UI(cybergis)
    assert(ui.secondsToTime(555) == '09:00')
    assert(ui.secondsToTime(5555) == '01:32:00')
    assert(ui.secondsToTime(5555555) == '64-07:12:00')

"""
Tests that days/hours/minutes are being converted to secornds properly
"""
def test_unitTimeToSecond():
    ui = UI.UI(cybergis)
    assert(ui.unitTimeToSecond('Minutes', 12) == 720)
    assert(ui.unitTimeToSecond('Hours', 12) == 43200)
    assert(ui.unitTimeToSecond('Days', 12) == 1036800)

"""
Ensures that common malicious file names are removed and that input strings are formatted correctly for folder naming
"""
def test_makeNameSafe():
    ui = UI.UI(cybergis)
    assert(ui.makeNameSafe(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~') == '.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz')
    assert(ui.makeNameSafe('test123') == 'test123')
    assert(ui.makeNameSafe('') == '')
    assert(ui.makeNameSafe('TeSt1!2@3#') == 'TeSt123')
    assert(ui.makeNameSafe('test_123') == 'test_123')
    assert(ui.makeNameSafe('ЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя') == 'ЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя')
    assert(ui.makeNameSafe('\' rm *') == 'rm')
    assert(ui.makeNameSafe('.txt rm *') == '.txtrm')