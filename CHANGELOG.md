# Change log
All notable changes to this project will be documented in this file.  This
should be succinct, but still capture "what I would want co-developers to know".

This project adheres to [Semantic Versioning](http://semver.org/), but reserves
the right to do whatever the hell it wants with pre-release versioning.

Observe format below, particularly:
- version headings (with links)
- diff quick link(s) under each version heading
- project section (dir) sub-headings for each version, alphabetical with
      `Project & Toolchain` at top, then all subpackages/modules, then docs.
- type-of-change prefix for each change line
- each change only a line or 2, maybe 3 (sub-lists allowed in select cases)
- issue (not PR) link for every change line
- milestones, projects, issues, and PRs with issue linkage for each version in
      alphanumeric order
- reference-style links at very bottom of file, grouped and in completion order
- 'Unit Tests' sections only updated when async change with relevant src change
  - Otherwise assumed src changes have corresponding unit test changes

Release change log convention via
[Keep a Changelog](http://keepachangelog.com/).


---


# [Unreleased](https://github.com/JonathanCasey/asana_extensions/tree/develop)

Compare to [stable](https://github.com/JonathanCasey/asana_extensions/compare/stable...develop)


### Project & Toolchain: `.git*`, `.editorconfig`
- [Added] `.editorconfig` and `.gitattributes` added ([#5][]).
- [Added] VS Code related items added to `.gitignore` ([#5][]).
- [Added] `.conf` extensions in `config` dir added to `.gitignore` ([#1][]).
- [Added] `.env` extensions in `config` dir added to `.gitignore` ([#3][]).


### Project & Toolchain: CircleCI
- [Added] CircleCI implemented, with `.circleci/config.yml` file that ensures
      project builds successfully ([#5][]).
- [Added] `asana-creds` added as context for unit tests, with setup of mock
      files to load access token into secrets conf ([#9][]).
- [Added] Job to pylint `conftest.py` added ([#10][]).
- [Added] Appended to pytest command to run a second invocation of `pytest`
      using `--run-no-warnings-only`, appending cov report ([#10][]).
- [Changed] `lint-and-test` workflow split into separate `lint` and `test`
      workflows to more easily see results separately on GitHub ([#27][]).
- [Changed] Codecov uploader migrated from deprecated bash uploader to new
      uploader ([#28][]).
- [Changed] Python version changed from 3.8 to 3.10 ([#33][]).


### Project & Toolchain: CI Support
- [Added] `dir_init_checker.py` added to new `ci_support` dir to run code for
      checking `__init__.py` files are up to date ([#5][]).
- [Fixed] References to previous project removed ([#7][]).
- [Added] `trailing_commas.py` added for pylint checker plugin for multi-line
      lists and trailing commas ([#13][]).
  - From groboclown; with modifications to add ignore for empty list as well as
        options for ignoring `if`, tuples, and functions.
  - Source code updated with fixes, but no functional changes.


### Project & Toolchain: CodeCov
- [Added] CodeCov support added to project (`.codecov.yml`) and CircleCI
      ([#5][]).
- [Changed] CodeCov targets set to 100% for project and patch ([#12][]).
- [Fixed] Incorrect code coverage in [#32][] corrected by upgrade to python 3.10
      ([#33][]).


### Project & Toolchain: Conventions
- [Added] Set convention to use leading `_` for class instance members only
      intended for private access ([#5][]).


### Project & Toolchain: Package, Requirements
- [Added] `requirements.txt` added, with `pylint`,  `pytest`, `pytest-cov` as
      only entries ([#5][]).
- [Added] `python-dateutil` added to `requirements.txt` ([#1][]).
- [Added] `asana` added to `requirements.txt` ([#9][]).
- [Changed] Python version changed from 3.7/3.8 to 3.10 ([#33][]).


### Project & Toolchain: Pylint
- [Added] `.pylintrc` added to configure pylint, with source code paths added
      ([#5][]).
- [Fixed] References to previous project removed ([#7][]).
- [Added] `trailing_commas` plugin added, with options to ignore `if`, tuples,
      and functions ([#13][]).


### Project & Toolchain: Pytest, /conftest
- [Added] `--run-no-warnings-only` CLI arg added to only run tests marked with
      `no_warnings_only` (and otherwise skip those tests) ([#10][]).


### Project & Toolchain: Tests: Exceptions
- [Added] `/tests/exceptions.py` added, with `TesterNotInitializedError` to be
      used if required external Asana configuration not done ([#10][]).


### Asana / Meta

##### Unit Tests: conftest
- [Added] Added `conftest.py` to root of `asana` subpackage in unit tests dir,
      with new `fixture_sections_in_utl_test()` added for use by other modules
      in subpackage ([#18][]).


##### Unit Tests: Tester Data
- [Added] `tester_data.py` added to hold test data constants, initially
      including the `_WORKSPACE`, `_PROJECT_TEMPLATE`, and `_SESSIONS_TEMPLATE`
      constants ([#10][]).
- [Added] `_TASK_TEMPLATE` added for naming test tasks ([#18][]).


### Asana: Client
- [Added] `asana_client.py` added, with initial `_get_client()` management
      method and `_get_me()` helper method imlpemented ([#9][]).
- [Changed] `asana_client.py` and `test_asana_client.py` renamed to `client.py`
      and `test_client.py`, with `aclient` being the recommended import as
      ([#16][]).
- [Added] Logger will now capture warnings from `warnings` module ([#10][]).
- [Added] Exceptions `DataNotFoundError`, `DuplicateNameError`, and
      `MismatchedDataError` added ([#10][]).
- [Added] Methods to get the gid from the name added for workspace, project,
      and section resource types, leveraging `_find_gid_from_name()` ([#10][]).
- [Added] Added method to get the user task list gid either by user gid or for
      "me" ([#10][]).
- [Added] Added method to get the list of sections (as gids) in a project or
      user task list ([#10][]).
- [Added] `@asana_error_handler` decorator added to wrap exception handling
      for asana API requests (just logs and raises) ([#25][]).
  - Adds a `_is_wrapped_by_asana_error_handler` to function for test purposes.
- [Changed] All functions that make API requests directly now decorated with
      `@asana_error_handler` and all existing relevant exception handling
      removed from those functions ([#25][]).
- [Added] `get_tasks()` method added to get tasks from asana API based on given
      criteria ([#18][]).
- [Added] `move_task_to_section()` added, with option to move to top or bottom
      ([#19][]).
- [Changed] Asana API deprecation warning fixed by explicitly using the
      `new_user_task_lists` (thereby dropping support for older user task list
      version, which probably didn't work here anyways) ([#37][]).
- [Fixed] Issue where gids are mixed up between str and int for comparison,
      asana module calls is resolved ([#48][]).

##### Unit Tests
- [Changed] `fixture_raise_no_authorization_error` and
      `fixture_raise_not_found_error` removed in favor of a general
      `fixture_raise_asana_error` ([#25][]).
  - Uses an `asana_error_data` pytest marker to allow customization of
        exception by test using it.
- [Changed] `fixture_section_in_project_test` is now
      `fixture_sections_in_project_test`, supports 2 sections ([#25][]).
  - This also means it now returns a list of dicts.  Relevant tests updated.
- [Added] `subtest_asana_error_handler_func()` added, intended to be called in
      test of every function decorated with `@asana_error_handler` ([#25][]).
  - Test cases for these functions updated to call this new method in
        combination with `asana_error_data` pytest marker.
- [Added] `test_asana_error_handler()` added for direct test of decorator
      ([#25][]).
- [Added] `test_dec_usage_asana_error_handler()` added for simple parametrized
      testing of all functions decorated with `@asana_error_handler` to ensure
      they are decorated as expected ([#25][]).
- [Added] `test_pagination` added to ensure pagination does not cause any issues
      with this project (really an integration test) ([#25][]).
- [Changed] Improved looping syntax by iterating by item, not be index in some
      places ([#18][]).
- [Added] `fixture_tasks_in_project_and_utl_test()` added to create tasks for
      testing `get_tasks()` method (so far) ([#18][]).
- [Added] `fixture_tasks_movable_in_project_and_utl_test()` added for tests
      prepared for tasks to be moved ([#19][]).
- [Added] `filter_result_for_test()` added to only return results (presumably
      from the asana API) that are allowed for the test ([#19][]).
- [Changed] Refactored any existing tests that can utilize the new
      `filter_result_for_test()` ([#19][]).


### Asana: Utils
- [Added] `utils.py` added to cover aggregate logic building on top of straight
      API results ([#10][]).
- [Added] `DataConflictError` and `DataMissingError` exceptions added ([#10][]).
- [Added] Method to get the net included section gids based on project contents
      and explicit includes/excludes added ([#10][]).
- [Added] `get_filtered_tasks()` added to filter tasks based on due date/time in
      a given section, including factoring in timezone as best as API will
      allow ([#18][]).
- [Added] `_filter_tasks_by_datetime()` and `_filter_tasks_by_completed` added
      to support specific filter processing of `get_filtered_tasks()` ([#18][]).

##### Unit Tests
- [Added] `fixture_tasks_with_due_in_utl_test()` added for testing task
      filtering (so far) ([#18][]).


### Bin: asana_extensions_exec_all.sh
- [Added] `asana_extensions_exec_all.sh` added as a wrapper script for Ubuntu,
      with rsyslog and email failure support added ([#3][]).


### Config: .secrets.conf
- [Added] `.secrets.conf` file created (with `.default` stub), with `asana`
      section for personal access token key added ([#9][]).


### Config: .secrets.env
- [Added] `.secrets.env` file created (with `.default` stub), with parameters
      for email server and admin email config (for Ubuntu bin script) ([#3][]).


### Config: asana_extensions.env
- [Added] `asana_extensions.env` file created (with `.default` stub) with
      parameter to specify path to python bin to use (for Ubuntu bin script)
      ([#3][]).


### Config: rules.conf
- [Added] `rules.conf` file created (with `.default` stub), with move tasks rule
      stub added ([#1][]).
- [Fixed] Correct description that `for my tasks list` and `user task list id`
      cannot be provided together, now matching code ([#10][]).
- [Fixed] Cleaned up comments not meant to be committed.
- [Added] `assumed time for min due` and `assumed time for max due` added along
      with explanation of usage ([#18][]).
- [Fixed] For sections, names can only be listed by newline separators now, but
      gids can now properly be listed by any combo of newlines and commas
      ([#49][]).


### General: Config
- [Added] `config.py` added with basic `ConfigParser` file loading, including
      without a section header; and list parsing ([#7][]).
- [Changed] `conf_base_dir` parameter in `read_conf_file_fake_header()`,
      `read_conf_file()` changed to `None`, with the real default set within the
      method body to better support testing ([#1][]).
- [Added] `UnsupportedFormatError` added for cases where a config value is in
      a parsable format, but it's use as such is not supported ([#18][]).
- [Changed] `parse_list_from_conf_string()` now also takes `delim_newlines` as
      a parameter and will split on that and/or the `delim` parameter ([#49][]).
- [Changed] The `delim` parameter in `parse_list_from_conf_string()` can be
      `None` to not split on a character string ([#49][]).
- [Fixed] Empty string entries in list parser from conf string are now dropped
      ([#49][]).
- [Added] `LevelFilter` added for logging so an upper severity can be specified
      for logging routing ([#45][]).


### General: Dirs
- [Added] `dirs.py` added with basic dir resolution ([#7][]).


### General: Exceptions
- [Added] `exceptions.py` added with `TimeframeArgDupeError` ([#1][]).


### General: Utils
- [Added] `utils.py` added, with `is_date_only()` check, which only supports
      ISO 8601 strings and `relativedelta` input only ([#18][]).


### Main / __main__
- [Added] `main.py` added to `/asana_extensions` for main entry point for app
      ([#20][]).
  - Set logger level based on CLI arg.
  - Set whether to force test report only mode based on CLI arg.
  - Execute modules based on CLI arg (so far, only `rules` or `all`).
  - Shutdown signal handler added.
- [Fixed] `__main__.py` added to `/asana_extensions` as the real entry point
      when executing as a module (which is required) -- it is an extremely slim
      wrapper for `main.py` ([#3][], [#44][]).
- [Changed] `StreamHandler`s added to root logger config with `LevelFilter` so
      can split low severity and high severity between stdout and stderr,
      respectively ([#45][]).
- [Fixed] In `_config_root_logger()`, raising the `ValueError` from string
      parsing is deferred until after trying int parsing so numbers passed as
      strings will work ([#46][]).

##### Unit Tests
- [Fixed] `fixture_ensure_logging_framework_not_altered()` added with `autouse`
      to fix issue where some tests would fail due to root logger usage of
      `StreamHandler` in some tests clashing with `capsys` fixture in some tests
      ([#51][]).


### Rules / Meta
- [Added] `rule_meta.py` added with abstract `Rule` defining interface and some
      consolidated logic ([#1][]).
- [Added] Time-delta arg and timeframe parsing added to `Rule` ([#1][]).
- [Added] `rules.py` added with `load_all_from_config()` started to load all
      rules from the `rules.conf` file ([#1][]).
- [Added] `MoveTasksRule` added to `_RULES` list in `rules.py` ([#1][]).
- [Added] `parse_time_arg()` added to `Rule` to parse time-only iso-format
      values (not full ISO 8601 format though) ([#18][]).
- [Changed] `parse_timedelta_arg()` will now also return `None` if an empty
      string is provided in case key is left in config but is blank ([#18][]).
- [Added] `_is_valid` added to `Rule` to store cached validation results
      ([#2][]).
- [Added] `get_rule_id()` accessor method added to `Rule` ([#2][]).
- [Added] `_sync_and_validate_with_api()` and `_execute()` abstract methods
      added to `Rule` ([#2][]).
- [Added] `is_valid()` and `is_criteria_met()` methods added to `Rule` with
      default logic for any subclasses that don't need to override ([#2][]).
- [Added] `execute_rules()` added to `rules.py` to perform the actions for all
      provided rules ([#2][]).

##### Unit Tests: conftest
- [Added] Added `conftest.py` to root of `rules` subpackage in unit tests dir,
      with new `fixture_blank_rule_cls()` added for use by other modules
      in subpackage ([#2][]).
- [Changed] Some existing functions that used a `BlankRule` class refactored to
      use `fixture_blank_rule_cls()` ([#2][]).


### Rules: Move Tasks Rule
- [Added] `move_tasks_rule.py` added with `MoveTasksRule` having initial logic
      to load from config and do non-API validation ([#1][]).
- [Added] Support for `assumed time for min/max due` config parameters added,
      with catch of `UnsupportedFormatError` ([#18][]).
- [Fixed] Updated incorrect parameter name in error message ([#18][]).
- [Changed] References to timeframe in error messages changed to be `timeframe`
      instead of `time` to be more clear and distinuish from assumed time errors
      ([#18][]).
- [Added] Implemented `_sync_and_validate_with_api()` to do API-dependent
      pre-processing [#2][].
- [Added] Implemented `execute()` to check and perform `MoveTasksRule` action
      ([#2][]).
- [Fixed] For sections, names can only be listed by newline separators now, but
      gids can now properly be listed by any combo of newlines and commas
      ([#49][]).

##### Unit Tests
- [Changed] `[test-move-tasks-full-is-utl-and-gid]` is now split into
      `[test-move-tasks-is-utl-and-gid]` and `[test-move-tasks-full]` to ensure
      that if `full` is changed later, no need to worry about it reducing
      coverage ([#18][]).
- [Added] `fixture_blank_move_tasks_rule()` added as a basis for a blank
      `MoveTasksRule` ([#2][]).
- [Changed] `test_load_specific_from_conf_impossible()` renamed to
      `test_load_specific_from_conf__impossible()` ([#2][]).
- [Changed] `test_get_provider_names()` renamed to `test_get_rule_type_names()`
      ([#2][]).


### Docs: CHANGELOG
- [Added] This `CHANGELOG.md` file created and updated with all project work
      to-date (+1 self reference) ([#5][]).


### Docs: CONTRIBUTING
- [Added] `CONTRIBUTING.md` added to project root; relevant parts from
      `setup.md` and `usage.md` migrated ([#5][]).
- [Changed] `pytest` workflow command updated to use coverage output ([#13][]).
- [Removed] The `test` `env` is not applicable to this project and references
      have been removed ([#9][]).
- [Added] Details regarding the usage of the Asana account for test added
      ([#10][]).
- [Added] Additional workflow steps and details added for additional
      modules/packages to pylint, as well as 2nd pytest invocation with
      `--run-no-warnings-only` ([#10][]).


### Docs: README
- [Changed] Updated with project intro (mostly placeholder) ([#5][]).
- [Added] Link to `setup.md`, `usage.md`, `CONTRIBUTING.md` added ([#5][]).
- [Added] Code cov badge added ([#7][]).
- [Added] Added the move tasks rule to list of supported feature ([#1][]).
- [Added] Notes regarding OS support and how to use with multiple Asana accounts
      added ([#3][]).


### Docs: Setup
- [Added] `setup.md` added (placeholder) ([#5][]).
- [Added] Noted that python 3.7 was used for dev ([#1][]).
- [Added] Added setup instructions on creating config from stubs ([#1][]).
- [Changed] Python version changed from 3.7 to 3.10 ([#33][]).
- [Added] Noted python 3.7 as the likely min version ([#3][]).
- [Added] Guidance on setting up each config file added while trying to minimize
      duplication with notes in stub files ([#3][]).
- [Added] Steps to install python and/or Ubuntu prerequisites added ([#3][]).
- [Added] Guidance on setting up rsyslog and scheduling
      (cron/systemd/task scheduler) added ([#3][]).


### Docs: Usage
- [Added] `usage.md` added with workflow tips ([#5][]).
- [Added] Added note to run through setup prior to first use ([#1][]).
- [Fixed] Execution changed to run as a module so it actually works ([#44][]).
- [Fixed] Python 3.6 removed as an example of a possible earlier python version
      to use now that it is confirmed to not work ([#3][]).
- [Added] Executing shell script in Ubuntu added ([#3][]).
- [Added] Tips on monitoring log output in Ubuntu added ([#3][]).


### Ref Links

#### Milestones & Projects
- [Milestone: v1.0.0](https://github.com/JonathanCasey/asana_extensions/milestone/1)
- [Project: v1.0.0](https://github.com/JonathanCasey/asana_extensions/projects/1)

#### Issues
- [#1][]
- [#2][]
- [#3][]
- [#5][]
- [#7][]
- [#9][]
- [#10][]
- [#12][]
- [#13][]
- [#16][]
- [#18][]
- [#19][]
- [#20][]
- [#25][]
- [#27][]
- [#28][]
- [#33][]
- [#37][]
- [#44][]
- [#45][]
- [#46][]
- [#48][]
- [#49][]
- [#51][]

#### PRs
- [#6][] for [#5][]
- [#8][] for [#7][]
- [#11][] for [#1][], [#12][]
- [#14][] for [#13][]
- [#15][] for [#9][]
- [#17][] for [#16][]
- [#26][] for [#10][]
- [#29][] for [#27][]
- [#30][] for [#25][]
- [#31][] for [#28][]
- [#32][] for [#18][]
- [#34][] for [#33][]
- [#38][] for [#19][]
- [#41][] for [#2][]
- [#42][] for [#20][]
- [#43][] for [#37][]
- [#50][] for [#3][], [#44][], [#45][], [#46][], [#48][], [#49][], [#51][]


---


Reference-style links here (see below, only in source) in develop-merge order.

[#5]: https://github.com/JonathanCasey/asana_extensions/issues/5 'Issue #5'
[#7]: https://github.com/JonathanCasey/asana_extensions/issues/7 'Issue #7'
[#1]: https://github.com/JonathanCasey/asana_extensions/issues/1 'Issue #1'
[#12]: https://github.com/JonathanCasey/asana_extensions/issues/12 'Issue #12'
[#13]: https://github.com/JonathanCasey/asana_extensions/issues/13 'Issue #13'
[#9]: https://github.com/JonathanCasey/asana_extensions/issues/9 'Issue #9'
[#16]: https://github.com/JonathanCasey/asana_extensions/issues/16 'Issue #16'
[#10]: https://github.com/JonathanCasey/asana_extensions/issues/10 'Issue #10'
[#27]: https://github.com/JonathanCasey/asana_extensions/issues/27 'Issue #27'
[#25]: https://github.com/JonathanCasey/asana_extensions/issues/25 'Issue #25'
[#28]: https://github.com/JonathanCasey/asana_extensions/issues/28 'Issue #28'
[#18]: https://github.com/JonathanCasey/asana_extensions/issues/18 'Issue #18'
[#33]: https://github.com/JonathanCasey/asana_extensions/issues/33 'Issue #33'
[#19]: https://github.com/JonathanCasey/asana_extensions/issues/19 'Issue #19'
[#2]: https://github.com/JonathanCasey/asana_extensions/issues/2 'Issue #2'
[#20]: https://github.com/JonathanCasey/asana_extensions/issues/20 'Issue #20'
[#37]: https://github.com/JonathanCasey/asana_extensions/issues/37 'Issue #37'
[#3]: https://github.com/JonathanCasey/asana_extensions/issues/3 'Issue #3'
[#44]: https://github.com/JonathanCasey/asana_extensions/issues/44 'Issue #44'
[#45]: https://github.com/JonathanCasey/asana_extensions/issues/45 'Issue #45'
[#46]: https://github.com/JonathanCasey/asana_extensions/issues/46 'Issue #46'
[#48]: https://github.com/JonathanCasey/asana_extensions/issues/48 'Issue #48'
[#49]: https://github.com/JonathanCasey/asana_extensions/issues/49 'Issue #49'
[#51]: https://github.com/JonathanCasey/asana_extensions/issues/51 'Issue #51'

[#6]: https://github.com/JonathanCasey/asana_extensions/pull/6 'PR #6'
[#8]: https://github.com/JonathanCasey/asana_extensions/pull/8 'PR #8'
[#11]: https://github.com/JonathanCasey/asana_extensions/pull/11 'PR #11'
[#14]: https://github.com/JonathanCasey/asana_extensions/pull/14 'PR #14'
[#15]: https://github.com/JonathanCasey/asana_extensions/pull/15 'PR #15'
[#17]: https://github.com/JonathanCasey/asana_extensions/pull/17 'PR #17'
[#26]: https://github.com/JonathanCasey/asana_extensions/pull/26 'PR #26'
[#29]: https://github.com/JonathanCasey/asana_extensions/pull/29 'PR #29'
[#30]: https://github.com/JonathanCasey/asana_extensions/pull/30 'PR #30'
[#31]: https://github.com/JonathanCasey/asana_extensions/pull/31 'PR #31'
[#32]: https://github.com/JonathanCasey/asana_extensions/pull/32 'PR #32'
[#34]: https://github.com/JonathanCasey/asana_extensions/pull/34 'PR #34'
[#38]: https://github.com/JonathanCasey/asana_extensions/pull/38 'PR #38'
[#41]: https://github.com/JonathanCasey/asana_extensions/pull/41 'PR #41'
[#42]: https://github.com/JonathanCasey/asana_extensions/pull/42 'PR #42'
[#43]: https://github.com/JonathanCasey/asana_extensions/pull/43 'PR #43'
[#50]: https://github.com/JonathanCasey/asana_extensions/pull/50 'PR #50'
