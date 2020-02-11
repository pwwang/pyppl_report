"""
Panflute filter to parse CSV in fenced YAML code blocks

Turn
```table
caption : An awesome table
file    : /path/to/csv/tsv/file
header  : true
download: true
rows    : 10
cols    : 0
sort    : [0]
pagesize: 25
csvargs :
    delimiter: "\t"
```

into:

```html
<div class="pyppl-report-table"
       data-prtable-caption="An awesome table"
       data-prtable-header="['HEADER1', 'HEADER2', ...]">
       data-prtable-data="[[ROW1], [ROW2], ...]"
       data-prtable-sort="[0]"
       data-prtable-download="true"
       data-prtable-file="FILE-PATH-TO-THE-TABLE"
       data-prtable-pagesize="25"></div>
```
which will be ready for the theme js to parse and render
"""
import io
import json
import csv
from pathlib import Path
import panflute as pf
from utils import copy_to_media, md5str

# pylint: disable=unused-argument
def fenced_action(options, data, element, doc):
    """fenced action"""
    # We'll only run this for CodeBlock elements of class 'table'

    attributes = {}
    attributes['data-prtable-file'] = ""
    attributes['data-prtable-download'] = str(options.get('download',
                                                          False)).lower()
    attributes['data-prtable-pagesize'] = str(options.get('sort', 25))
    attributes['data-prtable-sort'] = json.dumps(options.get('sort', [0]))
    attributes['data-prtable-caption'] = options.get('caption',
                                                     'Untitled Table')

    filepath = options.get('file')
    has_header = options.get('header', True)
    nrows = options.get('rows', 0)
    ncols = options.get('cols', 0)
    mediadir = Path(doc.get_metadata('mediadir'))
    nrows += 1 if nrows and has_header else 0

    csvargs = options.get('csvargs', {})
    pf.debug(options)
    csvargs['dialect'] = csvargs.get('dialect', "unix")
    csvargs['delimiter'] = csvargs.get('delimiter',
                                       "\t").encode().decode('unicode_escape')

    filepath = (Path(doc.get_metadata('indir')) / filepath
                if filepath and str(filepath)[:1] != '/'
                else filepath)
    fdata = io.StringIO(data) if data else open(filepath)
    attributes['data-prtable-header'] = False
    try:
        reader = csv.reader(fdata, **csvargs)
        attributes['data-prtable-data'] = []
        for i, row in enumerate(reader):
            if i == 0 and has_header:
                attributes['data-prtable-header'] = row
                continue

            if nrows and i > nrows:
                continue
            attributes['data-prtable-data'].append([
                x for k, x in enumerate(row)
                if not ncols or k < ncols
            ])
    finally:
        fdata.close()

    if (attributes['data-prtable-header']
            and attributes['data-prtable-data']
            and len(attributes['data-prtable-data'][0]) ==
            len(attributes['data-prtable-header']) + 1):
        attributes['data-prtable-header'].insert(0, "ROWNAME")
    if (attributes['data-prtable-header']
            and attributes['data-prtable-header'][0] == ""):
        attributes['data-prtable-header'][0] = "ROWNAME"

    if attributes['data-prtable-download'] == 'true':
        if not filepath:
            filepath = mediadir.joinpath(str(md5str(data))).with_suffix('.txt')
            attributes['data-prtable-file'] = str(filepath.relative_to(
                doc.get_metadata('outdir')
            ))
            with filepath.open('w') as fdata:
                if attributes['data-prtable-header']:
                    fdata.write("\t".join(attributes['data-prtable-header']) +
                                "\n")
                for row in attributes['data-prtable-data']:
                    fdata.write("\t".join(row) +
                                "\n")
        else:
            # copy file to mediadir and check if file exists
            filepath = Path(filepath)
            attributes['data-prtable-file'] = str(copy_to_media(
                filepath,
                mediadir / filepath.name
            ).relative_to(doc.get_metadata('outdir')))

    attributes['data-prtable-header'] = json.dumps(
        attributes['data-prtable-header']
    )
    attributes['data-prtable-data'] = json.dumps(
        attributes['data-prtable-data']
    )
    return pf.Div(classes=['pyppl-report-table'], attributes=attributes)

def main(doc=None):
    """main function"""
    return pf.run_filter(pf.yaml_filter,
                         tag='table',
                         function=fenced_action,
                         doc=doc)


if __name__ == '__main__':
    main()
