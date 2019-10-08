"""
Make html reports non-standalone, allowing css, javascript and images saved in mediadir.
"""
from pathlib import Path
from shutil import copyfile
from hashlib import md5
from urllib.parse import unquote
import panflute as pf

def prepare(doc):
	mediadir = doc.get_metadata('mediadir')
	template = doc.get_metadata('template')
	if not mediadir or not template:
		raise ValueError('Non-standalone mode need mediadir to be set.')
	mediadir = Path(mediadir)
	mediadir.joinpath('js').mkdir(exist_ok = True, parents = True)
	mediadir.joinpath('css').mkdir(exist_ok = True, parents = True)
	template = Path(template)
	for jsfile in template.parent.joinpath('static').glob('*.js'):
		copyfile(jsfile, mediadir.joinpath('js', jsfile.name))
	for cssfile in template.parent.joinpath('static').glob('*.css'):
		copyfile(cssfile, mediadir.joinpath('css', cssfile.name))
	doc.mediadir = mediadir

def action(elem, doc):
	if isinstance(elem, pf.Image) and elem.url.startswith('/'): # local image
		filepath = Path(unquote(elem.url))
		destfile = doc.mediadir.joinpath(filepath.name)
		if destfile.exists():
			md5sum1 = md5(destfile.read_bytes()).hexdigest()
			md5sum2 = md5(filepath.read_bytes()).hexdigest()
			if (md5sum1 != md5sum2): # rename and copy file
				candfiles = list(doc.mediadir.glob("[[]*[]]" + filepath.name))
				if not candfiles:
					destfile = doc.mediadir / ('[1]' + filepath.name)
				else:
					maxnum = max(int(cfile.name.split(']')[0][1:]) for cfile in candfiles)
					destfile = doc.mediadir / ('[{}]{}'.format(maxnum + 1, filepath.name))
				copyfile(filepath, destfile)
		else:
			copyfile(filepath, destfile)
		elem.url = str(destfile.relative_to(destfile.parent.parent))

def main(doc=None):
	return pf.run_filter(action, prepare=prepare, doc=doc)

if __name__ == '__main__':
	main()
