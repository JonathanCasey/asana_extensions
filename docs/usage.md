# Usage

See [setup](setup.md) for required setup prior to first use.


## Executing
Main scripts intended for execution are in the root of `asana_extensions`.
These need to be run from the repo root to make paths work correctly.  E.g.:
```bash
cd /path/to/repo/root
python asana_extensions/main.py
```

Use the above with `--help` to get the most updated list of command line (CLI)
arguments.  As of writing, these are:

- `-e`/`--execute`: Flag to fully perform actions, provided it is not configured
      for test mode elsewhere, such as in an individual rule config.  Omitting
      will default to test mode for everything.
- `-l`/`--log-level <level>`: The log level to use for logging messages.  This
      will log all messages at the specified level and more severe.  See the
      help message or
      [python logging docs](https://docs.python.org/3/library/logging.html#logging-levels)
      for full list of options.
- `-m`/`--modules <mod1> <mod2> ...`: The space-separated list of modules to run
      in this invocation.  Omitting will result in nothing being run.  See the
      help message for full and latest list of modules options, but they should
      be:
  - `all`: Run all modules.
  - `rules`: Run the rules module.


This project is developed with python 3.10, but it is very likely that earlier
versions such as 3.6 and 3.7 work at this time.
