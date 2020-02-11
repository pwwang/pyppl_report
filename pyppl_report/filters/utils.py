"""Some utilities for pyppl_report"""
from hashlib import md5
from pathlib import Path
from shutil import copyfile

def md5sum(filepath):
    """Get the md5sum of a file"""
    if not filepath or not Path(filepath).exists():
        return None
    return md5(Path(filepath).read_bytes()).hexdigest()

def md5str(string):
    """Get the md5 of a string"""
    return md5(string.encode('utf-8')).hexdigest()

def copy_to_media(filepath, destfile):
    """Copy files to mediadir, check their md5sum"""

    dest_md5 = md5sum(destfile)
    if dest_md5 and dest_md5 == md5sum(filepath):
        return destfile

    destfile = Path(destfile)
    # just overwrite asset files
    if dest_md5 and destfile.suffix not in ('.js', '.css', '.woff2', '.woff',
                                            '.eot', '.ttf'):
        candfiles = list(destfile.parent.glob("[[]*[]]" + destfile.name))
        if not candfiles:
            destfile = destfile.parent / ('[1]' + destfile.name)
        else:
            maxnum = max(
                int(cfile.name.split(']')[0][1:]) for cfile in candfiles)
            destfile = destfile.parent / ('[{}]{}'.format(
                maxnum + 1, destfile.name))

    destfile.parent.mkdir(exist_ok=True, parents=True)
    if destfile.is_symlink(): # pragma: no cover
        destfile.unlink()
    copyfile(str(filepath), str(destfile))
    return destfile
