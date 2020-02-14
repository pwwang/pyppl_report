## 0.6.0
- Add caching for report generation
- Rewrite part of the plugin for better theming
- Add three builtin themes (templates): layui, bootstrap, semantic
- Allow comments in csv for table filter
- Try another run if pandoc throws "Stack space overflow".

## 0.5.0
- Adopt `PyPPL 3.0`

## 0.4.2
- Add `pyppl-report` executable
- Use `diot` instead of `python-box`

## 0.4.1
- Raise informative exception while rendering markdown for a process.
- Adjust styles for default template.
- Remove unused code in template.js

## 0.4.0
- Add directory of outfile to resource-path
- Fix # alignment error in filetable filter
- Add download link for non-standalone mode
- Allow links in filetable in Markdown format
- Add tests for filters
- Save common static files in common directory instead to avoid redundant files for non-standalone mode

## 0.3.0
- Add non-standalone mode for html reports
- Fix bug when disabling report generating report for individual process using `proc.report = False`

## 0.2.1
- Ignore title if md doc has h1 for command line mode.
- Force adding title even if md doc has h1.

## 0.2.0
- Rename to pyppl_report due to inability of dash in entry point
- Report time elapsed for generating reports
- Use template.html instead of standalone.html for templates
- Add loading mask for template bootstrap
- Fix not jumping to collapse head when expanded
- Fix table header being overlapped in pdf mode
- Remove scripts in pdf mode

## 0.1.5
- Add `pyppl_report` command to convert external markdown files as well
- Suport PDF output: #1

## 0.1.4
- Add image preview for theme bootstrap
- Format numbers for filetable filter

## 0.1.3
- Allow data in table fenced block

## 0.1.2
- Drop proc.tplenvs, use drop.envs instead

## 0.1.1
- Add jquery.datatables

## 0.1.0
- Add more HTML components
- Fix bugs
- Add tests

## 0.0.1
- Implement basic functions
