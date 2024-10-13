# Start of Selection
# These imports are specifically placed in __init__.py for the following reasons:
# 1. It simplifies the import process for users of this package.
# 2. It provides a clean and consistent API for the package.
# 3. It allows users to import these functions and classes directly from the package.
#
# By doing this, users can now import and use these components like this:
# from pg_logger import exec_script_str, exec_script_str_local, PGLogger
#
# This approach reduces the need for users to know the internal structure of the package,
# making it more user-friendly and easier to use.

from .core_executor import exec_script_str, exec_script_str_local
from .pg_logger import PGLogger
# Support interactive user input by:
#
# 1. running the entire program up to a call to raw_input (or input in py3),
# 2. bailing and returning a trace ending in a special 'raw_input' event,
# 3. letting the web frontend issue a prompt to the user to grab a string,
# 4. RE-RUNNING the whole program with that string added to input_string_queue,
# 5. which should bring execution to the next raw_input call (if
#    available), or to termination.
# Repeat until no more raw_input calls are encountered.
# Note that this is mad inefficient, but is simple to implement!

# VERY IMPORTANT -- set random seed to 0 to ensure deterministic execution:
import random

random.seed(0)