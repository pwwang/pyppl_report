"""Report generating system using pandoc"""
import re
from pathlib import Path
from functools import partial
from base64 import b64encode, b64decode
from shutil import rmtree
from cmdy import pandoc, wkhtmltopdf
from .filters.utils import copy_to_media

HERE = Path(__file__).resolve().parent
DEFAULT_FILTERS = ['table', 'link', 'image']
DEFAULT_TEMPLATE = 'layui'


def _replace_all(regex, callback, string):
    matches = re.finditer(regex, string)
    ret = ''
    start = 0
    for match in matches:
        ret += string[start:match.start(0)]
        start = match.end(0)
        ret += callback(match.group(), *match.groups())
    return ret + string[start:]

def _replace_ref_index(matched, citations):
    """citations: index => ref"""
    index = matched[2:-2]
    if index in citations:
        return '[#REF: %s #]' % citations[index]
    return matched

def _replace_ref(matched, citations):
    """citations: ref => index"""
    cite = matched[7:-3] # [#REF: ... #]
    if cite not in citations:
        citations[cite] = len(citations) + 1
    return '[[{i}]](#PYPPL-REF-{i}){{.pyppl-report-refindex}}'.format(
        i=citations[cite]
    )


class ProcReport:  # pylint: disable=too-few-public-methods
    """Report for each process"""
    def __init__(self, rptfile):
        self.rptfile = Path(rptfile)
        self.source = None

    def prepare(self):
        """Get the citations"""
        lines = self.rptfile.read_text().splitlines()
        # get the references first
        # references should be placed at the bottom
        source = []
        citations = {}
        for line in lines:
            line = line.rstrip('\n')
            # [1]: reference 1
            # [2]: reference 2
            matched = re.match(r'\[\[(\d+)\]\]: (.+)', line)
            if not matched:
                source.append(line)
                continue
            citations[matched.group(1)] = b64encode(
                matched.group(2).strip().encode()
            ).decode()

        source = '\n'.join(source) if source else ''
        self.source = _replace_all(r'\[\[\d+\]\]',
                                   partial(_replace_ref_index,
                                           citations=citations),
                                   source)

class Report:
    """The Report class"""
    def __init__(self, rptfiles, outfile, title='Untitled document'):
        self.reports = [ProcReport(rptfile) for rptfile in rptfiles]
        # // convert to relative path
        try:
            self.outfile = Path(outfile).resolve().relative_to(Path.cwd())
        except ValueError:
            self.outfile = Path(outfile)
        self.mdfile = self.outfile.with_suffix('.tmp.md')
        self.title = title

    def cleanup(self):
        """Cleanup and generate markdown for each process"""
        citations = {}

        with self.mdfile.open('w') as fmd:
            for report in self.reports:
                report.prepare()
                # replace reference to citation indexes
                source = _replace_all(r'\[#REF: .+? #\]',
                                      partial(_replace_ref,
                                              citations=citations),
                                      report.source)

                fmd.write(source + '\n\n')

            if citations:
                fmd.write('# Reference\n')
                for cite, index in sorted(citations.items(),
                                          key=lambda item: int(item[1])):
                    fmd.write('[[{i}]: {cite}](){{.pyppl-report-reference '
                              'name=PYPPL-REF-{i}}}'.format(
                                  i=index, cite=b64decode(cite).decode()
                              ))

    def generate(self, standalone, template, filters, toc):
        """Generate the reports"""
        from pyppl import __version__ as pyppl_version
        from . import __version__ as report_version

        self.cleanup()
        template = template or DEFAULT_TEMPLATE
        if template and '/' not in template:
            template = HERE / 'templates' / template / 'template.html'

        ext = self.outfile.suffix.lower()
        if 'htm' not in ext and 'pdf' not in ext:
            raise ValueError('Only html and pdf format supported currently.')
        if not standalone and 'pdf' in ext:
            raise ValueError('pdf format has to be standalone.')

        metadata = [
            'pagetitle=%s' % self.title,
            'pyppl_version=%s' % pyppl_version,
            'report_version=%s' % report_version,
            'standalone=%s' % int(standalone),
            'indir=%s' % self.reports[0].rptfile.parent if self.reports else '',
            'outdir=%s' % self.outfile.parent,
            'pdf=%s' % bool('pdf' in ext)
        ]
        if toc > 0:
            metadata.append('toc=%d' % toc)
        mediadir = self.outfile.with_suffix('.files')
        srcpath = ['.', str(self.outfile.parent), str(mediadir),
                   str(Path(template).parent)]
        # add input directory
        srcpath += [str(self.reports[0].rptfile.parent)] if self.reports else []
        if mediadir.is_dir():
            rmtree(mediadir)
        metadata.extend(['mediadir=%s' % mediadir, 'template=%s' % template])

        if not standalone:
            # copy files to dir relative to the output file
            dest_staticdir = self.outfile.parent.joinpath('static')
            src_staticdir = Path(template).parent.joinpath('static')
            if not src_staticdir.is_dir():
                raise ValueError(
                    'Directory "static" not found in the template directory'
                )
            dest_staticdir.mkdir(parents=True, exist_ok=True)
            for staticfile in src_staticdir.rglob('*'):
                if staticfile.is_file():
                    copy_to_media(staticfile,
                                  dest_staticdir.joinpath(
                                      staticfile.relative_to(src_staticdir)
                                  ))

        kwargs = {
            'metadata': metadata,
            'read': 'markdown',
            'write': 'html5',
            'template': template,
            'filter': [HERE.joinpath('filters', filt + '.py')
                       if '_' not in filt
                       else filt
                       for filt in DEFAULT_FILTERS + (filters or [])],
            'self-contained': standalone,
            'resource-path': ':'.join(srcpath),
            '_raise': True,
            '_sep': 'auto',
            '_dupkey': True,
        }
        if 'pdf' not in ext:
            kwargs['output'] = self.outfile
            kwargs['_hold'] = True
            return pandoc(self.mdfile, **kwargs)

        kwargs['_pipe'] = True
        return pandoc(self.mdfile, **kwargs) | wkhtmltopdf(
            '-',
            _=self.outfile,
            _raise=True,
            _hold=True
        )
