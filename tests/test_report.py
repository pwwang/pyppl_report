import pytest
from pyppl import PyPPL, Proc
from os import environ
environ['PYPPL_default__plugins'] = 'py:["pyppl-report"]'

@pytest.fixture
def proc():
	p = Proc()

def test_basic(proc, tmp_path):

	PyPPL().start(proc).run().report(outfile = str(tmp_path / 'pyppl-report-test-basic.html'))
