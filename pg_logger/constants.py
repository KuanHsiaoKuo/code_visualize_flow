import sys
import re
import types

MAX_EXECUTED_LINES = 1000
# DEBUG = False
DEBUG = True
BREAKPOINT_STR = '#break'
# if a line starts with this string, then look for a comma-separated
# list of variables after the colon. *hide* those variables in da trace
#
# 2018-06-17:
# - now supports unix-style shell globs using the syntax in
#   https://docs.python.org/3/library/fnmatch.html so you can write things
#   like '#pythontutor_hide: _*' to hide all private instance variables
# - also now filters class and instance fields in addition to top-level vars
PYTUTOR_HIDE_STR = '#pythontutor_hide:'
# 2018-06-17: a comma-separated list of types that should be displayed *inline*
# like primitives, with their actual values HIDDEN to save space. for details
# of what types are legal to specify, see:
# pg_encoder.py:should_inline_object_by_type()
# - also accepts shell globs, just like PYTUTOR_HIDE_STR
PYTUTOR_INLINE_TYPE_STR = '#pythontutor_hide_type:'

CLASS_RE = re.compile('class\s+')
# TODO: use the 'six' package to smooth out Py2 and Py3 differences
is_python3 = (sys.version_info[0] == 3)
TRY_ANACONDA_STR = '\n\nYou can also try "Python 3.6 with Anaconda (experimental)",\nwhich is slower but lets you import many more modules.\n'


# From http://coreygoldberg.blogspot.com/2009/05/python-redirect-or-turn-off-stdout-and.html
class NullDevice():
    def write(self, s):
        pass


# ugh, I can't figure out why in Python 2, __builtins__ seems to
# be a dict, but in Python 3, __builtins__ seems to be a module,
# so just handle both cases ... UGLY!
if type(__builtins__) is dict:
    BUILTIN_IMPORT = __builtins__['__import__']
else:
    assert type(__builtins__) is types.ModuleType
    BUILTIN_IMPORT = __builtins__.__import__

# whitelist of module imports
ALLOWED_STDLIB_MODULE_IMPORTS = ['math', 'random', 'time', 'datetime',
                                 'functools', 'itertools', 'operator', 'string',
                                 'collections', 're', 'json',
                                 'heapq', 'bisect', 'copy', 'hashlib', 'typing',
                                 # the above modules were first added in 2012-09
                                 # and then incrementally appended to up until
                                 # 2016-ish (see git blame logs)

                                 # added these additional ones on 2018-06-15
                                 # after seeing usage logs of what users tried
                                 # importing a lot but we didn't support yet
                                 # (ignoring imports that heavily deal with
                                 # filesystem, networking, or 3rd-party libs)
                                 '__future__', 'cmath', 'decimal', 'fractions',
                                 'pprint', 'calendar', 'pickle',
                                 'types', 'array',
                                 'locale', 'abc',
                                 'doctest', 'unittest',
                                 ]

PRE_IMPORT_MODULES = ['pandas', 'numpy', 'asyncio']
# allow users to import but don't explicitly import it since it's
# already been done above
OTHER_STDLIB_WHITELIST = ['StringIO', 'io'] + PRE_IMPORT_MODULES

# blacklist of builtins
BANNED_BUILTINS = []  # 2018-06-15 don't ban any builtins since that's just security by obscurity
# we should rely on other layered security mechanisms

# old banned built-ins prior to 2018-06-15
# BANNED_BUILTINS = ['reload', 'open', 'compile',
#                   'file', 'eval', 'exec', 'execfile',
#                   'exit', 'quit', 'help',
#                   'dir', 'globals', 'locals', 'vars']
# Peter says 'apply' isn't dangerous, so don't ban it

IGNORE_VARS = set(('__builtins__', '__name__', '__exception__', '__doc__', '__package__'))

# queue of input strings passed from either raw_input or mouse_input
input_string_queue = []
