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


### Project & Toolchain: CircleCI
- [Added] CircleCI implemented, with `.circleci/config.yml` file that ensures
      project builds successfully ([#5][]).


### Project & Toolchain: CI Support
- [Added] `dir_init_checker.py` added to new `ci_support` dir to run code for
      checking `__init__.py` files are up to date ([#5][]).
- [Fixed] References to previous project removed ([#1][]).


### Project & Toolchain: CodeCov
- [Added] CodeCov support added to project (`.codecov.yml`) and CircleCI
      ([#5][]).


### Project & Toolchain: Conventions
- [Added] Set convention to use leading `_` for class instance members only
      intended for private access ([#5][]).


### Project & Toolchain: Package, Requirements
- [Added] `requirements.txt` added, with `pylint`,  `pytest`, `pytest-cov` as
      only entries ([#5][]).


### Project & Toolchain: Pylint
- [Added] `.pylintrc` added to configure pylint, with source code paths added
      ([#5][]).
- [Fixed] References to previous project removed ([#1][]).


### General: Dirs
- [Added] `dirs.py` added with basic dir resolution ([#1][]).


### Docs: CHANGELOG
- [Added] This `CHANGELOG.md` file created and updated with all project work
      to-date (+1 self reference) ([#5][]).


### Docs: CONTRIBUTING
- [Added] `CONTRIBUTING.md` added to project root; relevant parts from
      `setup.md` and `usage.md` migrated ([#5][]).


### Docs: README
- [Changed] Updated with project intro (mostly placeholder) ([#5][]).
- [Added] Link to `setup.md`, `usage.md`, `CONTRIBUTING.md` added ([#5][]).
- [Added] Code cov badge added ([#1][]).


### Docs: Setup
- [Added] `setup.md` added (placeholder) ([#5][]).


### Docs: Usage
- [Added] `usage.md` added with workflow tips ([#5][]).


### Ref Links

#### Milestones & Projects
- [Milestone: v1.0.0](https://github.com/JonathanCasey/asana_extensions/milestone/1)
- [Project: v1.0.0](https://github.com/JonathanCasey/asana_extensions/projects/1)

#### Issues
- [#1][]
- [#5][]

#### PRs
- [#6][] for [#5][]


---


Reference-style links here (see below, only in source) in develop-merge order.

[#5]: https://github.com/JonathanCasey/asana_extensions/issues/5 'Issue #5'
[#1]: https://github.com/JonathanCasey/asana_extensions/issues/1 'Issue #1'

[#6]: https://github.com/JonathanCasey/asana_extensions/pull/6 'PR #6'
