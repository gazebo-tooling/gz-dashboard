import argparse


def add_common_arguments(parser):
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    group = parser.add_argument_group("Common parameters")

    group.add_argument(
        "--debug", action="store_true", default=False, help="Show debug messages"
    )
