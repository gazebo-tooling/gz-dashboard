import argparse
import copy
import os
import sys
import urllib.request as request

import yaml
from humanfriendly.terminal import ansi_wrap
from vcstool.commands.import_ import add_dependencies, generate_jobs, get_repositories
from vcstool.executor import execute_jobs, output_results

from gz_dashboard import __version__ as dashboard_version
from gz_dashboard.commands.command import add_common_arguments
from gz_dashboard.streams import set_streams


def get_parser():
    parser = argparse.ArgumentParser(
        description="Sync a set of distribution repositories to latest"
    )

    group = parser.add_argument_group("sync")
    group.add_argument(
        "--clean",
        action="store_true",
        default=False,
        help="Clean repository directories before sync",
    )
    group.add_argument(
        "--config",
        type=file_or_url_type,
        default="-",
        help="Where to read YAML from",
        metavar="FILE_OR_URL",
    )
    group.add_argument("--path", nargs="?", type=existing_dir, default=os.curdir)
    return parser


def existing_dir(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("Path '%s' does not exist." % path)
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("Path '%s' is not a directory." % path)
    return path


def file_or_url_type(value):
    print(value)
    if os.path.exists(value) or "://" not in value:
        return argparse.FileType("r")(value)
    # use another user agent to avoid getting a 403 (forbidden) error,
    # since some websites blacklist or block unrecognized user agents
    return request.Request(
        value, headers={"User-Agent": f"gz-dashboard/{dashboard_version}"}
    )


def get_distributions(yaml_file):
    try:
        root = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        raise RuntimeError(f"Input data is not valid yaml format: {e}")

    try:
        distributions = root["distributions"]
        return distributions
    except KeyError as e:
        raise RuntimeError(f"Input data is not valid format: {e}")


def sync_distro(name, config, args):
    print(f"sync_distro: {name}, {config}")
    config = file_or_url_type(config["url"])
    try:
        if isinstance(config, request.Request):
            config = request.urlopen(config)
    except (RuntimeError, request.URLError) as e:
        print(ansi_wrap(str(e), color="red"), file=sys.stderr)
        return 1

    print(config)

    args.path = os.path.join(args.path, name)
    args.recursive = False
    args.shallow = False
    args.retry = 2
    args.force = False
    args.skip_existing = False
    args.workers = 4

    if not os.path.exists(args.path):
        os.mkdir(args.path)

    repos = get_repositories(config)
    jobs = generate_jobs(repos, args)
    add_dependencies(jobs)

    print(f"Syncing distribution: {name}")
    results = execute_jobs(
        jobs, show_progress=True, number_of_workers=args.workers, debug_jobs=args.debug
    )

    output_results(results)
    any_error = any(r["returncode"] for r in results)

    return 1 if any_error else 0


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    parser = get_parser()
    add_common_arguments(parser)

    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args(args)

    try:
        config = args.config
        if isinstance(config, request.Request):
            config = request.urlopen(config)
    except (RuntimeError, request.URLError) as e:
        print(ansi_wrap(str(e), color="red"), file=sys.stderr)
        return 1

    distros = get_distributions(config)

    for (distro_name, distro_config) in distros.items():
        res = sync_distro(distro_name, distro_config, copy.copy(args))
        if res != 0:
            print(
                ansi_wrap(f"Error importing {distro_name}", color="red"),
                file=sys.stderr,
            )


if __name__ == "__main__":
    sys.exit(main())
