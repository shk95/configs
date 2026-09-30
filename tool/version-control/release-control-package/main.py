"""Retained entry, reached only after loader verification."""
# INV repository/release-control-preview-only
import json
from pathlib import Path
import sys

# -I ignores ambient Python path. This directory contains only manifest-verified files.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import Refusal, parse, read
from adapter import document
from engine import preview


def main():
    if len(sys.argv) != 5:
        return 1
    try:
        operating, transcript, request, approved = sys.argv[1:]
        result = preview(operating, document(read(transcript)),
                         parse(read(request), "request"), parse(read(approved), "approved"))
        if result is not None:
            print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    except (Refusal, OSError, ValueError, TypeError, KeyError):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
