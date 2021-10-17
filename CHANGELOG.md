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


### Project & Toolchain: CircleCI
- [Added] CircleCI implemented, with `.circleci/config.yml` file that ensures
      project builds successfully ([#5][]).
- [Added] `asana-creds` added as context for unit tests, with setup of mock
      files to load access token into secrets conf ([#9][]).
- [Added] Job to pylint `conftest.py` added ([#10][]).
- [Added] Appended to pytest command to run a second invocation of `pytest`
      using `--run-no-warnings-only`, appending cov report ([#10][]).


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


### Project & Toolchain: Conventions
- [Added] Set convention to use leading `_` for class instance members only
      intended for private access ([#5][]).


### Project & Toolchain: Package, Requirements
- [Added] `requirements.txt` added, with `pylint`,  `pytest`, `pytest-cov` as
      only entries ([#5][]).
- [Added] `python-dateutil` added to `requirements.txt` ([#1][]).
- [Added] `asana` added to `requirements.txt` ([#9][]).


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

##### Unit Tests: Tester Data
- [Added] `tester_data.py` added to hold test data constants, initially
      including the `_WORKSPACE`, `_PROJECT_TEMPLATE`, and `_SESSIONS_TEMPLATE`
      constants ([#10][]).


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


### Asana: Utils
- [Added] `utils.py` added to cover aggregate logic building on top of straight
      API results ([#10][]).
- [Added] `DataConflictError` and `DataMissingError` exceptions added ([#10][]).
- [Added] Method to get the net included section gids based on project contents
      and explicit includes/excludes added ([#10][]).


### Config: .secrets.conf
- [Added] `.secrets.conf` file created (with `.default` stub), with `asana`
      section for personal access token key added ([#9][]).


### Config: rules.conf
- [Added] `rules.conf` file created (with `.default` stub), with move tasks rule
      stub added ([#1][]).
- [Fixed] Correct description that `for my tasks list` and `user task list id`
      cannot be provided together, now matching code ([#10][]).
- [Fixed] Cleaned up comments not meant to be committed.


### General: Config
- [Added] `config.py` added with basic `ConfigParser` file loading, including
      without a section header; and list parsing ([#7][]).
- [Changed] `conf_base_dir` parameter in `read_conf_file_fake_header()`,
      `read_conf_file()` changed to `None`, with the real default set within the
      method body to better support testing ([#1][]).


### General: Dirs
- [Added] `dirs.py` added with basic dir resolution ([#7][]).


### General: Exceptions
- [Added] `exceptions.py` added with `TimeframeArgDupeError` ([#1][]).


### Rules / Meta
- [Added] `rule_meta.py` added with abstract `Rule` defining interface and some
      consolidated logic ([#1][]).
- [Added] Time-delta arg and timeframe parsing added to `Rule` ([#1][]).
- [Added] `rules.py` added with `load_all_from_config()` started to load all
      rules from the `rules.conf` file ([#1][]).
- [Added] `MoveTasksRule` added to `_RULES` list in `rules.py` ([#1][]).


### Rules: Move Tasks Rule
- [Added] `move_tasks_rule.py` added with `MoveTasksRule` having initial logic
      to load from config and do non-API validation ([#1][]).


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


### Docs: Setup
- [Added] `setup.md` added (placeholder) ([#5][]).
- [Added] Noted that python 3.7 was used for dev ([#1][]).
- [Added] Added setup instructions on creating config from stubs ([#1][]).


### Docs: Usage
- [Added] `usage.md` added with workflow tips ([#5][]).
- [Added] Added note to run through setup prior to first use ([#1][]).


### Ref Links

#### Milestones & Projects
- [Milestone: v1.0.0](https://github.com/JonathanCasey/asana_extensions/milestone/1)
- [Project: v1.0.0](https://github.com/JonathanCasey/asana_extensions/projects/1)

#### Issues
- [#1][]
- [#5][]
- [#7][]
- [#9][]
- [#10][]
- [#12][]
- [#13][]
- [#16][]

#### PRs
- [#6][] for [#5][]
- [#8][] for [#7][]
- [#11][] for [#1][], [#12][]
- [#14][] for [#13][]
- [#15][] for [#9][]
- [#17][] for [#16][]
- [#26][] for [#10][]


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

[#6]: https://github.com/JonathanCasey/asana_extensions/pull/6 'PR #6'
[#8]: https://github.com/JonathanCasey/asana_extensions/pull/8 'PR #8'
[#11]: https://github.com/JonathanCasey/asana_extensions/pull/11 'PR #11'
[#14]: https://github.com/JonathanCasey/asana_extensions/pull/14 'PR #14'
[#15]: https://github.com/JonathanCasey/asana_extensions/pull/15 'PR #15'
[#17]: https://github.com/JonathanCasey/asana_extensions/pull/17 'PR #17'
[#26]: https://github.com/JonathanCasey/asana_extensions/pull/26 'PR #26'
