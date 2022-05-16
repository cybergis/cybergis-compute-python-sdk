import io
import sys
import pytest
from unittest.mock import patch

from job_supervisor_client import JAT

def test_parseAccessToken():
    jat = JAT()
    with pytest.raises(Exception):
        jat.parseAccessToken('a.a.a.a.a')

def test_parseAccessToken():
    jat = JAT()
    with pytest.raises(Exception):
        jat._checkInit()

def test_encodeString():
    jat = JAT()
    assert(jat._encodeString('test string') == 'dGVzdCBzdHJpbmc=')

def test__decodeString():
    jat = JAT()
    assert(jat._decodeString('dGVzdCBzdHJpbmc=') == 'test string')