"""pyppl_report/pyppl-report executable"""

import sys
from os import path
from pyparam import params
from cmdy import CmdyReturnCodeException
from diot import Diot
from pyppl.logger import logger
from .report import Report

params['in'].required = True
params['in'].desc = 'The input file.'
params.i = params['in']
params.i.type = list
params.out.desc = 'The output file. Default: <in>.html'
params.out.callback = lambda opt, ps: opt.setValue(path.splitext(ps.i.value[0])[0] + '.html') \
	if not opt.value else None
params.o = params.out
params.nonstand = False
params.nonstand.desc = 'Non-standalone mode. ' + \
	'Save static files in `<filename of --out>.files` separately.'
params.n = params.nonstand
params.filter = []
params.filter.desc = 'The filters for pandoc'
params.title = 'Untitled document'
params.title.desc = '''The title of the document.
If the first element of the document is H1 (#), this will be ignored and the text of H1 will be used as title.
If the title is specified as "# Title", then a title will be added anyway.
'''
params.template = 'bootstrap'
params.template.desc = 'The template to use. ' + \
	'Either standard template name or full path to template file.'

def main():
	"""Main entry point"""
	opts = params._parse(dict_wrapper = Diot)
	cmd = Report(opts.i, opts.o, opts.title).generate(not opts.nonstand, opts.template, opts.filter)
	try:
		logger.info('Running: ' + cmd.pipedcmd)
		cmd.run()
		logger.info('Report generated: ' + str(opts.o))
	except CmdyReturnCodeException as ex:
		logger.error(str(ex))
		sys.exit(1)
