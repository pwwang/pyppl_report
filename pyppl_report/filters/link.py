"""
Panflute filter to support attributes for in Markdown

Turn
```markdown
[TEXT](URL {attr1=a, attr2=b} "TITLE")
```

into:

```html
<a class="pyppl-report-link"
   data-prlink-attr1="a"
   data-prlink-attr2="b"
   title="TITLE">TEXT</a>
```
which will be ready for the theme js to parse and render

If we are in non-standalone mode, try to save a copy of the file to mediadir
for the downloadable link
"""
from pathlib import Path
from urllib.parse import unquote
import panflute as pf
from utils import copy_to_media

def action(elem, doc):
    """action"""
    # local image or local link for download
    if isinstance(elem, pf.Link):
        attrs = elem.attributes.__class__([
            ('prlink-' + attrkey,
             attrval.lower()
             if attrval.lower() in ('true', 'false')
             else attrval)
            for attrkey, attrval in elem.attributes.items()
        ])
        if attrs.get('prlink-download') == 'true':
            filepath = Path(unquote(elem.url))
            if str(filepath)[:1] != '/':
                filepath = Path(doc.get_metadata('indir')) / filepath
            dstfile = Path(doc.get_metadata('mediadir')) / filepath.name
            dstfile = copy_to_media(filepath, dstfile)
            elem.url = str(dstfile.relative_to(doc.get_metadata('outdir')))

def main(doc=None):
    """main function"""
    return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
    main()
