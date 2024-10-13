import bdb
import json

from pg_logger.pg_logger import PGLogger


# the MAIN meaty function!!!
def exec_script_str(script_str, raw_input_lst_json, options_json, finalizer_func):
    if options_json:
        options = json.loads(options_json)
    else:
        # defaults
        options = {'cumulative_mode': False,
                   'heap_primitives': False, 'show_only_outputs': False}

    py_crazy_mode = ('py_crazy_mode' in options and options['py_crazy_mode'])

    logger = PGLogger(options['cumulative_mode'], options['heap_primitives'], options['show_only_outputs'],
                      finalizer_func,
                      crazy_mode=py_crazy_mode)

    # TODO: refactor these NOT to be globals
    global input_string_queue
    input_string_queue = []
    if raw_input_lst_json:
        # TODO: if we want to support unicode, remove str() cast
        input_string_queue = [str(e) for e in json.loads(raw_input_lst_json)]

    try:
        logger._runscript(script_str)
    except bdb.BdbQuit:
        pass
    finally:
        logger.finalize()


# disables security check and returns the result of finalizer_func
# WARNING: ONLY RUN THIS LOCALLY and never over the web, since
# security checks are disabled
#
# [optional] probe_exprs is a list of strings representing
# expressions whose values to probe at each step (advanced)
def exec_script_str_local(script_str, raw_input_lst_json, cumulative_mode, heap_primitives, finalizer_func,
                          probe_exprs=None, allow_all_modules=False):
    logger = PGLogger(cumulative_mode, heap_primitives, False, finalizer_func,
                      disable_security_checks=True,
                      allow_all_modules=allow_all_modules,
                      probe_exprs=probe_exprs)

    # TODO: refactor these NOT to be globals
    global input_string_queue
    input_string_queue = []
    if raw_input_lst_json:
        # TODO: if we want to support unicode, remove str() cast
        input_string_queue = [str(e) for e in json.loads(raw_input_lst_json)]

    try:
        logger._runscript(script_str)
    except bdb.BdbQuit:
        pass
    finally:
        return logger.finalize()
