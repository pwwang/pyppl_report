# pyppl_report

[![Pypi][3]][4] [![Github][5]][6] [![PyPPL][7]][1] [![PythonVers][8]][4] [![docs][9]][2] [![Travis building][10]][11] [![Codacy][12]][13] [![Codacy coverage][14]][13]

A report generating system for [PyPPL][1]

## Installation
Requires pandoc 2.7+ (and wkhtmltopdf 0.12.4+ when creating PDF reports)

`pyppl_report` requires `pandoc/wkhtmltopdf` to be installed in `$PATH`

```shell
pip install pyppl_report
```

## Usage
### Specifiation of template

````python
pPyClone.config.report_template = """
# {{report.title}}

PyClone[1] is a tool using Probabilistic model for inferring clonal population
structure from deep NGS sequencing.

![Similarity matrix]({{path.join(job.o.outdir, "plots/loci/similarity_matrix.svg")}})

```table
caption: Clusters
file: "{{path.join(job.o.outdir, "tables/cluster.tsv")}}"
rows: 10
```

[1]: Roth, Andrew, et al. "PyClone: statistical inference of clonal population structure in cancer."
Nature methods 11.4 (2014): 396.
"""

# or use a template file

pPyClone.config.report_template = "file:/path/to/template.md"
````

### Generating report
```python
PyPPL().start(pPyClone).run().report(
	'/path/to/report',
	title='Clonality analysis using PyClone',
	template='bootstrap'
)

# or save report in a directory
PyPPL(name='Awesome-pipeline').start(pPyClone).run().report('/path/to/')
# report generated at ./Awesome-pipeline.report.html
```


### Extra data for rendering
You can generate a `toml` file named `job.report.data.toml` under `<job.outdir>` with extra data to render the report template. Beyond that, `proc` attributes and `args` can also be used.

For example:
`job.report.data.toml`:
```toml
description = 'A awesome report for job 1'
```
Then in your template, you can use it:
```markdown
## {{jobs[0].description}}
```

### References

We use `[1]`, `[2]` ... to link to the references, so HTML links have to be in-place (in the format of `[text](link)` instead of `[text][link-index]`). All references from different processes will be re-ordered and combined.

## Built-in themes

[Bootstrip]()
[Layui]()
[Semantic]()


[1]: https://github.com/pwwang/PyPPL
[2]: https://pyppl_report.readthedocs.io/en/latest/
[3]: https://img.shields.io/pypi/v/pyppl_report?style=flat-square
[4]: https://pypi.org/project/pyppl_report/
[5]: https://img.shields.io/github/tag/pwwang/pyppl_report?style=flat-square
[6]: https://github.com/pwwang/pyppl_report
[7]: https://img.shields.io/github/tag/pwwang/pyppl?label=PyPPL&style=flat-square
[8]: https://img.shields.io/pypi/pyversions/pyppl_report?style=flat-square
[9]: https://img.shields.io/readthedocs/pyppl_report.svg?style=flat-square
[10]: https://img.shields.io/travis/pwwang/pyppl_report?style=flat-square
[11]: https://travis-ci.org/pwwang/pyppl_report
[12]: https://img.shields.io/codacy/grade/2b7914a18f794248a62d7b36eb2408a3?style=flat-square
[13]: https://app.codacy.com/manual/pwwang/pyppl_report/dashboard
[14]: https://img.shields.io/codacy/coverage/2b7914a18f794248a62d7b36eb2408a3?style=flat-square
