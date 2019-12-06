"""
Panflute filter to parse CSV in fenced YAML code blocks

```table
caption    : An awesome table
file       : /path/to/csv/tsv/file
header     : true
width      : 1
total_width: .8
align      : default
rows       : 10
cols       : 0
csvargs    :
	dialect: unix
	delimiter: "\t"
datatable: # false to disable
	"page-length": 10
	"search": true
```
"""
import io
import json
import csv
import re
from pathlib import Path
from hashlib import md5
from shutil import copyfile
import panflute as pf
from nonstand import _copyfile

def formatCell(text):
	if len(text) < 10 or text.isdigit():
		return pf.Plain(pf.Str(text))
	try:
		text = float(text)
		if text > 0 and text < .001:
			return pf.Plain(pf.Str('%.3E' % text))
		return pf.Plain(pf.Str('%.3f' % text))
	except (ValueError, TypeError):
		# transform links
		elems = []
		lastend = None
		for m in re.finditer(r'\[(.+?)\]\((.+?)\)', text):
			if lastend is None:
				elems.append(pf.Str(text[:m.start()]))
			else:
				elems.append(pf.Str(text[lastend:m.start()]))
			elems.append(pf.Link(pf.Str(m.group(1)), url = m.group(2)))
			lastend = m.end()
		if elems:
			elems.append(pf.Str(text[lastend:]))
			return pf.Plain(*elems)
		return pf.Plain(pf.Str(text))

def fenced_action(options, data, element, doc):
	# We'll only run this for CodeBlock elements of class 'table'
	caption     = options.get('caption', 'Untitled Table')
	#caption     = [pf.Str(caption)]
	filepath    = options.get('file')
	has_header  = options.get('header', True)
	width       = options.get('width', 1)
	total_width = float(options.get('total_width', .8))
	align       = options.get('align', 'default')
	nrows       = options.get('rows', 0)
	ncols       = options.get('cols', 0)
	csvargs     = options.get('csvargs', {})
	dtargs      = options.get('dtargs', {})
	mediadir    = doc.get_metadata('mediadir')

	csvargs['dialect']   = csvargs.get('dialect', "unix")
	csvargs['delimiter'] = csvargs.get('delimiter', "\t").encode().decode('unicode_escape')

	f = io.StringIO(data) if data else open(filepath)
	try:
		reader = csv.reader(f, **csvargs)
		body = []
		for i, row in enumerate(reader):
			if nrows and i > nrows:
				continue
			cells = [	pf.TableCell(formatCell(x))
						for k, x in enumerate(row) if not ncols or k < ncols]
			body.append(pf.TableRow(*cells))
	finally:
		f.close()

	ncols = min(ncols, len(row)) if ncols else len(row)
	if has_header:
		header = body.pop(0)
		if body and len(body[0].content) == len(header.content) + 1:
			header.content.insert(0, pf.TableCell(pf.Plain(pf.Str(''))))
	elif nrows:
		header = None
		body = body[:nrows]

	if not isinstance(width, list):
		width = [width]
	if len(width) == 1 and ncols:
		width = width * ncols
	sumwidth    = float(sum(width))
	total_width = min(total_width, 1)
	width       = [float(wid)*float(total_width)/sumwidth for wid in width]
	if not isinstance(align, list):
		align = [align]
	if len(align) == 1 and ncols:
		align = align * ncols
	align = ['Align' + al.capitalize() for al in align]

	if mediadir and filepath:
		# copy file to mediadir and check if file exists
		filepath = Path(filepath)
		mediadir = Path(mediadir)
		mediadir.mkdir(exist_ok = True, parents = True)
		destfile = mediadir / filepath.name
		destfile = _copyfile(filepath, destfile)

		caption = [pf.Link(	pf.Str(caption),
							url = str(destfile.relative_to(destfile.parent.parent)),
							title = 'Right clink and "Save link as" to download whole table.',
							attributes = {'target': '_blank'})]
	else:
		caption = [pf.Str(caption)]

	table = pf.Table(*body,
		header=header, caption=caption, width=width, alignment = align)
	if dtargs is False:
		return pf.Div(table, classes = ['tablewrapper'])
	else:
		return pf.Div(table, classes = ['tablewrapper', 'datatablewrapper'], attributes = {
			'data-datatable': json.dumps(dtargs)
		})

def main(doc=None):
	return pf.run_filter(pf.yaml_filter, tag='table', function=fenced_action, doc=doc)

if __name__ == '__main__':
	main()
