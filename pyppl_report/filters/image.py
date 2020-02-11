"""
Panflute filter to save a copy of the image to
the mediadir in non-standard mode
Move "src" to "data-src" for lazy loading
So if the theme doesn't implement lazy loading, you have to set the "src"
using javascript
"""
from pathlib import Path
from urllib.parse import unquote
import panflute as pf
from link import copy_to_media

def action(elem, doc):
    """action"""
    # local image or local link for download
    if isinstance(elem, pf.Image):
        # parse the attributes from href
        if '//' not in elem.url and doc.get_metadata('standalone') != '1':
            # local images
            filepath = Path(unquote(elem.url))
            if str(filepath)[:1] != '/':
                filepath = Path(doc.get_metadata('indir')) / filepath
            destfile = Path(doc.get_metadata('mediadir')) / filepath.name
            destfile = copy_to_media(filepath, destfile)
            elem.url = str(destfile.relative_to(doc.get_metadata('outdir')))
        elem.attributes['data-src'] = elem.url
        elem.url = 'data:null'

def main(doc=None):
    """main function"""
    return pf.run_filter(action, doc=doc)

if __name__ == '__main__':
    main()
