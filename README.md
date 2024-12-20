# Code Visualize Flow: Enhanced Code Execution Visualization

## How to Run

```python
pip
install - r
requirements.txt
python
bottle_server.py  # python 3.x (x <=9)
python
flask_server.py  # python 3.x (x > 9)
```

## Raw:

- [pathrise-python-tutor/v3/docs/developer-overview.md at master · pathrise-eng/pathrise-python-tutor](https://github.com/pathrise-eng/pathrise-python-tutor/blob/master/v3/docs/developer-overview.md)

## Design Philosophy of PGLogger

The `PGLogger` class is crafted to track and log Python programs' execution process, typically for educational or
analytical tools. By capturing the dynamic behavior of running code, such as variable changes, function call stacks, and
exception information, PGLogger acts as a simplified debugger. It is designed to provide an insightful, interactive
experience into understanding Python code execution.

### Key Features

1. **Code Tracing and Execution Logging**:
    - Utilizes the `bdb.Bdb` class framework to monitor the execution flow of Python code.
    - Logs events related to function calls, line executions, returns, and exceptions.

2. **Output Capturing**:
    - Redirects and captures standard output (`sys.stdout`) to create faux streams for different modules, allowing
      separate streams per module.

3. **Security Management**:
    - Implements a basic sandbox by restricting file descriptor access and blocking potentially dangerous built-ins and
      module imports.

4. **State Management**:
    - Maintains information about stack frames, global variables, and heap objects.
    - Outputs this data in a structured format for visualization and analysis.

5. **Custom Module Support**:
    - Executes code from custom modules and imports their content to help set the initial environment and context before
      running user scripts.

### Implementation Strategies

- **Initialization**: In the `__init__` method, PGLogger sets up its attributes, such as control flags for cumulative
  mode, safety assertions, modular output streams, etc.

- **Bdb Method Overrides**: Core methods like `user_call`, `user_line`, `user_return`, and `user_exception` are
  overridden to finely control the execution trace collection process.

- **Execution Management**: The `interaction` method centrally handles the processing of all execution events, updating
  stack information and managing exceptions and user-defined breakpoints.

- **Termination Control**: Methods `force_terminate` and `finalize` define termination logic to end script execution
  gracefully upon reaching step limits or encountering infinite loops.

### Design Motivation

- **User-Friendly Interaction**: Aimed at educational use, providing a clear view of program execution and behavior.
- **Security and Isolation**: Ensures safe tracing by implementing simple sandbox restrictions.
- **Flexibility and Extensibility**: Easily adaptable through custom modules and variables, enabling extended usage.

### ASCII Flow Design Diagram

Below is a simplified representation of the PGLogger's design flow:

```
+---------------------+
|    Initialize       |
|                     |
| - Set control flags |
| - Prepare stdout    |
|   streams           |
+---------+-----------+
          |
          v
+---------------------+
|      Execute        |
|                     |
| - Load user script  |
| - Override Bdb      |
|   methods           |
+---------+-----------+
          |
          v
+---------------------+
| Interaction         |
| - Handle events     |
| - Update stack info |
| - Check exceptions  |
+---------+-----------+
          |
          v
+---------------------+
|  Termination        |
| - Force quit        |
| - Call finalizer    |
|   if needed         |
+---------------------+
```

This diagram outlines the key execution phases handled by PGLogger, illustrating an overview of its process from
initialization through execution to termination.

## Why Not Support Pandas/Numpy in Code Visualization Flow

While using code visualization tools like Python Tutor can be highly beneficial for understanding and illustrating
Python code execution, there are limitations when it comes to supporting certain libraries, such as Pandas and Numpy.
These libraries, although powerful and widely used for data manipulation and numerical computations, rely extensively on
C extensions and complex data structures.

```shell
<frozen importlib._bootstrap>:228: RuntimeWarning: Cython module failed to patch module with custom type
```

### Key Reasons:

1. **Complexity of C Extensions**: Pandas and Numpy utilize C and Cython code to achieve high performance and
   efficiency, which are not easily simulated or executed in the restricted Python environment that most visualization
   tools provide.

2. **Resource Constraints**: These libraries require significant computational resources and optimized environments that
   code visualization tools often cannot offer. This includes handling large datasets and matrix operations efficiently.

3. **Runtime Environment Limitations**: The runtime environments used by such tools simplify Python’s execution model to
   allow step-by-step visualization. This simplification often cannot accommodate the advanced operations and
   optimizations made available by Pandas and Numpy.

4. **Maintenance Overhead**: Keeping a visualization tool in sync with the fast-evolving features and optimizations of
   these libraries would be challenging and resource-intensive.

For in-depth analysis and visual debugging of code that involves Pandas or Numpy, it's recommended to use local tools
like Jupyter Notebooks, where the full power of these libraries can be leveraged with robust supporting infrastructure.

