#!/usr/bin/env python3
"""Home Manager's finite-contract check/apply adapter; capture stays preview/save.

INV unixlike/host-written-payload-projected
"""
import argparse
import sys

from engine import CONTRACT, Refusal, Unavailable, adapt


def main():
    p = argparse.ArgumentParser(description="Check/apply enabled module settings units")
    p.add_argument("command", choices=["check", "apply"])
    p.add_argument("--unit", action="append", choices=list(CONTRACT["units"]), default=[])
    p.add_argument("--settings", action="append", default=[])
    p.add_argument("--host")
    p.add_argument("--hotkeys-host")
    p.add_argument("--target")
    p.add_argument("--hotkeys-target")
    args = p.parse_args()
    try:
        return adapt(args)
    except Unavailable as error:
        print("unavailable: " + str(error), file=sys.stderr)
        return 69
    except (Refusal, OSError, KeyError, TypeError) as error:
        print("refused: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
