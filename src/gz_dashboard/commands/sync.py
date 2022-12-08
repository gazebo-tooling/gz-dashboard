import argparse
import sys

from gz_dashboard.streams import set_streams


def get_parser():
    parser = argparse.ArgumentParser(
        description="Sync a set of distribution repositories to latest"
    )

    return parser


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    get_parser()

    if args is None:
        args = sys.argv[1:]


if __name__ == "__main__":
    sys.exit(main())
