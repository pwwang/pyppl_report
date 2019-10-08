You may pass values to process envs to control report content:
```python
pXXX.envs.report.foo = "bar"
```
Then in you can use it in the report template:
```python
pXXX.report = """
The value of foo is "{{foo}}".
"""
```

!!! Tip

	To disable report generation for a process, just set `proc.report = ''` or `proc.report = False`.

## Preserved envs variables

We have 4 preserved variables under `pXXX.envs`:
```python
# Control the level of headings in the
pXXX.envs.report.level = 2
# Content to add before the template
pXXX.envs.report.pre = ''
# Content to add after the template
pXXX.envs.report.post = ''
# The title of the process report
pXXX.envs.report.title = None
```

### Process report levels

No matter at which level you want to put this process report in the entire report, you need to each heading from level 1, then according to `pXXX.envs.report.level`, the headings will be shifted to corresponding level. For example, with `pXXX.envs.report.level = 2`, following template

```markdown
# Section
## Subsection
content
```

will be rendered into:
```markdown
## Section
### Subsection
content
```

!!! note

	Comments in codeblock will be preserved.

### Adding extra contents to process report

You may add extra contents to the process report. For example, if you put the process report at level 3, then you probably need a level-2 heading. For previous example, if you have `pXXX.envs.report.level = 3`, without a level-2 heading, the entire report will look like:

```markdown
# An awesome report

### Section
#### Subsection
content
```

Then you missed a level-2 heading, which will make your report look wired. Here you can specify a level-2 heading with `pXXX.envs.report.pre = '## I am H2'`:

```markdown
# An awesome report

## I am H2
### Section
#### Subsection
content
```

You may also append something to the process report with `pXXX.envs.report.post`

!!! warning

	Headings added by `pre` and `post` will not be adjusted by `pXXX.envs.report.level`

### Title of the process report

By default, if not assigned or assigned with `None`, the process description will be used as the title of the process report. Of course you can overwrite it with `pXXX.envs.report.title`.

```python
# by default
pXXX = Proc(desc = 'Some analysis')
# ... other necessary settings
pXXX.report = '# {{title}}'
```

will be rendered as (remember default level is 2):
```markdown
## Some analysis
```

with `pXXX.envs.report.title = 'An amazing analysis'`, we will have:

```markdown
## An amazing analysis
```

## Making your report flexiable

You can interpolate some variables in the templates to make your report flexiable. For example, you may want to hide an image in some cases:

```markdown
# {{title}}

I have enough details.

{% if report.get('showimage') %}
![Image](./path/to/image)
{% endif %}
```

Then you can show that image in the report only when you have `pXXX.envs.report.showimage = True`.
