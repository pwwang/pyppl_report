"""Report generating system using pandoc"""
import re
from pathlib import Path
from cmdy import pandoc, wkhtmltopdf

RESOURCE_DIR     = Path(__file__).resolve().parent / 'resources'
DEFAULT_FILTERS  = ['filetable', 'modal']
DEFAULT_TEMPLATE = 'bootstrap'

def _replace_all(regex, callback, string):
	matches = re.finditer(regex, string)
	ret = ''
	start = 0
	for match in matches:
		ret += string[start:match.start(0)]
		start = match.end(0)
		ret += callback(match.group(), *match.groups())
	return ret + string[start:]

class ProcReport: # pylint: disable=too-few-public-methods
	"""Report for each process"""
	def __init__(self, rptfile):
		self.rptfile   = Path(rptfile)
		self.source, self.appendix = self._analysis()

	def _analysis(self):
		"""Get the citations and appendix"""
		lines = self.rptfile.read_text().splitlines()
		# get the references first
		# references should be placed at the bottom
		source   = None
		appendix = None
		citations = {}
		for line in lines:
			line = line.rstrip('\n')
			if line.startswith('## Appendix'): # appendix has to be on level2 anyway
				appendix = []
			else:
				matched = re.match(r'\[(\d+)\]: (.+)', line)
				if matched:
					citations[matched.group(1)] = matched.group(2).strip()
				elif appendix is None:
					source = source or []
					source.append(line)
				else:
					appendix.append(line)

		# replace all citation marks with real references
		def replace(mstr):
			index = mstr[1:-1]
			if index not in citations:
				return mstr
			return '[#REF: %s #]' % citations[index]

		source = '\n'.join(source) if source else ''
		source = _replace_all(r'\[\d+\]', replace, source)

		appendix = '\n'.join(appendix) if appendix else ''
		appendix = _replace_all(r'\[\d+\]', replace, appendix)

		return source, appendix

class Report:
	"""The Report class"""
	def __init__(self, rptfiles, outfile, title):
		self.reports = [ProcReport(rptfile) for rptfile in rptfiles]
		#self.srcpath = ':'.join(str(Path(rptfile).parent) for rptfile in rptfiles)
		self.outfile = Path(outfile)
		self.mdfile  = self.outfile.resolve().with_suffix('.md')
		if str(self.mdfile) in [str(Path(rptfile).resolve()) for rptfile in rptfiles]:
			# don't overwrite input file
			self.mdfile = self.outfile.with_suffix('.tmp.md')
		self.orgtitle = ''
		if rptfiles:
			with open(rptfiles[0], 'r') as f:
				firstline = f.readline().strip()
				while not firstline:
					firstline = f.readline().strip()
				if firstline and firstline[0] == '#' and firstline[1] != '#':
					self.orgtitle = firstline.lstrip('# ')
		self.title = title
		self.cleanup()

	def cleanup(self):
		"""Cleanup and generate markdown for each process"""
		citations = {}
		def replace(mstr):
			cite = mstr[7:-3]
			if cite not in citations:
				citations[cite] = len(citations) + 1
			return '<sup><a href="#REF_{i}">[{i}]</a></sup>'.format(i = citations[cite])

		with self.mdfile.open('w') as fmd:
			# only when self.title starts with # or there is no orgtitle
			if self.title.startswith('#') or not self.orgtitle:
				fmd.write('# %s\n\n' % self.title.lstrip('# '))
			appendix = ''
			for report in self.reports:
				# replace reference to citation indexes
				source = _replace_all(r'\[#REF: .+? #\]', replace, report.source)
				if report.appendix:
					appendix += _replace_all(r'\[#REF: .+? #\]', replace, report.appendix)

				fmd.write(source + '\n\n')

			if appendix:
				fmd.write('## Appendix\n')
				fmd.write(appendix + '\n\n')

			if citations:
				fmd.write('## Reference\n')
				for cite, index in sorted(citations.items(), key = lambda item: item[1]):
					fmd.write('<a name="REF_{i}" class="reference">**[{i}]** {cite}</a>\n\n'.format(
						i=index, cite=cite))

	def generate(self, standalone, template, filters):
		"""Generate the reports"""
		from pyppl import __version__ as pyppl_version
		from . import __version__ as report_version

		template = template or DEFAULT_TEMPLATE
		if template and '/' not in template:
			template = RESOURCE_DIR / 'templates' / template / 'template.html'

		ext = self.outfile.suffix.lower()
		if 'htm' not in ext and 'pdf' not in ext:
			raise ValueError('Only html and pdf format supported currently.')
		if not standalone and 'pdf' in ext:
			raise ValueError('pdf format has to be standalone.')

		metadata = [
			'pagetitle=%s' % (self.title.lstrip('# ') \
				if self.title.startswith('#') or not self.orgtitle \
				else self.orgtitle),
			'pyppl_version=%s' % pyppl_version,
			'report_version=%s' % report_version,
			'pdf=%s' % bool('pdf' in ext)]
		srcpath = ['.', str(self.outfile.parent), str(Path(template).parent)]
		if not standalone:
			mediadir = self.outfile.with_suffix('.files')
			metadata.extend([
				'mediadir=%s' % mediadir,
				'template=%s' % template])
			srcpath.insert(2, str(mediadir))

		dfilters = DEFAULT_FILTERS[:]
		if not standalone:
			dfilters.append('nonstand')
		dfilters.extend(filters or [])

		args = (self.mdfile, )
		kwargs = {
			'metadata': metadata,
			'read'    : 'markdown',
			'write'   : 'html5',
			'template': template,
			'filter'  : [	RESOURCE_DIR / 'filters' / (filt + '.py')
							for filt in dfilters],
			'toc'           : True,
			'toc-depth'     : 3,
			'self-contained': standalone,
			'resource-path' : ':'.join(srcpath),
			'_raise'        : True,
			'_sep'          : 'auto',
			'_dupkey'       : True,
		}
		if 'pdf' not in ext:
			kwargs['output'] = self.outfile
			kwargs['_hold'] = True
			return pandoc(*args, **kwargs)
		kwargs['_pipe'] = True
		return pandoc(*args, **kwargs) | wkhtmltopdf(
			'-', _ = self.outfile, _raise = True, _hold = True)
