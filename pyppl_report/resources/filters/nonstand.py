"""
Make html reports non-standalone, allowing css, javascript and images saved in mediadir.
"""
from pathlib import Path
from shutil import copyfile
from hashlib import md5
from urllib.parse import unquote
import panflute as pf

def _copyfile(filepath, destfile):
	if destfile.exists():
		md5sum1 = md5(destfile.read_bytes()).hexdigest()
		md5sum2 = md5(filepath.read_bytes()).hexdigest()
		if (md5sum1 != md5sum2): # rename and copy file
			candfiles = list(destfile.parent.glob("[[]*[]]" + destfile.name))
			if not candfiles:
				destfile = destfile.parent / ('[1]' + destfile.name)
			else:
				maxnum = max(int(cfile.name.split(']')[0][1:]) for cfile in candfiles)
				destfile = destfile.parent / ('[{}]{}'.format(maxnum + 1, destfile.name))
			copyfile(filepath, destfile)
	else:
		copyfile(str(filepath), str(destfile))

	return destfile

def prepare(doc):
	mediadir = doc.get_metadata('mediadir')
	doc.mediadir = Path(mediadir)

	template = doc.get_metadata('template')
	if not mediadir or not template: # pragma: no cover
		raise ValueError('Non-standalone mode needs mediadir to be set.')

	mediadir = doc.mediadir.parent.joinpath('__common__.files')
	mediadir.joinpath('js').mkdir(exist_ok = True, parents = True)
	mediadir.joinpath('css').mkdir(exist_ok = True, parents = True)
	template = Path(template)
	for jsfile in template.parent.joinpath('static').glob('*.js'):
		_copyfile(jsfile, mediadir.joinpath('js', jsfile.name))
	for cssfile in template.parent.joinpath('static').glob('*.css'):
		_copyfile(cssfile, mediadir.joinpath('css', cssfile.name))

def action(elem, doc):
	# local image or local link for download
	if  (isinstance(elem, pf.Image) and elem.url.startswith('/')) or \
		(isinstance(elem, pf.Link) and elem.title == 'file-download'):
		filepath = Path(unquote(elem.url))
		destfile = doc.mediadir.joinpath(filepath.name)
		destfile = _copyfile(filepath, destfile)
		elem.url = str(destfile.relative_to(destfile.parent.parent))

def main(doc=None):
	return pf.run_filter(action, prepare=prepare, doc=doc)

if __name__ == '__main__':
	main()
