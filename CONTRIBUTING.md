# Contributing

Guidelines for contributing are largely TBD, as this is a solo project at this
time.  Helpful items for setup and usage, including for forking, are below.

Follow existing conventions as best as possible.

Respect the CI and the CI will respect you.

- [One-time Setup](#one-time-setup)
- [Usage](#usage)
- [Conventions](#conventions)



# One-time Setup

### Python environment and VSCode Setup
In general the repo root should be added to the python path environment
variable.  Python automatically adds the directory of the module being executed
to the path, but elements of this project will not work unless the repo root is
in the path, and there are no modules that execute from the repo root.

Save this workspace, and edit the workspace settings (Ctrl+Shift+P >
`Preferences: Open Workspace Settings (JSON)`) and ADD the following to the
existing settings.  This workspace file should be the one opened everytime
evelopment is being started.  The workspace will need to be closed and reopened
after editing these workspace settings:
```json
{
	"settings": {
		"terminal.integrated.env.linux": {               // If developing on Linux
			"PYTHONPATH": "/path/to/repo/root"
		},
    "terminal.integrated.env.osx": {                 // If developing on Mac OSX
			"PYTHONPATH": "/path/to/repo/root"
		},
    "terminal.integrated.env.windows": {             // If developing on Windows
			"PYTHONPATH": "C:/path/to/repo/root",
			"WSLENV": "PYTHONPATH/l"                       // If using WSL in Windows
		}
	}
}
```


In Windows, one way of using a specific version of python is to open a cmd
prompt (not powershell) -- probably as admin -- and navigate to the desired
older python version's folder.  Then, run
`mklink python3.7.exe C:\path\to\python37\python.exe` to make a sym link for
python 3.7, for example.  Now this can be evoked with `python3.7`.

While the admin prompt is open, this might be the best time to install
required pacakges with pip (can use `pip3.7` in this example) as installing as a
user can cause some headaches...  It has been observed that after installing
`pytest-order` as admin, the first run of `pytest` needs to be run as an admin
to finish some sort of init it seems -- after that, it should work as a user.


To support pytest and pylint, add the following to `.vscode/settings.json` in
the root of the repo:
```json
{
    "python.linting.pylintEnabled": true,
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.pytestEnabled": true
}
```

In the `python.testing.pytestArgs` list above, it is likely desireable to put
some pytest args.  This does mean other args needs to be tested separately.
Without this, there may be inconsistent test results since some tests can be
mutually exclusive.


### CircleCI
If forking this project, CircleCI will need contexts setup.  See
`.circleci/config.yml` for the contexts needed; the contents should be mostly
obvious (e.g. `docker-hub-creds` is intended to define the user/pass env vars).
For the Docker Hub password, an access token should be created on the Security
page of your Docker Hub account profile.


### Config files and Unit Testing
While unit testing in CI uses mock configs, running unit testing locally expects
certain test environment configs to exist.  The following config sections/IDs
are required in their respective config files in order to run the relevant
unit tests:
- (TBD)

Note that some test WILL make API calls, so it will count against any rate
limiting or quotas.


### Asana account
This does access Asana to ensure full compatibility.  The API calls are limited
where reasonable, but it always does some API calls to ensure this will work
when deployed.

Some setup items are required.  For the account associated with the personal
access token used in `.secrets.conf` / CircleCI, the following must be done
once before the first tests are run:
- Create a workspace named `TEST Asana Extensions`

Running tests will create and delete projects, sections, and tasks starting
with `TEST` and ending in a UUID.  If there is a critical tester error, some of
these may remain.  If confident that no tests are running, any remaining items
can be deleted to keep workspace empty.

If these docs are out of date, the data in `/tests/unit/asana/tester_data.py`
holds all of these constants.  The exceptions raised when running relevant tests
will also provided guidance on what is required.



# Usage

## Logger
Balancing readability against performance, the pylint warnings
`logging-fstring-interpolation` and `logging-not-lazy` are disabled.  The
intention is largely for this to apply to warnings and more severe log levels
as well as anything that would be low overhead.  It is recommended that anything
info or debug level, especially if there are many calls or each call is an
time-expensive interpolation to use the
`logger.debug('log %(name)s', {'name'=name_var})` sort of methods instead so
that the interpolation is only executed when that logger level is enabled.


## Workflows
Before pushing, it is recommended to run through the checks that CircleCI will
run.  In short, this is largely running from the repo root:
```
python -m pylint asana_extensions
python -m pylint tests
python -m pylint ci_support
python -m pylint conftest

python ci_support/dir_init_checker.py asana_extensions
python ci_support/dir_init_checker.py ci_support
python ci_support/dir_init_checker.py tests

python ci_support/version_checker.py dev-required

python -m pytest --cov=asana_extensions
python -m pytest --cov=asana_extensions --cov-append --run-no-warnings-only -p no:warnings
```

The `version_checker.py` could be run with different args, but during
development, it is most likely that `dev-required` is the correct arg.

When running `pytest` without the `-p no:warnings` option, the warnings provided
may be from `pytest`, but may also be from other packages, such as deprecation
warnings from `asana`.



# Conventions

## Versioning
See the top of `/asana_extensions/version.py` for information on the version
information.  The general idea is that development versions must have a `+dev`
appended while stable branch commits must not have this.  `release/*` branches
are where this is allowed to be either to allow for the transition.
