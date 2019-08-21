import sys
from os import path
from pyparam import params
from cmdy import CmdyReturnCodeException
from pyppl import Box
from pyppl.logger import logger
from .report import Report

params['in'].required = True
params['in'].desc = 'The input file.'
params.i = params['in']
params.i.type = list
params.out.desc = 'The output file. Default: <in>.html'
params.out.callback = lambda opt, ps: opt.setValue(path.splitext(ps.i.value[0])[0] + '.html') if not opt.value else None
params.o = params.out
params.filter = []
params.filter.desc = 'The filters for pandoc'
params.title = 'Untitled document'
params.title.desc = 'The title of the document.'
params.template = 'bootstrap'
params.template.desc = 'The template to use. Either standard template name or full path to template file.'

def main():
	opts = params._parse(dict_wrapper = Box)
	cmd = Report(opts.i, opts.o, opts.title).generate(True, opts.template, opts.filter)
	try:
		logger.info('Running: ' + cmd.pipedcmd)
		cmd.run()
		logger.info('Report generated: ' + str(opts.o))
	except CmdyReturnCodeException as ex:
		logger.error(str(ex))
		sys.exit(1)
