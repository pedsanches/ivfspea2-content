"""Deprecated shim — import from :mod:`ivfspea2.cohorts` instead.

The implementation moved into the installable package. This module stays because
thirteen scripts import it under two different spellings:

    try:
        from cohort_filter import filter_submission_synthetic_cohort
    except ModuleNotFoundError:
        from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

Both spellings still resolve here, so no caller had to change to make the move.
New code should import ``ivfspea2.cohorts`` directly; this file can be deleted
once the last caller has moved.
"""

from ivfspea2.cohorts import (  # noqa: F401
    BASELINE_RUN_MAX,
    BASELINE_RUN_MIN,
    BASELINE_WINDOW,
    ENGINEERING_PREFIX,
    IVF_ALGORITHM,
    IVF_RUN_MAX,
    IVF_RUN_MIN,
    IVF_WINDOW,
    CohortWindow,
    build_group_coverage,
    filter_submission_synthetic_cohort,
    is_engineering_problem,
)

__all__ = [
    "BASELINE_RUN_MAX",
    "BASELINE_RUN_MIN",
    "BASELINE_WINDOW",
    "ENGINEERING_PREFIX",
    "IVF_ALGORITHM",
    "IVF_RUN_MAX",
    "IVF_RUN_MIN",
    "IVF_WINDOW",
    "CohortWindow",
    "build_group_coverage",
    "filter_submission_synthetic_cohort",
    "is_engineering_problem",
]
