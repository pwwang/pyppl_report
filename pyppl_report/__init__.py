"""A report generating system for PyPPL"""
import sys
from time import time
from hashlib import sha256
from pathlib import Path
import textwrap
import toml
from pyppl.plugin import hookimpl
from pyppl.logger import logger
from pyppl.jobmgr import STATES
from pyppl.utils import fs, format_secs, filesig
from pyppl.exception import ProcessAttributeError
from diot import Diot, OrderedDiot
from cmdy import CmdyReturnCodeException
from .report import Report

__version__ = "0.6.0"


def report_template_converter(value):
    """Convert relative path of a template to absolute"""
    if value and value.startswith('file:'):
        scriptpath = Path(value[5:])
        if not scriptpath.is_absolute():
            from inspect import getframeinfo, stack

            # 0: .../pyppl_report/pyppl_report/__init__.py
            # 1: .../PyPPL/pyppl/plugin.py
            # 2: .../site-packages/diot.py
            # 3: .../pyppl_report/tests/test_report.py
            # if it fails in the future, check if the callstacks
            # changed from pluggy
            caller = getframeinfo(stack()[3][0])
            scriptdir = Path(caller.filename).parent.resolve()
            scriptpath = scriptdir / scriptpath
        if not scriptpath.is_file():
            raise ProcessAttributeError(
                'Report template file does not exist: %s' % scriptpath)
        return "file:%s" % scriptpath
    return value


@hookimpl
def setup(config):
    """Setup the plugin"""
    config.config.report_template = ''
    config.config.report_envs = Diot(level=1, pre='', post='')


@hookimpl
def logger_init(logger):  # pylint: disable=redefined-outer-name
    """Add log level"""
    logger.add_level('report')


@hookimpl
def proc_init(proc):
    """Add config"""
    proc.add_config('report_template',
                    default='',
                    converter=report_template_converter)
    proc.add_config('report_envs',
                    default=Diot(),
                    converter=lambda envs: envs or Diot())


@hookimpl
def proc_postrun(proc, status):
    """Generate report for the process"""
    # skip if process failed or cached
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    report_file = proc.workdir.joinpath('proc.report.md')
    template = proc.config.report_template
    template_file = None
    if template and template.startswith('file:'):
        template_file = Path(template[5:])
        logger.debug("Using report template: %s", template_file, proc=proc.id)

    if not template and report_file.is_file():
        report_file.unlink()

    if not template or status == 'failed':
        return

    signature = OrderedDiot([(key, value)
                             for key, value in sorted(proc.config.items())
                             if key.startswith('report_')])
    if template_file and template_file.is_file():
        signature.template = filesig(template_file)
    signature = sha256(toml.dumps(signature).encode()).hexdigest()

    if status == 'cached' and report_file.is_file():
        with report_file.open() as frpt:
            if frpt.readline().strip() == '<!--- %s -->' % signature:
                logger.debug("Report markdown file cached, skip.", proc=proc.id)
                return

    fs.remove(report_file)
    logger.debug('Rendering report template ...', proc=proc.id)
    if template_file:
        template = template_file.read_text()

    template = proc.template(template, **proc.envs)
    rptdata = dict(jobs=[None] * proc.size, proc=proc, args=proc.args)
    for i, job in enumerate(proc.jobs):
        rptdata['jobs'][i] = job.data.job.copy()
        rptdata['jobs'][i]['i'] = job.data.i
        rptdata['jobs'][i]['o'] = job.data.o

        datafile = job.dir / 'output/job.report.data.toml'
        if datafile.is_file():
            with datafile.open() as fdata:
                rptdata['jobs'][i].update(toml.load(fdata))

    rptenvs = Diot(level=1, pre='', post='', title=proc.desc)
    rptenvs.update(proc.config.report_envs)
    rptdata['report'] = rptenvs
    try:
        reportmd = template.render(rptdata)
    except Exception as exc:
        raise RuntimeError('Failed to render report markdown for process: %s' %
                           (proc)) from exc
    reportmd = reportmd.splitlines()

    codeblock = False
    for i, line in enumerate(reportmd):
        if line.startswith('#') and not codeblock:
            reportmd[i] = '#' * (rptenvs.level - 1) + line
        elif codeblock:
            if line.startswith('```') and len(line) - len(
                    line.lstrip('`')) == codeblock:
                codeblock = False
        elif line.startswith('```'):
            codeblock = len(line) - len(line.lstrip('`'))

    report_file.write_text(
        '<!--- %s -->' % signature +
        proc.template(textwrap.dedent(rptenvs.pre),
                      **proc.envs).render(rptdata) + '\n\n' +
        '\n'.join(reportmd) + '\n\n' +
        proc.template(textwrap.dedent(rptenvs.post),
                      **proc.envs).render(rptdata) + '\n'
    )

def report(ppl, # pylint: disable=too-many-arguments
           outfile=None,
           title=None,
           standalone=True,
           template=False,
           filters=False,
           toc=3):
    """@API
    Generate report for the pipeline.
    Currently only HTML format supported.
    @params:
        outfile (file): The report file, could be a directory,
            then the report file will be:
            - `<pipeline name>.report.html`
        title (str): The title of the report.
            - Default: 'A report generated by pipeline powered by PyPPL'
        standalone (bool): A standalone html file? Default: True
            - Otherwise, static files, including js/css/images will be
              store in a separated directory.
    """
    timer = time()
    default_basename = '%s.report.html' % ppl.name
    if not outfile:
        outfile = Path('.').joinpath(default_basename)
    elif Path(outfile).is_dir():
        outfile = Path(outfile).joinpath(default_basename)
    else:
        outfile = Path(outfile)

    logger.report('Generating report using pandoc ...')
    reports = [
        proc.workdir.joinpath('proc.report.md') for proc in ppl.procs
        if proc.workdir.joinpath('proc.report.md').exists()
    ]

    # see if it is cached:
    if (outfile.is_file()
            and reports
            and outfile.stat().st_mtime >= max(rptmd.stat().st_mtime
                                               for rptmd in reports)):
        logger.report('Report cached: %s', outfile)
    else:
        # force to add a title.
        title = title or 'Reports for ' + ppl.name + ' pipeline'
        cmd = Report(reports, outfile, title).generate(standalone,
                                                       template,
                                                       filters,
                                                       toc)
        try:
            logger.debug('Running: ' + cmd.cmd)
            cmd.run()
            logger.report('Report generated: %s', outfile)
            logger.report('Time elapsed: %s', format_secs(time() - timer))
        except CmdyReturnCodeException as ex:
            ex = str(ex)
            if 'Stack space overflow' not in ex:
                logger.error(str(ex))
                sys.exit(1)

            logger.warning('Error "Stack space overflow" from pandoc, '
                           'try to use "+RTS -K512M -RTS"')
            cmds = cmd.cmd.split(' ', 1)
            cmds.insert(1, '+RTS -K512M -RTS')
            cmd.cmd = ' '.join(cmds)
            try:
                logger.debug('Running: ' + cmd.cmd)
                cmd.done = False
                cmd.run()
                logger.report('Report generated: %s', outfile)
                logger.report('Time elapsed: %s', format_secs(time() - timer))
            except CmdyReturnCodeException as ex2:
                logger.error(str(ex2))
                sys.exit(1)

@hookimpl
def pyppl_init(ppl):
    """Add method to PyPPL instance"""
    ppl.add_method(report, require='run')


@hookimpl
def cli_addcmd(commands):
    """Add subcommand to pyppl"""
    commands.report = 'Convert a Markdown file to report.'
    params = commands.report
    params['in'].required = True
    params['in'].desc = 'The input file.'
    params.i = params['in']
    params.i.type = list
    params.out.desc = 'The output file. Default: <in>.html'
    params.out.callback = lambda opt, ps: (
        opt.set_value(Path(ps.i.value[0]).with_suffix('.html'))
        if not opt.value
        else None
    )
    params.o = params.out
    params.nonstand = False
    params.nonstand.desc = ('Non-standalone mode. '
                            'Save static files in `<filename of --out>.files` '
                            'separately.')
    params.n = params.nonstand
    params.filter = []
    params.filter.desc = 'The filters for pandoc'
    params.toc = 3
    params.toc.desc = 'The depth of heading levels to put in TOC. 0 to disable.'
    params.title = 'Untitled document'
    params.title.desc = ['The title of the document.',
                         'If the first element of the document is H1 (#), '
                         'this will be ignored and the text of H1 will be '
                         'used as title.',
                         'If the title is specified as "# Title", '
                         'then a title will be added anyway.']
    params.template = 'bootstrap'
    params.template.desc = ('The template to use. '
                            'Either standard template name or '
                            'full path to template file.')


@hookimpl
def cli_execcmd(command, opts):
    """Run the command"""
    if command == 'report':
        cmd = Report(opts.i, opts.o,
                     opts.title).generate(not opts.nonstand, opts.template,
                                          opts.filter, opts.toc)
        try:
            logger.info('Running: ' + cmd.pipedcmd)
            cmd.run()
            logger.info('Report generated: ' + str(opts.o))
        except CmdyReturnCodeException as ex:
            logger.error(str(ex))
            sys.exit(1)
