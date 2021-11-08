# Setup

These are the one-time setup items to be completed prior to first run.

Was developed on python 3.10.  It requires at least python 3.7.


## Config files
The config files in `/config/stubs` must be copied to `/config` with the
`.default` suffix dropped; the rest of the filename must remain unchanged (e.g.
`/config/stubs/rules.conf.default` -> `/config/rules.conf`).

### config/.secrets.conf
These are any items that should be kept confidential that are not also needed in
a shell environment.  See the `.default` stub file for directions on what is
required.


### config/.secrets.env
This is only used in the Linux/Ubuntu environment when using the `/bin` scripts
at this time.

This should be a list of credentials to be imported as environment variables
for the shell scripts, as well as for python scripts to parse.  Respect the
quote usage as shown below and in the stubs.

To fill out the section, see an existing setup or find someone associated with
this project.

For the `EMAIL_ADMIN_RECIPIENT_NAME_AND_ADDR`, this should be the person (most
likely you) who would be responsible for handling execution errors, as well as
anyone who should know that the monitoring did not report properly.  As with all
in the `EMAIL_*_NAME_AND_ADDR` naming convention, this does support the
`Display Name <email@address.com>` format, and multiple recipients can be
specified provided that they are comma separated.

As an example of using with a Gmail account:
```ini
EMAIL_SERVER_HOST="smtp.gmail.com"
EMAIL_SERVER_PORT=587
EMAIL_USERNAME="your-gmail-login-name"
EMAIL_PASSWORD="your-gmail-login-password"
EMAIL_SENDER_NAME_AND_ADDR="name/address to send from, likely your email"
EMAIL_ADMIN_RECIPIENT_NAME_AND_ADDR="name/address to send errors to, likely yours"
```


### config/asana_extensions.env
This is only used in the Linux/Ubuntu environment when using the `/bin` scripts
at this time.

These are non-sensitive configuration variables needed to be used at least in
the shell environment.

The `PYTHON_BIN` would be the path to the desired python version to use, such
as `"/usr/bin/python3"`.  If using in Windows (not that it is applicable here), it
would be a path such as `"C:/Program Files/Python37"`.


### config/rules.conf
If using the rules module, this would hold all rules to be executed.

There are 2 example sections given in the file:
- Moving tasks within a user task list
- Moving tasks within a project

Each section can be duplicated and edited as many times as needed.  The names of
the sections are not important and are for user's own reference.  Unused
sections and/or keys should be deleted or commented out.



## Prereqs

### Python
These are all in the `/requirements.txt` file.  This is as simple as executing:
```bash
cd /path/to/repo/root
pip install -r requirements.txt
```


### Ubuntu
If using Ubuntu with the `/bin` scripts, they have some additional package
dependencies:
- rsyslog
- sendemail

If any are missing, these should be as easy as `sudo apt-get install <package>`.



# System Config

### Ubuntu: Rsyslog
For `rsyslog`, it expected that it can use `local7` as the priority to route to
a config file.  If a lower value must be used, it can be changed in the
`/bin/asana_extension_exec_all.sh` file.

To configure rsyslog, first a file in `/etc/rsyslog.d` should be edited, such as
`99-asana-extensions.conf`.  The template below is an example, but could be
omitted; the important piece is the `local7.*` line (if omitting the template,
the `;preciseLevelFormat` at the end of the line must be removed):
```
template(name="preciseLevelFormat" type="list") {
    property(name="timestamp" dateFormat="rfc3339")
    constant(value=" ")
    property(name="syslogseverity-text" caseconversion="upper")
    constant(value=" ")
    property(name="hostname")
    constant(value=" ")
    property(name="syslogtag")
    property(name="msg" spifno1stsp="on" )
    property(name="msg" droplastlf="on" )
    constant(value="\n")
    }

local7.*                /var/log/asana_extensions.log;preciseLevelFormat
```

Then the appropriate system command:
```bash
sudo systemctl restart rsyslog.service
or
sudo service rsyslogd restart
```


## Scheduling
The real value in this project is running it automatically.  This is not
directly covered by this project, but is a setup item left to the user to
perform on the executing system.

### Ubuntu: cron
A really simply method is to use `cron`.  After executing `crontab -e`, the
following could be added:
```ini
# Run everyday at 1am and log result
0 1 * * * /path/to/repo/bin/asana_extensions_exec_all.sh -l
```


### Ubuntu: systemd
It is also possible to use `systemd` by creating service files, as this is the
intended, more robust method for running cron jobs.  This would require creating
a `.service` file and a `.timer` file.  Something as simple as the following
should work (untested):
```ini
# vi: ft=dosini

# asana_extensions.service

[Unit]
Description=Periodic execution of asana extensions
After=network-pre.target
# Ensure it will always retry
StartLimitBurst=0

[Service]
WorkingDirectory=/path/to/repo
ExecStart=/path/to/repo/bin/asana_extensions_exec_all.sh -l

Restart=no

StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=asana-extensions
```

```ini
# vi: ft=dosini

# asana_extensions.timer

[Unit]
Description=Periodic execution of asana extensions

[Timer]
# OnCalendar may have multiple entries; format per
# https://www.freedesktop.org/software/systemd/man/systemd.time.html#Calendar%20Events
# Every day at 1am
OnCalendar=*-*-* 01:00:00
AccuracySec=1
Persistent=true

[Install]
WantedBy=default.target
```

These should be saved to `/etc/systemd/system` and it should NOT have the
executable flag in its file permissions.  Finally, the following shell commands
will get it started (assuming files named as suggested above):
```bash
sudo systemctl daemon-reload
sudo systemctl enable asana_extensions.timer
```

Status can be monitored with `journalctl -f -u asana_extensions.service`.


It may be helpful to prepend a `-u` to the `script` var in the
`/bin/asana_extension_exec_all.sh` file so logger messages are not buffered to
the point that it seems they aren't being logged.


### Windows: Task Scheduler
There should be a way to set this up with "Task Scheduler" in Windows.  See
Windows docs for more info.
