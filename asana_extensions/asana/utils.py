#!/usr/bin/env python3
"""
Asana utilities.  These are logic and other helper pieces that sit on top of the
client layer, using that data from the API to further manipulate data for
specific purposes.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import datetime as dt
import logging
import operator

import dateutil.parser as dp

from asana_extensions.asana import client as aclient
from asana_extensions.general import utils



logger = logging.getLogger(__name__)



class DataConflictError(Exception):
    """
    Raised when there is a conflicting combination of data, such as data that is
    explicitly specified to be included and excluded at the same time.
    """



class DataMissingError(Exception):
    """
    Raised when there is data that is explicitly specified and expected to
    exist but it ultimately does not exist; and this data being missing is
    likely a critical error.
    """



def get_net_include_section_gids(              # pylint: disable=too-many-locals
        proj_or_utl_gid,
        include_sect_names=None, include_sect_gids=None,
        exclude_sect_names=None, exclude_sect_gids=None,
        default_to_include=True):
    """
    Gets the filterd list of section gids, providing only the net included ones.
    This will convert all names to gids and look at the resulting sets of
    included and exclude gids as compared to all section gids in the project or
    UTL.  This does not do anything special for matches or mismatches between
    names and gids within includes or within excludes; it simply takes the union
    of them to form a combined set.

    Any section that is explicitly both included and excluded will raise an
    error.

    The default behavior when no includes or excludes are provided can be
    specified, though providing any explicit includes will effectively override
    this behavior to default to exclude.

    Args:
      proj_or_utl_gid (int): The gid of the project for which to get sections.
        Through empirical testing and noted as a 'trick' on dev forums, the
        user task list gid (not 'me') can be used to get the sections of that.
      include_sect_names ([str] or None): The list of section names that will be
        explicitly included.
      include_sect_gids ([int] or None): The list of section gids that will be
        explicitly included.
      exclude_sect_names ([str] or None): The list of section names that will be
        explicitly excluded.
      exclude_sect_gids ([int] or None): The list of section gids that will be
        explicitly excluded.
      default_to_include (bool): The default behavior, such as when all include
        and exclude args are None.

    Returns:
      ({int}): The resulting set of section gids to include from the project.

    Raises:
      (DataConflictError): Raised if any gid (or gid derived from name) is
        explicitly both included and excluded.
      (DataMissingError): Raised if any gid (or gid derived from name) is
        explicitly included but is missing from the project.

      This will pass up unhandled client exceptions.
    """
    include_sect_names = include_sect_names or []
    include_sect_gids = include_sect_gids or []
    exclude_sect_names = exclude_sect_names or []
    exclude_sect_gids = exclude_sect_gids or []

    project_section_gids = set(aclient.get_section_gids_in_project_or_utl(
            proj_or_utl_gid))

    include_sect_gids_from_names = {aclient.get_section_gid_from_name(
            proj_or_utl_gid, s): s for s in include_sect_names}
    exclude_sect_gids_from_names = {aclient.get_section_gid_from_name(
            proj_or_utl_gid, s): s for s in exclude_sect_names}

    include_gids = set(include_sect_gids_from_names) | set(include_sect_gids)
    exclude_gids = set(exclude_sect_gids_from_names) | set(exclude_sect_gids)
    gids_to_names = {
        **include_sect_gids_from_names,
        **exclude_sect_gids_from_names,
    }

    if include_gids - project_section_gids:
        missing_gids = [str(g) for g in include_gids - project_section_gids]
        missing_names = [gids_to_names[int(g)] for g in missing_gids
                if int(g) in gids_to_names]
        err_msg = 'Section names/gids explicitly included are missing from' \
                + ' project/user task list.'
        err_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(missing_gids)}.'
        if missing_names:
            err_msg += f' Also check names: `{"`, `".join(missing_names)}`.'
        raise DataMissingError(err_msg)

    if exclude_gids - project_section_gids:
        missing_gids = [str(g) for g in exclude_gids - project_section_gids]
        missing_names = [gids_to_names[int(g)] for g in missing_gids
                if int(g) in gids_to_names]
        warn_msg = 'Section names/gids explicitly excluded are missing from' \
                + ' project/user task list. This may be unintentional.'
        warn_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(missing_gids)}.'
        if missing_names:
            warn_msg += f' Also check names: `{"`, `".join(missing_names)}`.'
        logger.warning(warn_msg)

    if include_gids & exclude_gids:
        conflicting_gids = [str(g) for g in include_gids & exclude_gids]
        conflicting_names = [gids_to_names[int(g)] for g in conflicting_gids
                if int(g) in gids_to_names]
        err_msg = 'Explicit section names/gids cannot be simultaneously' \
                + ' included and excluded.'
        err_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(conflicting_gids)}.'
        if conflicting_names:
            err_msg += f' Also check names: `{"`, `".join(conflicting_names)}`.'
        raise DataConflictError(err_msg)

    if not default_to_include or (default_to_include and include_gids):
        return include_gids

    return project_section_gids - exclude_gids



def get_filtered_tasks(section_gid, match_no_due_date=False,
        min_time_until_due=None, max_time_until_due=None,
        min_time_due_assumed=None, max_time_due_assumed=None,
        use_tzinfo=None):
    """
    Gets tasks in a given section that meet the due filter criteria provided.

    Args:
      section_gid (str/int): The section from which to fitler tasks based on due
        date/time.
      match_no_due_date (bool): Whether to select tasks that do not have a due
        date.  Cannot be used with `min_time_until_due` nor
        `max_time_until_due`.
      min_time_until_due (relativedelta or None): The lower bound of due
        date/time to select from the section tasks, relative to now.  I.e. this
        will select tasks that are due after and including this threshold
        relative to now.  If None (and `match_no_due_date` is False), selects
        all tasks since the beginning of time (up until `max_time_until_due`).
        Cannot be used with `match_no_due_date`.
      max_time_until_due (relativedelta or None): The upper bound of due
        date/time to select from the section tasks, relative to now.  I.e. this
        will select tasks that are due before and including this threshold
        relative to now.  If None (and `match_no_due_date` is False), selects
        all tasks until the end of time (but after `min_time_until_due`).
        Cannot be used with `match_no_due_date`
      min_time_due_assumed (time or None): A time to use for dates without times
        when evaluating the `min_time_until_due`.  Should NOT contain a
        timezone.  If None and `min_time_until_due` contains time durations,
        will ignore date-only tasks.  If `min_time_until_due` does not contain
        time durations, will be ignored.
      max_time_due_assumed (time or None): A time to use for dates without times
        when evaluating the `max_time_until_due`.  Should NOT contain a
        timezone.  If None and `max_time_until_due` contains time durations,
        will ignore date-only tasks.  If `max_time_until_due` does not contain
        time durations, will be ignored.
      use_tzinfo (timezone or None): The timezone to use for evaluating this
        "now".  Used to ensure this is run to match the timezone that is
        targetted to be used (which is what should be supplied) in case it is
        difference from what the local machine running this script has for a
        timezone (since this could change the date).  As a result, really only
        relevant with date-only comparisons since it can change which day things
        fall.  Datetime based comparisons are not affected since these are all
        done based with timezone factored in.  See docstring in
        `_filter_tasks_by_datetime()` for more info and an example of how this
        is used.

    Returns:
      filt_tasks ([{str:str}]): The tasks that meet the filter criteria, with
        each task being a dict of values based on the API key/values.
    """
    assert match_no_due_date \
            ^ (min_time_until_due is not None \
                or max_time_until_due is not None), \
            'Must provide min/max until due or specify no due date but not both'

    params = {
        'section': section_gid,
    }
    fields = [
        'due_at',
        'due_on',
        'name',
        'resource_type',
    ]
    sect_tasks = aclient.get_tasks(params, fields)

    if match_no_due_date:
        return [t for t in sect_tasks if t['due_on'] is None]

    now_with_tz = dt.datetime.now().astimezone(use_tzinfo)
    filt_tasks = _filter_tasks_by_datetime(sect_tasks, now_with_tz,
            min_time_until_due, operator.ge, min_time_due_assumed)
    filt_tasks = _filter_tasks_by_datetime(filt_tasks, now_with_tz,
            max_time_until_due, operator.le, max_time_due_assumed)
    return filt_tasks



def _filter_tasks_by_datetime(tasks, dt_base, rel_dt_until_due,
        task_is_rel_comparison_success_op, time_due_assumed=None):
    """
    Filters tasks by a date or datetime, returning the tasks that meet the
    provided filter criteria.

    ...and now we have to talk about timezones...

    Note that this will use the timezone of `dt_base`, which will default to the
    local timezone that runs this script if none is explicitly set!  Callers of
    this function have the option to change that timezone (e.g. `.astimezone()`
    on a datetime).  See `dt_base` parameter docstring for recommendations.

    As an example, let's say this is intended to run a script at 01:00 in NY
    (EST, UTC-0500) where it is primarily used by the user, but is loaded on a
    server in CA where it is 22:00 the previous day (PST, UTC-0800).  Let's say
    it is Apr-1 in CA, making it Apr-2 02:00 in NY.  Let's also say this script
    is running a "select tasks for today" script intended to run a little after
    midnight (1 hour in this case since user is in NY/EST), and there is a task
    due Apr-2 that is intended to be selected by this rule.  The asana API will
    return this task is due Apr-2, but in CA it is still Apr-1, so the task will
    not be selected.  Instead, though, if the `dt_base` is provided as EST, this
    script will run as though the date is Apr-2, effectively as though it were
    in EST.

    Args:
      tasks ([{str:str}]): List of tasks from asana API.  At the very least,
        must have the `due_on` key.
      dt_base (datetime): The datetime to use as the base for the relative
        threshold to check.  Normally this should be datetime.datetime.now(),
        but other datetime values can be used.  Date alone is NOT accepted.  If
        applying successive filters to the same data (i.e. min until due and
        the max until due), it is recommended to use same exact `dt_base` for
        each to ensure no weird gaps or call order issues.  This should include
        the TARGET timezone -- the timezone in which asana is/will primarily be
        used to be most accurate (in case different from where machine running
        script is).  Timezone is required.
      rel_dt_until_due (relativedelta): The relative date or datetime until the
        task is due.  This is relative to the `dt_base` provided.  This will be
        compared against the tasks due date/datetime based on the provided
        operator as explained by the `task_is_comparison_success_op` parameter.
        If this is only a date, all comparisons will be done as date-only.  If
        a time is included, all comparisons will be done as datetime.  In this
        latter case, any tasks without a due time but do have a due date will
        either be skipped if `time_due_assumed` is None, or will have that time
        set in the TARGET timezone provided by `dt_base`.  Note that while
        datetime API results have timezone info, the date-only API results seem
        to be the date based on the timezone in which the task was set (e.g. if
        it were set as Apr-1 in UTC+1400, it will still be Apr-1 when viewed
        in UTC-1200 at the same time).  This needs to be considered when setting
        the time at which this script runs and the timezone provided (or of the
        machine running it if none provided), as there could be a day-off error
        if operated at an edge case.  If None, will return all tasks.
      task_is_rel_comparison_success_op (operator): A less/greater than [or
        equal to] comparison operator to use in the filter evaluaion.  Tasks
        that satisfy the criteria of the task due date/datetime being
        [lt/gt/le/ge] the threshold date/datetime (determined from the base +
        relative until due) will successfully meet this filter criteria and be
        returned.
      time_due_assumed (time or None): A time to use for dates without times.
        Should NOT contain a timezone.  If None and `rel_dt_until_due` contains
        time durations, will ignore date-only tasks.  If `rel_dt_until_due` does
        not contain time durations, will be ignored.

    Returns:
      filt_tasks ([{str:str}]): The tasks that meet the filter criteria.  This
        will be all tasks if `rel_dt_until_due` is None; or will be tasks that
        satisfy `task_due [op] dt_base + rel_until_due`.
    """
    if rel_dt_until_due is None:
        return tasks

    if utils.is_date_only(rel_dt_until_due):
        ignore_time = True
        due_threshold = dt_base.date() + rel_dt_until_due
    else:
        ignore_time = False
        due_threshold = dt_base + rel_dt_until_due

    filt_tasks = []
    for task in tasks:
        if task['due_on'] is None:
            continue
        if ignore_time:
            due_task = dt.date.fromisoformat(task['due_on'])
        else:
            if 'due_at' in task and task['due_at'] is not None:
                # Need dateutil since datetime does not handle ending in Z
                due_task = dp.isoparse(task['due_at'])
            elif time_due_assumed is not None:
                # Use due date, but assume the "time" and tz as provided
                due_task = dt.datetime.combine(
                        dt.date.fromisoformat(task['due_on']),
                        time_due_assumed, dt_base.tzinfo)
            else:
                # Based on provided config, date-only should be skipped here
                continue

        # Since this is rel compare, format is `task [op] threshold`
        if task_is_rel_comparison_success_op(due_task, due_threshold):
            filt_tasks.append(task)

    return filt_tasks
