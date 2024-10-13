import re
import sys
import types
import pg_encoder
from .exceptions import RawInputException
from .constants import IGNORE_VARS, is_python3, input_string_queue


# copied-pasted from translate() in https://github.com/python/cpython/blob/2.7/Lib/fnmatch.py
def globToRegex(pat):
    """Translate a shell PATTERN to a regular expression.
    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            res = res + '.*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + '\Z(?ms)'


def compileGlobMatch(pattern):
    # very important to use match and *not* search!
    return re.compile(globToRegex(pattern)).match

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

# test globToRegex and compileGlobMatch
'''
for e in ('_*', '__*', '__*__', '*_$'):
    stuff = compileGlobMatch(e)
    for s in ('_test', 'test_', '_test_', '__test', '__test__'):
        print(e, s, stuff(s) is not None)
'''

'''
2013-12-26

Okay, what's with this f_valuestack business?

If you compile your own CPython and patch Objects/frameobject.c to add a
Python accessor for f_valuestack, then you can actually access the value
stack, which is useful for, say, grabbbing the objects within
list/set/dict comprehensions as they're being built. e.g., try:

    z = [x*y for x in range(5) for y in range(5)]

Note that on pythontutor.com, I am currently running custom-compiled
versions of Python-2.7.6 and Python-3.3.3 with this f_valuestack hack.
Unless you run your own custom CPython, you won't get these benefits.
- update as of 2018-06-16: I don't think the above has been true for a while


Patch:

 static PyObject *
 frame_getlineno(PyFrameObject *f, void *closure)
 {
     return PyLong_FromLong(PyFrame_GetLineNumber(f));
 }

+// copied from Py2crazy, which was for Python 2, but let's hope this still works!
+static PyObject *
+frame_getvaluestack(PyFrameObject* f) {
+    // pgbovine - TODO: will this memory leak? hopefully not,
+    // since all other accessors seem to follow the same idiom
+    PyObject* lst = PyList_New(0);
+    if (f->f_stacktop != NULL) {
+        PyObject** p = NULL;
+        for (p = f->f_valuestack; p < f->f_stacktop; p++) {
+            PyList_Append(lst, *p);
+        }
+    }
+
+    return lst;
+}
+
 /* Setter for f_lineno - you can set f_lineno from within a trace function in
  * order to jump to a given line of code, subject to some restrictions.  Most
  * lines are OK to jump to because they don't make any assumptions about the
@@ -368,6 +384,11 @@

 static PyGetSetDef frame_getsetlist[] = {
     {"f_locals",        (getter)frame_getlocals, NULL, NULL},
     {"f_lineno",        (getter)frame_getlineno,
                     (setter)frame_setlineno, NULL},
     {"f_trace",         (getter)frame_gettrace, (setter)frame_settrace, NULL},
+
+    // pgbovine
+    {"f_valuestack",(getter)frame_getvaluestack,
+                    (setter)NULL /* don't let it be set */, NULL},
+
     {0}
 };
'''


# at_global_scope should be true only if 'frame' represents the global scope
def get_user_globals(frame, at_global_scope=False):
    d = filter_var_dict(frame.f_globals)

    # don't blurt out all of f_valuestack for now ...
    '''
    if at_global_scope and hasattr(frame, 'f_valuestack'):
      for (i, e) in enumerate(frame.f_valuestack):
        d['_tmp' + str(i+1)] = e
    '''

    # print out list objects being built up in Python 2.x list comprehensions
    # (which don't have its own special <listcomp> frame, sadly)
    if not is_python3 and hasattr(frame, 'f_valuestack'):
        for (i, e) in enumerate([e for e in frame.f_valuestack if type(e) is list]):
            d['_tmp' + str(i + 1)] = e

    # also filter out __return__ for globals only, but NOT for locals
    if '__return__' in d:
        del d['__return__']
    return d


def get_user_locals(frame):
    ret = filter_var_dict(frame.f_locals)
    # don't blurt out all of f_valuestack for now ...
    '''
    if hasattr(frame, 'f_valuestack'):
      for (i, e) in enumerate(frame.f_valuestack):
        ret['_tmp' + str(i+1)] = e
    '''

    # special printing of list/set/dict comprehension objects as they are
    # being built up incrementally ...
    f_name = frame.f_code.co_name
    if hasattr(frame, 'f_valuestack'):
        # print out list objects being built up in Python 2.x list comprehensions
        # (which don't have its own special <listcomp> frame, sadly)
        if not is_python3:
            for (i, e) in enumerate([e for e in frame.f_valuestack
                                     if type(e) is list]):
                ret['_tmp' + str(i + 1)] = e

        # for dict and set comprehensions, which have their own frames:
        if f_name.endswith('comp>'):
            for (i, e) in enumerate([e for e in frame.f_valuestack
                                     if type(e) in (list, set, dict)]):
                ret['_tmp' + str(i + 1)] = e

    return ret


def filter_var_dict(d):
    ret = {}
    for (k, v) in d.items():
        if k not in IGNORE_VARS:
            ret[k] = v
    return ret


# yield all function objects locally-reachable from frame,
# making sure to traverse inside all compound objects ...
def visit_all_locally_reachable_function_objs(frame):
    for (k, v) in get_user_locals(frame).items():
        for e in visit_function_obj(v, set()):
            if e:  # only non-null if it's a function object
                assert type(e) in (types.FunctionType, types.MethodType)
                yield e


# TODO: this might be slow if we're traversing inside lots of objects:
def visit_function_obj(v, ids_seen_set):
    v_id = id(v)

    # to prevent infinite loop
    if v_id in ids_seen_set:
        yield None
    else:
        ids_seen_set.add(v_id)

        typ = type(v)

        # simple base case
        if typ in (types.FunctionType, types.MethodType):
            yield v

        # recursive cases
        elif typ in (list, tuple, set):
            for child in v:
                for child_res in visit_function_obj(child, ids_seen_set):
                    yield child_res

        elif typ == dict or pg_encoder.is_class(v) or pg_encoder.is_instance(v):
            contents_dict = None

            if typ == dict:
                contents_dict = v
            # warning: some classes or instances don't have __dict__ attributes
            elif hasattr(v, '__dict__'):
                contents_dict = v.__dict__

            if contents_dict:
                for (key_child, val_child) in contents_dict.items():
                    for key_child_res in visit_function_obj(key_child, ids_seen_set):
                        yield key_child_res
                    for val_child_res in visit_function_obj(val_child, ids_seen_set):
                        yield val_child_res

        # degenerate base case
        yield None
