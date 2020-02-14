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

# pylint: disable=unused-argument,too-many-branches,too-many-statements
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

    options['header'] = options.get('header', True)
    options['nrows'] = options.pop('rows', options.get('nrows', 0))
    options['ncols'] = options.pop('cols', options.get('ncols', 0))
    mediadir = Path(doc.get_metadata('mediadir'))
    options['nrows'] += 1 if options['nrows'] and options['header'] else 0

    csvargs = options.get('csvargs', {})
    csvargs['dialect'] = csvargs.get('dialect', "unix")
    csvargs['delimiter'] = csvargs.get('delimiter',
                                       "\t").encode().decode('unicode_escape')
    comment = csvargs.pop('comment', False)

    options['file'] = (Path(doc.get_metadata('indir')) / options['file']
                       if 'file' in options and str(options['file'])[:1] != '/'
                       else options.get('file'))
    fdata = io.StringIO(data) if data else open(options['file'])
    attributes['data-prtable-header'] = False

    if comment:
        while True:
            fcursor = fdata.tell()
            pf.debug(fcursor)
            if fdata.readline().startswith(comment):
                continue
            fdata.seek(fcursor)
            break
    try:
        reader = csv.reader(fdata, **csvargs)
        attributes['data-prtable-data'] = []
        for i, row in enumerate(reader):
            if options['header'] and not attributes['data-prtable-header']:
                attributes['data-prtable-header'] = row
                continue

            if options['nrows'] and i > options['nrows']:
                break
            attributes['data-prtable-data'].append([
                x for k, x in enumerate(row)
                if not options['ncols'] or k < options['ncols']
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
        if not options['file']:
            options['file'] = mediadir.joinpath(
                str(md5str(data))
            ).with_suffix('.txt')
            attributes['data-prtable-file'] = str(options['file'].relative_to(
                doc.get_metadata('outdir')
            ))
            with options['file'].open('w') as fdata:
                if attributes['data-prtable-header']:
                    fdata.write("\t".join(attributes['data-prtable-header']) +
                                "\n")
                for row in attributes['data-prtable-data']:
                    fdata.write("\t".join(row) +
                                "\n")
        else:
            # copy file to mediadir and check if file exists
            options['file'] = Path(options['file'])
            attributes['data-prtable-file'] = str(copy_to_media(
                options['file'],
                mediadir / options['file'].name
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
