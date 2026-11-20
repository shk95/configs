"""Read the domain release version from a JSON declaration on stdin."""
# INV repository/release-tag-contract
import json
import re
import sys

VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z')

if __name__ == '__main__':
    try:
        version = json.load(sys.stdin)['version']
    except (ValueError, KeyError, TypeError):
        raise SystemExit('missing or invalid release declaration')
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise SystemExit('invalid source-owned SemVer')
    print(version)
