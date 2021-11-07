#!/usr/bin/env python3
"""The version information for the code.

The version most likely indicates the last release version.  It is encouraged
during dev to use a pre-release of dev indication as noted below in the module
attributes for the `version` attribute.

Module Attributes:
  _VERSION (string): The current version of the code per SemVer.  Format should
    be `M.m.P-p`.  The `-p` can and should be omitted if it is `0`.  When in
    development, a `+dev` must be appended to the version on which it is based.
    This should be removed as a last step on a `release/` branch and must be
    removed before merging into `stable`.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import datetime as dt
import re
import subprocess

from asana_extensions.general import dirs



_VERSION = '0.0.0+dev'



def get_full_version_string():
    """Gets a version string that includes the intended version (or might be
    most recent), the timestamp, and the git info string.

    Returns:
      (str): The string containing all version info for project.
    """
    timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    return f'v{_VERSION}_{timestamp}_{_get_git_info_string()}'



def _get_git_info_string():
    """Gets an info string for the git status that includes the recent commit,
    the branch, and the status of uncommitted changes.

    Returns:
      git_info (str): The git info string.
    """
    git_hash = _get_git_commit_hash()
    git_branch_code = _get_git_branch_code()
    git_status_code = _get_git_status_code()

    git_info = f'{git_hash}-{git_branch_code}'
    if git_status_code:
        git_info += f'-{git_status_code}'

    return git_info



def _get_git_commit_hash():
    """Gets the hash code for the most recent git commit on the current
    branch/checkout.

    Returns:
      git_hash (str): The 7-character short git commit hash for the most recent
        commit/checkout.  `x` if git is not installed.

    Raises:
      (subprocess.CalledProcessError): Raised if an unexpected non-zero return
        code is received from shell invocation.
    """
    try:
        result = subprocess.run(('git', 'rev-parse', '--short', 'HEAD'),
                cwd=dirs.get_root_path(), shell=True,
                capture_output=True, encoding='utf-8', check=True)
    except subprocess.CalledProcessError as ex:
        if ex.returncode == 1:
            # No .git dir / not cloned / git not installed
            return 'x'
        raise

    git_hash = result.stdout.strip()
    return git_hash



def _get_git_branch_code():
    """Gets the git branch and encodes into a code.
    Format is the branch code of `s`table, `d`evelop, or other `b`ranch.
    Detached head will be reported as `h`.  Git not being installed will be
    reported as `x`.

    Return:
      git_branch_code (str): The current git branch code.

    Raises:
      (subprocess.CalledProcessError): Raised if an unexpected non-zero return
        code is received from shell invocation.
    """
    try:
        result = subprocess.run(('git', 'symbolic-ref', 'HEAD'),
                cwd=dirs.get_root_path(), shell=True,
                capture_output=True, encoding='utf-8', check=True)
    except subprocess.CalledProcessError as ex:
        if ex.returncode == 1:
            # No .git dir / not cloned / git not installed
            return 'x'
        if ex.returncode == 128:
            # Detached head
            return 'h'
        raise

    branch_ptn = re.compile('^refs/heads/')
    git_branch = branch_ptn.sub('', result.stdout.strip())

    if git_branch == 'stable':
        return 's'
    if git_branch == 'develop':
        return 'd'
    return 'b'



def _get_git_status_code():
    """Gets the git status and encodes general file states.

    Format is `x-y`, where `x` is the listing of all `X` values from the short
    git status, and `y` is the listing of all `Y` values from the short git
    status.  Each section puts the letters in alphabetical order, and `?` is
    replaced by `u`, and `!` is replaced by `i`.  See the git status docs for
    more info on what `XY` codes are.

    Returns:
      git_status_code (str): The git status code summary string.  Literal `x-x`
        if git is not installed.

    Raises:
      (subprocess.CalledProcessError): Raised if an unexpected non-zero return
        code is received from shell invocation.
    """
    try:
        result = subprocess.run(('git', 'status', '--short'),
                cwd=dirs.get_root_path(), shell=True,
                capture_output=True, encoding='utf-8', check=True)
    except subprocess.CalledProcessError as ex:
        if ex.returncode == 1:
            # No .git dir / not cloned / git not installed
            return 'x-x'
        raise

    git_status = result.stdout  # Do NOT strip -- need leading whitespace!

    x_codes = set()
    y_codes = set()

    for line in git_status.splitlines():
        x = line[0].replace('?', 'u').replace('!', 'i')
        y = line[1].replace('?', 'u').replace('!', 'i')

        if x and x != ' ':
            x_codes.add(x)

        if y and y != ' ':
            y_codes.add(y)

    x_str = ''.join(sorted(x_codes))
    y_str = ''.join(sorted(y_codes))

    if not x_codes and not y_codes:
        return ''

    return f'{x_str}-{y_str}'
