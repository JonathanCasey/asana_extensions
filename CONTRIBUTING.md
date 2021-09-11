# Contributing

Guidelines for contributing are largely TBD, as this is a solo project at this
time.  Helpful items for setup and usage, including for forking, are below.

Follow existing conventions as best as possible.

Respect the CI and the CI will respect you.

- [One-time Setup](#one-time-setup)
- [Usage](#usage)



# One-time Setup

### Python environment in VSC
To support pytest, add the following to `.vscode/settings.json` in the root of
the repo:
```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.pytestEnabled": true,
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}/asana_extensions;${env:PYTHONPATH}",
    }
}
```

Also create a `.env` file in the root of the repo with the following line:
```
PYTHONPATH=C:\path\to\the\repo\root;${PYTHONPATH}
```

Note that in the above, if not on Windows, the semicolon `;` separator should be
replaced with a colon `:`.

This only works when opening the folder.  If opened as part of a multi-folder
project, the `"terminal.integrated.env.windows"` will not be applied.  While not
the most elegant, running
`$env:PYTHONPATH = 'C:\path\to\repo\asana_extensions;' + $env:PYTHONPATH` will
do the trick (the last part for the plus `+` sign and onwards can be omitted if
it is not set at all yet).


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

The `env` for each of those must be `test`.

Note that some test WILL make API calls, so it will count against any rate
limiting or quotas.



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
pytest
```
