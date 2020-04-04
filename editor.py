import locale
import os.path
import subprocess
import tempfile
from distutils.spawn import find_executable


def default_editors():
    return ('editor', 'vim', 'emacs','nano','code')

def editor_args(editor):
    if editor in ['vim', 'gvim', 'vim.basic', 'vim.tiny']:
        return ['-f', '-o']

    elif editor == 'emacs':
        return ['-nw']

    elif editor == 'gedit':
        return ['-w', '--new-window']

    elif editor == 'nano':
        return ['-R']

    elif editor == 'code':
        return ["-w", "-n"]

    return []

def get_editor():
    editor = os.environ.get('VISUAL') or os.environ.get('EDITOR')
    if editor:
        return editor

    for editor in default_editors():
        path = find_executable(editor)
        if path is not None:
            return path

    print("Unable to find an editor on this system.Please consider setting your $EDITOR variable")


def edit(filename=None, contents=None, suffix=''):
    editor = get_editor()
    args = [editor] + editor_args(os.path.basename(os.path.realpath(editor)))

    if filename is None:
        tmp = tempfile.NamedTemporaryFile(suffix=suffix)
        filename = tmp.name

    args += [filename]

    proc = subprocess.Popen(args, close_fds=True, stdout=None)
    proc.communicate()

    with open(filename, mode='rb') as f:
        return f.read()


def _get_editor(ns):
    print(get_editor())


def _edit(ns):
    contents = ns.contents
    if contents is not None:
        contents = contents.encode(locale.getpreferredencoding())
    print(edit(filename=ns.path, contents=contents))
