import pytest
from pyppl import PyPPL, Proc
from pyppl.exception import ProcessAttributeError
from os import environ
from pathlib import Path
HERE = Path(__file__).resolve().parent

@pytest.fixture
def proc(tmp_path):
    return Proc(input = {'a:var':[0]}, output = 'a:var:0', ppldir = tmp_path/'workdir').copy()

@pytest.fixture
def reportfile(tmp_path):
    return tmp_path / 'pyppl_report-test.report.html'

def assert_in_file(file, *strings):
    content = file.read_text()
    for string in strings:
        assert string in content
        content = content[content.find(string) + len(string):]

def test_basic(proc, reportfile):
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, 'Reports for ')

def test_nosuch_template(proc, reportfile, tmp_path):
    ppl = PyPPL(forks=5).start(proc).run()
    tmpdir = tmp_path.joinpath('nosuchstatic')
    tmpdir.mkdir(exist_ok=True)
    tmpdir.joinpath('template.html').write_text('')
    with pytest.raises(ValueError):
        ppl.report(outfile = reportfile, standalone=False, template=str(tmpdir.joinpath('template.html')))

def test_unlink_prev_report(proc, reportfile):
    proc.config.report_template = '# Report'
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert proc.workdir.joinpath('proc.report.md').is_file()
    assert_in_file(reportfile, 'Reports for ')

    procX = proc.copy()
    procX.workdir = proc.workdir
    procX.config.report_template = False
    PyPPL(forks=5).start(procX).run().report(outfile = reportfile)
    assert not procX.workdir.joinpath('proc.report.md').is_file()

def test_report_cached(proc, reportfile, caplog):
    proc.config.report_template = '# Report'
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    caplog.clear()

    procX = proc.copy(id = proc.id, tag='another')
    procX.workdir = proc.workdir
    procX.tag = proc.tag
    PyPPL(forks=5).start(procX).run().report(outfile = reportfile)
    assert 'Report markdown file cached, skip.' in caplog.text


def test_outfile_default(proc):
    ppl = PyPPL(forks=5).start(proc).run().report()
    reportfile = Path('.').joinpath('%s.report.html' % ppl.name)
    assert_in_file(reportfile, 'Reports for ')
    reportfile.with_suffix('.tmp.md').unlink()
    reportfile.unlink()

def test_title(proc, reportfile):
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile, title = 'Test title')
    assert_in_file(reportfile, 'Test title')

def test_template_abs(proc, reportfile, tmp_path):
    tplfile = tmp_path / 'pyppl_report-test-template.md'
    tplfile.write_text('# Hello world')
    proc.config.report_template = 'file:%s' % tplfile.resolve()
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, '<h1 id="hello-world">Hello world</h1>')

def test_template_rendererror(proc, reportfile, tmp_path):
    tplfile = tmp_path / 'pyppl_report-test-template.md'
    tplfile.write_text('# Hello world {{ x }}')
    proc.config.report_template = 'file:%s' % tplfile
    with pytest.raises(RuntimeError):
        PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_template_nonexist(proc, reportfile):
    with pytest.raises(ProcessAttributeError):
        proc.config.report_template = 'file:__NonExistFile__'

def test_template_rel(proc, reportfile):
    proc.config.report_template = 'file:data/rel_template.md'
    proc.config.report_envs.level = 3
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, '<h3 id="a-relative-path-template">A relative path template</h3>')

def test_template_extradata(proc, reportfile):
    proc.input = {'a': ['1']}
    proc.script = 'echo -e "mark = \'special job{{job.index}}\'" > {{job.outdir}}/job.report.data.toml'
    proc.config.report_template = '{{jobs[0].mark}}'
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, '<p>special job0</p>')

def test_coded_heading(proc, reportfile):
    proc.config.report_template = '''
# Level2
```
# Level1
```
'''
    proc.config.report_envs.level = 2
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, '<h2 id="level2">Level2</h2>', '<code># Level1</code>')

def test_pandoc_cmderror(proc, tmp_path):
    ppl = PyPPL(forks=5).start(proc).run()
    with pytest.raises(SystemExit):
        ppl.report(outfile = tmp_path, template = 'nonexist')
    assert tmp_path.joinpath('%s.report.tmp.md' % ppl.name).is_file()

# def test_appendix(proc, reportfile, tmp_path):
#     proc.config.report_template = '''
# # Title
# Some results

# ## Appendix
# ### Full detail
# Some table

# '''
#     p2 = Proc(input = {'a:var':[0]}, output = 'a:var:0', ppldir = tmp_path/'workdir')
#     p2.depends = proc
#     p2.config.report_template = '''
# # Title2
# Some other results

# ## Appendix
# ### Full detail2
# Some other table
# '''
#     PyPPL(logger_level = 'debug').start(proc).run().report(outfile = reportfile)
#     assert_in_file(reportfile,
#         '<h2 id="title">Title</h2>',
#         '<p>Some results</p>',
#         '<h2 id="title2">Title2</h2>',
#         '<p>Some other results</p>',
#         '<h2 id="appendix">Appendix</h2>',
#         '<h3 id="full-detail">Full detail</h3>',
#         '<p>Some table</p>',
#         '<h3 id="full-detail2">Full detail2</h3>',
#         '<p>Some other table</p>',
#     )

def test_citations(proc, reportfile, tmp_path):
    proc.config.report_template = '''
# Title
Some results[1]

Some[8] reports[2]

## Appendix
Some more results[3]

[1]: paper1
[2]: paper2
[3]: paper3
'''
    p3 = Proc(input = {'a:var':[0]}, output = 'a:var:0', ppldir = tmp_path/'workdir')
    p3.depends = proc
    p3.config.report_template = '''
# Title2
Some other results[1]

Some repeated results[2]

[1]: paper4
[2]: paper2
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile,
        '<h1 id="title">Title</h1>',
        '<p>Some results<a href="#PYPPL-REF-1" class="pyppl-report-refindex">[1]</a></p>',
        '<p>Some[8] reports<a href="#PYPPL-REF-2" class="pyppl-report-refindex">[2]</a></p>',
        '<h2 id="appendix">Appendix</h2>',
        '<p>Some more results<a href="#PYPPL-REF-3" class="pyppl-report-refindex">[3]</a></p>',
        '<h1 id="title2">Title2</h1>',
        '<p>Some other results<a href="#PYPPL-REF-4" class="pyppl-report-refindex">[4]</a></p>',
        '<p>Some repeated results<a href="#PYPPL-REF-2" class="pyppl-report-refindex">[2]</a></p>',
        '<h1 id="reference">Reference</h1>',
        '[1]: <a href class="pyppl-report-reference" name="PYPPL-REF-1">paper1</a>',
        '[2]: <a href class="pyppl-report-reference" name="PYPPL-REF-2">paper2</a>',
        '[3]: <a href class="pyppl-report-reference" name="PYPPL-REF-3">paper3</a>',
        '[4]: <a href class="pyppl-report-reference" name="PYPPL-REF-4">paper4</a>',
    )

## Test report.py

@pytest.mark.parametrize('regex,callback,string,expect', [
    (r'\d+', lambda x: str(int(x) + 1), 'a1b1c2', 'a2b2c3'),
    (r'\d+', lambda x: str(int(x) + 1), 'aabbcc', 'aabbcc'), # no matches
    (r'\w(\d+)', lambda x, y: x+str(int(y) + 1), 'a1b1c2', 'a12b12c23'),
])
def test_report_replaceall(regex, callback, string, expect):
    from pyppl_report.report import _replace_all
    assert _replace_all(regex, callback, string) == expect

## Front-end functions
def test_tabs(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(3) %}
::: {.panel}

content{{i}}
:::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_collapse(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(10) %}
::: {.panel}

content{{i}}
:::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_tabs_in_tabs(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(3) %}
:::: {.panel}
## Tab{{i}}

::: {.panel}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.panel}
### subtab2_{{i}}

content2_{{i}}
:::

::::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_collapses_in_tabs(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(3) %}
:::: {.panel}
## Tab{{i}}

::: {.panel}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.panel}
### subtab2_{{i}}

content2_{{i}}
:::

::: {.panel}
### subtab3_{{i}}

content3_{{i}}
:::

::: {.panel}
### subtab4_{{i}}

content4_{{i}}
:::

::::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_tabs_in_collapses(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(5) %}
:::: {.panel}
## Tab{{i}}

::: {.panel}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.panel}
### subtab2_{{i}}

content2_{{i}}
:::

::::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_collapses_in_collapses(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(5) %}
:::: {.panel}
## Tab{{i}}

::: {.panel}
### subtab1_{{i}}

content1_{{i}}
:::

::: {.panel}
### subtab2_{{i}}

content2_{{i}}
:::

::: {.panel}
### subtab3_{{i}}

content3_{{i}}
:::

::: {.panel}
### subtab4_{{i}}

content4_{{i}}
:::

::::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_force_collapses(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(3) %}
::: {.panel .accordion}

content{{i}}
:::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_filetable(proc, reportfile):
    proc.config.report_template = '''
```table
file: %s/data/filetable.txt
caption: Sample table
header: true
rows: 0
cols: 0
```
''' % HERE
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_force_tabs(proc, reportfile):
    proc.config.report_template = '''
# Title
{% for i in range(6) %}
::: {.tab .panel}

content{{i}}
:::
{% endfor %}
'''
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

# def test_modals(proc, reportfile):
#     proc.config.report_template = '''
# # Title
# Click [here](modal#detailinfo) for details.

# {# size: default, small, large, xlarge #}
# ::: {.modal id="detailinfo" title="Detailed information" closebtn="true" size="xlarge"}
# ```table
# file: %s/filetable.txt
# caption: Sample table
# header: true
# rows: 10
# cols: 0
# csvargs:
#     dialect: unix
#     #delimiter: "	"
# ```

# ![](%s/snapshot.png)
# :::
# ''' % (HERE, HERE)
#     PyPPL(forks=5).start(proc).run().report(outfile = reportfile)

def test_disable_report(proc, reportfile):
    proc.config.report_template = False
    PyPPL(forks=5).start(proc).run().report(outfile = reportfile)
    assert_in_file(reportfile, 'Reports for')
