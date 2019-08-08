import pytest
from pyppl import PyPPL, Proc
from pyppl.exception import ProcAttributeError
from os import environ
from pathlib import Path
HERE = Path(__file__).resolve().parent

@pytest.fixture
def proc():
	return Proc().copy()

@pytest.fixture
def reportfile(tmp_path):
	return tmp_path / 'pyppl-report-test.report.html'

def assertInfile(file, *strings):
	content = file.read_text()
	for string in strings:
		assert string in content
		content = content[content.find(string) + len(string):]

def test_basic(proc, reportfile):
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile, 'A report generated by pipeline powered by PyPPL')

def test_title(proc, reportfile):
	PyPPL().start(proc).run().report(outfile = reportfile, title = 'Test title')
	assertInfile(reportfile, 'Test title')

def test_template_abs(proc, reportfile, tmp_path):
	tplfile = tmp_path / 'pyppl-report-test-template.md'
	tplfile.write_text('# Hello world')
	proc.report = 'file:%s' % tplfile
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile, '<h2 id="hello-world">Hello world</h2>')

def test_template_nonexist(proc, reportfile):
	with pytest.raises(ProcAttributeError):
		proc.report = 'file:__NonExistFile__'

def test_template_rel(proc, reportfile):
	proc.report = 'file:rel_template.md'
	proc.envs.report.level = 3
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile, '<h3 id="a-relative-path-template">A relative path template</h3>')

def test_template_extradata(proc, reportfile):
	proc.input = {'a': ['1']}
	proc.script = 'echo "mark: special job{{job.index}}" > {{job.outdir}}/job.report.data.yaml'
	proc.report = '{{jobs[0].mark}}'
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile, '<p>special job0</p>')

def test_coded_heading(proc, reportfile):
	proc.report = '''
# Level2
```
# Level1
```
'''
	proc.envs.report.level = 2
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile, '<h2 id="level2">Level2</h2>', '<code># Level1</code>')

def test_pandoc_cmderror(proc):
	with pytest.raises(SystemExit):
		PyPPL().start(proc).run().report(template = 'nonexist')
	from glob import glob
	assert glob('./pytest.*.report.md')
	for rmd in glob('./pytest.*.report.md'):
		Path(rmd).unlink()
	assert not glob('./pytest.*.report.md')

def test_appendix(proc, reportfile):
	proc.report = '''
# Title
Some results

## Appendix
### Full detail
Some table

'''
	p2 = Proc()
	p2.depends = proc
	p2.report = '''
# Title2
Some other results

## Appendix
### Full detail2
Some other table
'''
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile,
		'<h2 id="title">Title</h2>',
		'<p>Some results</p>',
		'<h2 id="title2">Title2</h2>',
		'<p>Some other results</p>',
		'<h2 id="appendix">Appendix</h2>',
		'<h3 id="full-detail">Full detail</h3>',
		'<p>Some table</p>',
		'<h3 id="full-detail2">Full detail2</h3>',
		'<p>Some other table</p>',
	)

def test_citations(proc, reportfile):
	proc.report = '''
# Title
Some results[1]

Some[8] reports[2]

## Appendix
Some more results[3]

[1]: paper1
[2]: paper2
[3]: paper3
'''
	p3 = Proc()
	p3.depends = proc
	p3.report = '''
# Title2
Some other results[1]

Some repeated results[2]

[1]: paper4
[2]: paper2
'''
	PyPPL().start(proc).run().report(outfile = reportfile)
	assertInfile(reportfile,
		'<h2 id="title">Title</h2>',
		'<p>Some results<sup><a href="#REF_1">[1]</a></sup>',
		'<p>Some[8] reports<sup><a href="#REF_2">[2]</a></sup>',
		'<h2 id="title2">Title2</h2>',
		'<p>Some other results<sup><a href="#REF_4">[4]</a></sup>',
		'<p>Some repeated results<sup><a href="#REF_2">[2]</a></sup>',
		'<h2 id="appendix">Appendix</h2>',
		'<p>Some more results<sup><a href="#REF_3">[3]</a></sup>',
		'<h2 id="reference">Reference</h2>',
		'<p><a name="REF_1" class="reference"><strong>[1]</strong> paper1</a></p>',
		'<p><a name="REF_2" class="reference"><strong>[2]</strong> paper2</a></p>',
		'<p><a name="REF_3" class="reference"><strong>[3]</strong> paper3</a></p>',
		'<p><a name="REF_4" class="reference"><strong>[4]</strong> paper4</a></p>',
	)

## Test report.py
@pytest.fixture
def report():
	module = __import__('pyppl-report', fromlist = ['report'])
	return module.report

@pytest.mark.parametrize('regex,callback,string,expect', [
	(r'\d+', lambda x: str(int(x) + 1), 'a1b1c2', 'a2b2c3'),
	(r'\d+', lambda x: str(int(x) + 1), 'aabbcc', 'aabbcc'), # no matches
	(r'\w(\d+)', lambda x, y: x+str(int(y) + 1), 'a1b1c2', 'a12b12c23'),
])
def test_report_replaceall(regex, callback, string, expect, report):
	assert report._replaceAll(regex, callback, string) == expect

## Front-end functions
def test_tabs(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(3) %}
::: {.tab}

content{{i}}
:::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_collapse(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(10) %}
::: {.tab}

content{{i}}
:::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_tabs_in_tabs(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(3) %}
:::: {.tab}
## Tab{{i}}

::: {.tab}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.tab}
### subtab2_{{i}}

content2_{{i}}
:::

::::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_collapses_in_tabs(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(3) %}
:::: {.tab}
## Tab{{i}}

::: {.tab}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.tab}
### subtab2_{{i}}

content2_{{i}}
:::

::: {.tab}
### subtab3_{{i}}

content3_{{i}}
:::

::: {.tab}
### subtab4_{{i}}

content4_{{i}}
:::

::::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_tabs_in_collapses(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(5) %}
:::: {.tab}
## Tab{{i}}

::: {.tab}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.tab}
### subtab2_{{i}}

content2_{{i}}
:::

::::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_collapses_in_collapses(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(5) %}
:::: {.tab}
## Tab{{i}}

::: {.tab}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.tab}
### subtab2_{{i}}

content2_{{i}}
:::

::: {.tab}
### subtab3_{{i}}

content3_{{i}}
:::

::: {.tab}
### subtab4_{{i}}

content4_{{i}}
:::

::::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_force_collapses(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(3) %}
::: {.tab .force-collapse}

content{{i}}
:::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_filetable(proc, reportfile):
	proc.report = '''
```table
file: %s/filetable.txt
caption: Sample table
header: true
width: 1
total_width: .8
align: default
rows: 0
cols: 0
datatable:
	page-length: 5
```
''' % HERE
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_force_tabs(proc, reportfile):
	proc.report = '''
# Title
{% for i in range(6) %}
::: {.tab .force-tab}

content{{i}}
:::
{% endfor %}
'''
	PyPPL().start(proc).run().report(outfile = reportfile)

def test_modals(proc, reportfile):
	proc.report = '''
# Title
Click [here](modal#detailinfo) for details.

{# size: default, small, large, xlarge #}
::: {.modal id="detailinfo" title="Detailed information" closebtn="true" size="xlarge"}
```table
file: %s/filetable.txt
caption: Sample table
header: true
width: 1
total_width: .8
align: default
rows: 10
cols: 0
csvargs:
	dialect: unix
	#delimiter: "	"
```

![](%s/snapshot.png)
:::
''' % (HERE, HERE)
	PyPPL().start(proc).run().report(outfile = reportfile)


