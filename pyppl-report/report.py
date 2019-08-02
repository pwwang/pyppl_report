"""Report generating system using pandoc"""
import re
from cmdy import pandoc
from pathlib import Path

RESOURCE_DIR     = Path(__file__).resolve().parent / 'resources'
DEFAULT_FILTERS  = ['filetable', 'modal']
DEFAULT_TEMPLATE = 'bootstrap'

def _replaceAll(regex, callback, string):
	matches = re.finditer(regex, string)
	ret = ''
	start = 0
	for match in matches:
		ret += string[start:match.start(0)]
		start = match.end(0)
		ret += callback(match.group(), *match.groups())
	return ret + string[start:]

class ProcReport:

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
		def replace(m):
			index = m[1:-1]
			if index not in citations:
				return m
			return '[#REF: %s #]' % citations[index]

		source = source and '\n'.join(source) or ''
		source = _replaceAll(r'\[\d+\]', replace, source)

		appendix = appendix and '\n'.join(appendix) or ''
		appendix = _replaceAll(r'\[\d+\]', replace, appendix)

		return source, appendix

class Report:

	def __init__(self, rptfiles, outfile, title):
		self.reports = [ProcReport(rptfile) for rptfile in rptfiles]
		self.outfile = Path(outfile)
		self.mdfile  = self.outfile.with_suffix('.md')
		self.title   = title
		self.cleanup()

	def cleanup(self):
		citations = {}
		def replace(m):
			cite = m[7:-3]
			if cite not in citations:
				citations[cite] = len(citations) + 1
			return '<sup><a href="#REF_{i}">[{i}]</a></sup>'.format(i = citations[cite])

		with self.mdfile.open('w') as fmd:
			fmd.write('# %s\n\n' % self.title)
			appendix = ''
			for report in self.reports:
				# replace reference to citation indexes
				source = _replaceAll(r'\[#REF: .+? #\]', replace, report.source)
				if report.appendix:
					appendix += _replaceAll(r'\[#REF: .+? #\]', replace, report.appendix)

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
		from pyppl import __version__ as pyppl_version
		from . import __version__ as report_version
		template = template or DEFAULT_TEMPLATE
		if template and '/' not in template:
			template = RESOURCE_DIR / 'templates' / template / 'standalone.html'
		return pandoc(
			self.mdfile,
			metadata = [
				'pagetitle=%s' % self.title,
				'pyppl_version=%s' % pyppl_version,
				'report_version=%s' % report_version],
			read     = 'markdown',
			write    = 'html',
			template = template,
			filter   = [RESOURCE_DIR / 'filters' / (filt + '.py')
				for filt in DEFAULT_FILTERS] + (filters or []),
			toc      = True,
			output   = self.outfile,
			_raise   = True,
			_sep     = 'auto',
			_dupkey  = True,
			_hold    = True,
			**{ 'toc-depth': 3,
				'self-contained': standalone,
				'resource-path': Path(template).parent})
