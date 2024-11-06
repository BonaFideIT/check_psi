#!/usr/bin/env python3

"""Nagios plugin to monitor current pressure stall information against desired thresholds"""

import re
import argparse
from enum import Enum
from nagiosplugin import (
    Resource,
    Metric,
    Check,
    ScalarContext,
    CheckError,
    guarded,
)


class KindEnum(Enum):
    """Enum representing the kinds of PSI values and their default thresholds"""

    Full = "full"
    Some = "some"

    @property
    def default_cpu(self):
        """default CPU thresholds"""

        return {
            KindEnum.Full: {
                "avg10": (3, 5),
                "avg60": (2, 3),
                "avg300": (1, 2),
            },
            KindEnum.Some: {
                "avg10": (5, 10),
                "avg60": (3, 7),
                "avg300": (2, 5),
            },
        }[self]

    @property
    def default_io(self):
        """default IO thresholds"""

        return {
            KindEnum.Full: {
                "avg10": (5, 10),
                "avg60": (3, 7),
                "avg300": (1, 3),
            },
            KindEnum.Some: {
                "avg10": (10, 20),
                "avg60": (7, 15),
                "avg300": (5, 10),
            },
        }[self]

    @property
    def default_memory(self):
        """default memory pressure thresholds"""

        return {
            KindEnum.Full: {
                "avg10": (3, 5),
                "avg60": (2, 3),
                "avg300": (1, 2),
            },
            KindEnum.Some: {
                "avg10": (5, 10),
                "avg60": (3, 7),
                "avg300": (2, 5),
            },
        }[self]


class PSI(Resource):
    """PSI values for a given resource at a set point in time"""

    def __init__(self, resource):
        """Set the source of SPI information"""

        self.resource = resource

    def probe(self):
        """Read all values from proc and create metrics"""

        fn = f"/proc/pressure/{self.resource}"
        try:
            with open(fn) as fd:
                for line in fd:
                    # check line syntax
                    match = re.match(
                        "^(some|full) avg10=([0-9.]+) avg60=([0-9.]+) avg300=([0-9.]+) total=([0-9]+)",
                        line.strip(),
                    )
                    if not match:
                        raise CheckError(
                            f"File {fn} contains unexpected syntax line: {line} "
                        )

                    # unpack values
                    kind, avg10, avg60, avg300, _ = match.groups()
                    kind = KindEnum(kind)

                    # generate metrics with names matching kwargs
                    yield Metric(
                        f"{kind.value}_avg10", float(avg10), "%", min=0, max=100
                    )
                    yield Metric(
                        f"{kind.value}_avg60", float(avg60), "%", min=0, max=100
                    )
                    yield Metric(
                        f"{kind.value}_avg300", float(avg300), "%", min=0, max=100
                    )

                # clean up file handle
                fd.close()

        except FileNotFoundError:
            raise CheckError(f"PSI file {self.file_path} not found.")
        except OSError as e:
            raise CheckError(f"Error reading PSI file {self.file_path}: {e}")


def parse_tuple(value):
    try:
        # Split the input string on ":" and convert each part to a float value
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("Input must contain exactly two numbers separated by ':'")
        if not 0 <= parts[0] <= parts[1] <= 100:
            raise ValueError(
                "Thresholds need to be in percentages and warn should not exceed critical."
            )
        return float(parts[0]), float(parts[1])
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid format: {e}")


def parse_args():
    """Parse command line arguments, build arguments from default values"""

    parser = argparse.ArgumentParser(description=__doc__)
    resource_choices = ("cpu", "io", "memory")
    fields = ("avg10", "avg60", "avg300")

    # generate one sub-parser per resource kind for choosing the correct defaults
    subparsers = parser.add_subparsers(dest="resource")
    for resource in resource_choices:

        # adds subcommands per-resource
        subparser = subparsers.add_parser(
            resource, help=f"Override default values for {resource} pressure."
        )
        for kind in KindEnum:
            for fn in fields:
                # adds arguments for all kinds and values
                subparser.add_argument(
                    f"--{kind.value}-{fn}",
                    metavar="WARN:CRIT",
                    type=parse_tuple,
                    default=getattr(kind, f"default_{resource}")[fn],
                    help=f'Override thresholds for warning and critical for {fn} time window for "{kind.value.lower()}" values',
                )

    return parser.parse_args()


@guarded
def main():
    """Software entry point"""

    # handle command line arguments
    args = parse_args()

    # generate contexts
    contexts = []
    for k, v in args._get_kwargs():
        if k == "resource":
            continue
        contexts.append(ScalarContext(k, *v))

    # run check
    check = Check(PSI(args.resource), *contexts)
    check.main()


if __name__ == "__main__":
    main()
