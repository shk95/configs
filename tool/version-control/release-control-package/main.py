"""Retained entry, reached only after loader verification."""
# INV repository/release-control-preview-only
import base64
import json
from pathlib import Path
import sys

# -I ignores ambient Python path. This directory contains only manifest-verified files.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import Refusal, parse, read
from adapter import document
from engine import preview, project_range, reduce


def replay(directory, transcript, approved, before, prior):
    projection, stage, pending = project_range(directory, transcript, approved, before, prior)
    from records import history
    events,_=history(Path(directory)/'history',before,prior)
    config=parse(read(Path(directory)/'config/operating.tsv'),'config')
    result={"projection": base64.b64encode(projection).decode("ascii"), "stage": stage, "proposed": pending,
            'preparations':reduce(events,config,transcript)['preparations']}
    from records import require
    require(len(json.dumps(result,sort_keys=True).encode())<=4096, 'preparation-replay-output-bound')
    return result


def main():
    if len(sys.argv) == 8 and sys.argv[1] == "--preview-range":
        try:
            _, _, directory, transcript, request, approved, before, prior = sys.argv
            result = preview(directory, document(read(transcript)), parse(read(request), "request"),
                             parse(read(approved), "approved"), int(before), prior)
            if result is not None:
                print(json.dumps(result, sort_keys=True, ensure_ascii=True))
            return 0
        except (Refusal, OSError, ValueError, TypeError, KeyError):
            return 1
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
