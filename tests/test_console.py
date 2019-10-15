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

def test_nonstand_pdf(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	with pytest.raises(cmdy.CmdyReturnCodeException):
		cmdy.pyppl_report(i = infile, n = True, o = outfile, _exe = exe, _raise = True, _fg = True)

def test_nonstand(tmp_path, infile):
	outfile = tmp_path.with_suffix('.html')
	cmdy.pyppl_report(i = infile, n = True, o = outfile, _exe = exe, _raise = True, _fg = True)
	assert outfile.parent.joinpath('__common__.files').is_dir()
	assert outfile.parent.joinpath('__common__.files').joinpath('css').is_dir()
	assert outfile.parent.joinpath('__common__.files').joinpath('js').is_dir()
	assert outfile.parent.joinpath('__common__.files').joinpath('css', 'template.css').is_file()
	assert outfile.parent.joinpath('__common__.files').joinpath('js', 'template.js').is_file()

	outfile2 = tmp_path.with_name('nonstand_outfile.html')
	infile2 = tmp_path.with_name('nonstand_outfile.md')
	infile2.write_text('''# Title
```table
file: {0}
caption: filetable
rows: 5
dtargs: false
header: false
```

```table
caption: filetable
header: true
csvargs:
	delimiter: ','
---
a,b
a1,1,1
a2,2,2
```

[Download filetable]({0} "file-download")
'''.format(HERE/'filetable.txt'))
	cmdy.pyppl_report(i = infile2, n = True, o = outfile2,  _exe = exe, _raise = True, _fg = True)
	assert outfile2.with_suffix('.files').is_dir()
	assert outfile2.with_suffix('.files').joinpath('filetable.txt').is_file()

def test_copyfile(tmp_path):
	from pyppl_report.resources.filters import nonstand
	tmpdir = tmp_path.with_suffix('.dir')
	tmpdir.mkdir()
	srcfile = tmpdir / 'srcfile'
	dstfile = tmpdir / 'dstfile'
	srcfile.write_text('')
	nonstand._copyfile(srcfile, dstfile)
	assert dstfile.is_file()

	srcfile2 = tmpdir / 'srcfile2'
	srcfile2.write_text('2')
	assert nonstand._copyfile(srcfile2, dstfile) == tmpdir / '[1]dstfile'
	assert tmpdir.joinpath('[1]dstfile').is_file()

	srcfile3 = tmpdir / 'srcfile3'
	srcfile3.write_text('3')
	assert nonstand._copyfile(srcfile3, dstfile) == tmpdir / '[2]dstfile'
	assert tmpdir.joinpath('[2]dstfile').is_file()
