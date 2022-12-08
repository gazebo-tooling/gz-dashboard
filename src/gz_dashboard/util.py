import argparse
import os
import sys
import urllib.request as request

from humanfriendly.terminal import ansi_wrap

from gz_dashboard import __version__ as dashboard_version


def resolve_uri(uri):
    if isinstance(uri, str):
        uri = file_or_url_type(uri)
    try:
        if isinstance(uri, request.Request):
            uri = request.urlopen(uri)
    except (RuntimeError, request.URLError) as e:
        print(ansi_wrap(str(e), color="red"), file=sys.stderr)
        return None

    return uri


def file_or_url_type(value):
    if os.path.exists(value) or "://" not in value:
        return argparse.FileType("r")(value)
    # use another user agent to avoid getting a 403 (forbidden) error,
    # since some websites blacklist or block unrecognized user agents
    return request.Request(
        value, headers={"User-Agent": f"gz-dashboard/{dashboard_version}"}
    )
