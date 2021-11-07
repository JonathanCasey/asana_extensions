# Usage

See [setup](setup.md) for required setup prior to first use.


## Executing
Main scripts intended for execution are in the root of `asana_extensions`.
These need to be run from the repo root to make paths work correctly.  E.g.:
```bash
cd /path/to/repo/root
python -m asana_extensions
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
versions such as 3.7 work at this time.  Versions earlier than python 3.7 are
known to not work.


### Ubuntu
On Linux, at least on Ubuntu, there is a shell script wrapper for the most
common case.  This can be run via `./bin/asana_extensions_exec_all.sh -l`.  The
`-l` can be omitted, but it will log activity and email fatal error alerts if
`rsyslog` has been configured correctly.

When first testing, the `script_opts` are recommended to be changed to remove
the `-e` so it runs in test mode and add `-l info` to monitor how it goes.

##### Monitoring log output
There is also a log written to the location configured via `rsyslog` when the
`-l` arg us used with the `/bin/asana_extensions_exec_all.sh` script.  This can
be monitored with `tail -f /path/to/log/file.log` for live changes.

This can be piped to show only messages with certain keywords by appending
` | grep <keyword>`, where `<keyword>` is the filter of interest.  Another
powerful option is to invert match to exclude terms, such as `INFO` with
` | grep -i -v info` (`-i` matches case insensitive).

Note that, at this time, debug and info level messages are logged as `info` and
warning and error level messages are logged as `warning`.  This is planned to be
improved in the future.  In the meantime, the contents of the message does still
indicate the correct level, so that can be reviewed.

All info and lower messages are written to the log file before all the warning
and higher messages (probably because of the order of `logger` calls in the
shell script).  This should also get improved in the future at the same time as
resolving log levels as noted above.



## Asana Support and Deprecations
This project aims to stay up to date with API deprecations.  During the period
of time between deprecation and removal of API items, this project may opt to
fully switch away from deprecated features.

At this time, the following are deprecated via the API, but this project has
already migrated support and no longer supports the old methodology:
- `new_user_task_lists`: This project now supports the "User Task List v2".
      Support for the prior version user task list has been dropped.  For more
      info, see
      [this Asana forum thread](https://forum.asana.com/t/update-on-our-planned-api-changes-to-user-task-lists-a-k-a-my-tasks/103828).
