import sys

import yaml
from humanfriendly.terminal import ansi_wrap

from gz_dashboard.util import resolve_uri


def parse_distributions(yaml_file):
    try:
        root = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Input data is not valid yaml format: {e}")

    try:
        distributions = root["distributions"]
        return distributions
    except KeyError as e:
        raise RuntimeError(f"Input data is not valid format: {e}")


def get_distributions(uri):
    """
    Retrieve a list of distributions from a file or URL
    """

    uri = resolve_uri(uri)

    try:
        distributions = parse_distributions(uri)
        return distributions
    except (yaml.YAMLError, KeyError) as e:
        print(ansi_wrap(str(e), color="red"), file=sys.stderr)
        return {}
