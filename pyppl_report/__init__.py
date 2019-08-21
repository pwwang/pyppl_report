import sys
from time import time
from pathlib import Path
import yaml
from pyppl.plugin import hookimpl, postrun, addmethod
from pyppl.logger import logger, THEMES, LEVELS_ALWAYS
from pyppl.utils import fs, Box, formatSecs
from pyppl.exception import ProcAttributeError
from cmdy import CmdyReturnCodeException
from .report import Report

__version__ = "0.2.0"

@hookimpl
def setup(config):
	for colors in THEMES.values():
		colors['REPORT'] = colors['DONE']
	LEVELS_ALWAYS.add('REPORT')
	config['report']  = ''
	config['envs'].update(report = Box(
		level = 2,
		pre   = '',
		post  = '',
	))

@hookimpl
def procSetAttr(proc, name, value):
	if name == 'report' and value.startswith('file:'):
		scriptpath = Path(value[5:])
		if not scriptpath.is_absolute():
			from inspect import getframeinfo, stack

			# 0: .../pyppl_report/pyppl_report/__init__.py
			# 1: .../pluggy/callers.py
			# 2: .../pluggy/manager.py
			# 3: .../pluggy/manager.py
			# 4: .../pluggy/hooks.py
			# 5: .../PyPPL/pyppl/proc.py
			# 6: /file/define/the/report
			# if it fails in the future, check if the callstacks changed from pluggy
			caller = getframeinfo(stack()[6][0])
			scriptdir = Path(caller.filename).parent.resolve()
			scriptpath = scriptdir / scriptpath
		if not scriptpath.is_file():
			raise ProcAttributeError(
				'Report template file does not exist: %s' % scriptpath)
		proc.config[name] = "file:%s" % scriptpath

@hookimpl
def procGetAttr(proc, name):
	"""Pre-calculate the attribute"""
	if name == 'report':
		return Path(proc.workdir) / 'proc.report.md'

@hookimpl
def procPostRun(proc):
	"""Generate report for the process"""
	fs.remove(proc.report)
	if not proc.config.report:
		return

	logger.debug('Rendering report template ...')
	report = proc.config.report
	if report.startswith ('file:'):
		tplfile = Path(report[5:])
		## checked at __setattr__
		## and we are not able to change it on the run
		# if not fs.exists (tplfile):
		#	raise ProcAttributeError(tplfile, 'No such report template file')
		logger.debug("Using report template: %s", tplfile, proc = proc.id)
		report = tplfile.read_text()

	report  = proc.template(report, **proc.envs)
	rptdata = Box(jobs = [], **proc.procvars)
	for job in proc.jobs:
		jobdata  = job.data
		datafile = job.dir / 'output' / 'job.report.data.yaml'
		data = {}
		data.update(jobdata.job)
		if datafile.is_file():
			with datafile.open() as fdata:
				data.update(yaml.safe_load(fdata))
		rptdata.jobs.append(Box(i = jobdata.i, o = jobdata.o, **data))

	rptenvs  = Box(
		level = 2,
		pre   = '',
		post  = '',
		title = proc.desc)
	rptenvs.update(proc.envs.get('report', {}))
	rptdata.title = rptenvs.title
	reportmd = report.render(rptdata).splitlines()

	codeblock = False
	appendix  = False
	for i, line in enumerate(reportmd):
		if line.startswith('## Appendix') or appendix:
			appendix = True
			continue
		if line.startswith('#') and not codeblock:
			reportmd[i] = '#' * (rptenvs.level - 1) + line
		elif codeblock:
			if line.startswith('```') and len(line) - len(line.lstrip('`')) == codeblock:
				codeblock = False
		elif line.startswith('```'):
			codeblock = len(line) - len(line.lstrip('`'))

	proc.report.write_text(
		proc.template(rptenvs.pre, **proc.envs).render(rptdata) + '\n\n' +
		'\n'.join(reportmd) + '\n\n' +
		proc.template(rptenvs.post, **proc.envs).render(rptdata) + '\n'
	)

@postrun
def pyppl_report(ppl, outfile = None,
	title = 'A report generated by pipeline powered by PyPPL',
	standalone = True, template = False, filters = False):
	"""@API
	Generate report for the pipeline.
	Currently only HTML format supported.
	@params:
		outfile (file): The report file.
		title (str): The title of the report.
			- Default: 'A report generated by pipeline powered by PyPPL'
		standalone (bool): A standalone html file? Default: True
	@returns:
		(PyPPL): The pipeline object itppl.
	"""
	timer = time()
	outfile = outfile or (Path('.') / Path(sys.argv[0]).stem).with_suffix(
		'%s.report.html' % ('.' + str(ppl.counter) if ppl.counter else ''))
	logger.report('Generating report using pandoc ...')
	reports = [proc.report for proc in ppl.procs if proc.report.exists()]
	cmd = Report(reports, outfile, title).generate(standalone, template, filters)
	try:
		logger.debug('Running: ' + cmd.cmd)
		cmd.run()
		logger.report('Time elapsed: %s, report generated: %s' % (formatSecs(time() - timer), str(outfile)))
	except CmdyReturnCodeException as ex:
		logger.error(str(ex))
		sys.exit(1)

@hookimpl
def pypplInit(ppl):
	addmethod(ppl, 'report', pyppl_report)