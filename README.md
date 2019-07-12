# pyppl-report

A report generating system for [PyPPL][1]

## Installation
```shell
pip install pyppl-report
```

## Usage
### Specifiation of template

````python
pPyClone.report = """
## {{proc.desc}}

PyClone[1] is a tool using Probabilistic model for inferring clonal population structure from deep NGS sequencing.

![Similarity matrix]({{path.join(job.o.outdir, "plots/loci/similarity_matrix.svg")}})

```table
caption: Clusters
file: "{{path.join(job.o.outdir, "tables/cluster.tsv")}}"
rows: 10
```

[1]: Roth, Andrew, et al. "PyClone: statistical inference of clonal population structure in cancer." Nature methods 11.4 (2014): 396.
"""

# or use a template file

pPyClone.report = "file:/path/to/template.md"
````

### Generating report
```python
PyPPL().start(pPyClone).run().report('/path/to/report', title = 'Clonality analysis using PyClone')
```

![Snapshort](./snapshot.png)

### Extra data for rendering
You can generate a `YAML` file named `job.report.data.yaml` under `<job.outdir>` with extra data to render the report template. Beyond that, `proc` attributes and `args` can also be used.

For example:
`job.report.data.yaml`:
```yaml
title: 'A awesome report for job 1'
```
Then in your template, you can use it:
```markdown
## {{jobs[0].title}}
```

### Showing tables with csv/tsv file

````markdown
```table
caption    : An awesome table
file       : /path/to/csv/tsv/file
header     : true
width      : 1   # width of each column
total_width: .8  # total width of the table
align      : default # alignment of each column
rows       : 10  # max rows to show
cols       : 0   # max cols to show, default: 0 (show all)
csvargs    : # csvargs for `csv.read`
	dialect: unix
	delimiter: "\t"
````

You may also specify `width` and `align` for individual columns:
```yaml
width:
  - .1
  - .2
  - .1
```

### References

We use `[1]`, `[2]` ... to link to the references, so HTML links have to be in-place (in the format of `[text](link)` instead of `[text][link-index]`). All references from different processes will be re-ordered and combined.

[1]: https://github.com/pwwang/PyPPL
