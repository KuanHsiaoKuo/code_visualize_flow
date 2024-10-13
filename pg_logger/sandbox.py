import sys
import types

from .exceptions import RawInputException, MouseInputException
from .constants import is_python3, TRY_ANACONDA_STR, ALLOWED_STDLIB_MODULE_IMPORTS, OTHER_STDLIB_WHITELIST, \
    BUILTIN_IMPORT, input_string_queue


def open_wrapper(*args):
    if is_python3:
        raise Exception('''open() is not supported by Python Tutor.
Instead use io.StringIO() to simulate a file.
Example: http://goo.gl/uNvBGl''' + TRY_ANACONDA_STR)
    else:
        raise Exception('''open() is not supported by Python Tutor.
Instead use StringIO.StringIO() to simulate a file.
Example: http://goo.gl/Q9xQ4p''' + TRY_ANACONDA_STR)


def raw_input_wrapper(prompt=''):
    if input_string_queue:
        input_str = input_string_queue.pop(0)

        # write the prompt and user input to stdout, to emulate what happens
        # at the terminal
        sys.stdout.write(str(prompt))  # always convert prompt into a string
        sys.stdout.write(input_str + "\n")  # newline to simulate the user hitting Enter
        return input_str
    raise RawInputException(str(prompt))  # always convert prompt into a string


# Python 2 input() does eval(raw_input())
def python2_input_wrapper(prompt=''):
    if input_string_queue:
        input_str = input_string_queue.pop(0)

        # write the prompt and user input to stdout, to emulate what happens
        # at the terminal
        sys.stdout.write(str(prompt))  # always convert prompt into a string
        sys.stdout.write(input_str + "\n")  # newline to simulate the user hitting Enter
        return eval(input_str)  # remember to eval!
    raise RawInputException(str(prompt))  # always convert prompt into a string


def mouse_input_wrapper(prompt=''):
    if input_string_queue:
        return input_string_queue.pop(0)
    raise MouseInputException(prompt)


# create a more sensible error message for unsupported features
def create_banned_builtins_wrapper(fn_name):
    def err_func(*args):
        raise Exception("'" + fn_name + "' is not supported by Python Tutor." + TRY_ANACONDA_STR)

    return err_func


# Restrict imports to a whitelist
def __restricted_import__(*args):
    # filter args to ONLY take in real strings so that someone can't
    # subclass str and bypass the 'in' test on the next line
    args = [e for e in args if type(e) is str]

    all_allowed_imports = sorted(ALLOWED_STDLIB_MODULE_IMPORTS + OTHER_STDLIB_WHITELIST)
    if is_python3:
        all_allowed_imports.remove('StringIO')
    else:
        all_allowed_imports.remove('typing')

    if args[0] in all_allowed_imports:
        imported_mod = BUILTIN_IMPORT(*args)
        # somewhat weak protection against imported modules that contain one
        # of these troublesome builtins. again, NOTHING is foolproof ...
        # just more defense in depth :)
        #
        # unload it so that if someone attempts to reload it, then it has to be
        # loaded from the filesystem, which is (supposedly!) blocked by setrlimit
        for mod in ('os', 'sys', 'posix', 'gc'):
            if hasattr(imported_mod, mod):
                delattr(imported_mod, mod)

        return imported_mod
    else:
        # original error message ...
        # raise ImportError('{0} not supported'.format(args[0]))

        # 2017-12-06: added a better error message to tell the user what
        # modules *can* be imported in python tutor ...
        ENTRIES_PER_LINE = 6

        lines_to_print = []
        # adapted from https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        for i in range(0, len(all_allowed_imports), ENTRIES_PER_LINE):
            lines_to_print.append(all_allowed_imports[i:i + ENTRIES_PER_LINE])
        pretty_printed_imports = ',\n  '.join([', '.join(e) for e in lines_to_print])

        raise ImportError(
            '{0} not found or not supported\nOnly these modules can be imported:\n  {1}{2}'.format(args[0],
                                                                                                   pretty_printed_imports,
                                                                                                   TRY_ANACONDA_STR))
