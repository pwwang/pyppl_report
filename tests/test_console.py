import sys
import cmdy
import pytest
from pathlib import Path
from pyppl import config_plugins
import pyppl_report
config_plugins(pyppl_report)
from pyppl import console
from pyparam import commands
HERE = Path(__file__).resolve().parent

@pytest.fixture
def infile():
	return HERE / 'rel_template.md'

def run_report(**opts):
	commands.report.filter.value = False
	sys.argv = ['pyppl', 'report'] + sum([[('-' if len(key) == 1 else '--')  + key, str(val)] for key, val in opts.items()], [])
	console.main()

def test_avoid_input_overwriting(infile):
	before = infile.read_text()
	run_report(i = infile)
	assert infile.read_text() == before
	assert infile.with_suffix('.tmp.md').exists()
	assert infile.with_suffix('.html').exists()
	infile.with_suffix('.tmp.md').unlink()
	infile.with_suffix('.html').unlink()

def test_only_html_pdf(tmp_path, infile):
	with pytest.raises(ValueError):
		run_report(i = infile, o = str(tmp_path.with_suffix('.xyz')))

def test_pdf(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	run_report(i = infile, o = outfile)
	assert outfile.exists()

def test_returncode(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	with pytest.raises(SystemExit):
		run_report(i = infile, o = outfile, filter = '__notexist__')

def test_nonstand_pdf(tmp_path, infile):
	outfile = tmp_path.with_suffix('.pdf')
	with pytest.raises(ValueError):
		run_report(i = infile, n = True, o = outfile)

def test_nonstand(tmp_path, infile):
	outfile = tmp_path.with_suffix('.html')
	run_report(i = infile, n = True, o = outfile)
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
	run_report(i = infile2, n = True, o = outfile2)
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
