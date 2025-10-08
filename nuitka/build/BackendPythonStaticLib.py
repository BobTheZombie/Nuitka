"""Helpers for discovering static libpython archives in special environments."""

import glob
import os

from nuitka.PythonVersions import python_version_str
from nuitka.Tracing import general


def _isLpmModeEnabled():
    value = os.environ.get("LPM_MODE")

    if value is None:
        return False

    normalized = value.strip().lower()

    return normalized not in ("", "0", "false", "no", "off")


def _getCandidateDirectories():
    """Yield candidate directories containing libpython archives."""

    libdir = os.environ.get("LPM_PYTHON_LIBDIR")
    if libdir:
        yield libdir

    sysroot = os.environ.get("LPM_SYSROOT")
    if sysroot:
        for pattern in ("lib", "lib64", "lib32"):
            candidate = os.path.join(sysroot, "usr", pattern)
            if os.path.isdir(candidate):
                yield candidate

        for candidate in sorted(glob.glob(os.path.join(sysroot, "usr", "lib*"))):
            if os.path.isdir(candidate):
                yield candidate


def detectStaticLibPython():
    """Return a static libpython archive path for LPM builds if available."""

    if not (
        _isLpmModeEnabled()
        or os.environ.get("LPM_SYSROOT")
        or os.environ.get("LPM_PYTHON_LIBDIR")
    ):
        return None

    python_major, python_minor = python_version_str.split(".")

    preferred_names = (
        f"libpython{python_major}.{python_minor}.a",
        f"libpython{python_major}.a",
    )

    for directory in _getCandidateDirectories():
        try:
            entries = os.listdir(directory)
        except OSError:
            continue

        for name in preferred_names:
            if name in entries:
                candidate = os.path.abspath(os.path.join(directory, name))
                general.info(
                    "LPM mode: using static Python library '%s'." % candidate
                )
                return candidate

        for entry in sorted(entries):
            if entry.startswith("libpython") and entry.endswith(".a"):
                candidate = os.path.abspath(os.path.join(directory, entry))
                general.info(
                    "LPM mode: using static Python library '%s'." % candidate
                )
                return candidate

    return None
