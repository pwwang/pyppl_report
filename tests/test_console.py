import cmdy
import pytest
from pathlib import Path
HERE = Path(__file__).resolve().parent
exe = str(HERE / 'pyppl_report')
cmdy.chmod('+x', exe)

@pytest.fixture
def infile():
	return HERE / 'rel_template.md'

def test_avoid_input_overwriting(infile):
	before = infile.read_text()
	cmdy.pyppl_report(i = infile, _exe = exe, _fg = True)
	assert infile.read_text() == before
	assert infile.with_suffix('.tmp.md').exists()
	assert infile.with_suffix('.html').exists()
	infile.with_suffix('.tmp.md').unlink()
	infile.with_suffix('.html').unlink()

def test_only_html_pdf(tmp_path, infile):
	with pytest.raises(cmdy.CmdyReturnCodeException):
		cmdy.pyppl_report(i = infile, o = str(tmp_path.with_suffix('.xyz')), _exe = exe, _fg = True)

def test_pdf(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	cmdy.pyppl_report(i = infile, o = outfile, _exe = exe, _raise = True, _fg = True)
	assert outfile.exists()

def test_returncode(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	with pytest.raises(cmdy.CmdyReturnCodeException):
		cmdy.pyppl_report(i = infile, o = outfile, _exe = exe, filter = '__notexist__', _raise = True, _fg = True)


