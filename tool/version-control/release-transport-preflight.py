"""Read-only source/template inspection. No operating mode is exposed."""
# INV repository/authenticated-release-transport
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

FILES=tuple('tool/version-control/'+name for name in (
 'release-control-loader.py','release-transport','release-transport.py',
 'release-transport-retained.py','release-transport-preflight.py'))
FIELDS={'format','transport-source','transport-manifest','operating-repository','operating-ref',
 'environment','connection','repository-id','workflow-id','workflow-path','job-name','actors',
 'approved-master','approved-control','approved-manifest','bootstrap-record','public-evidence',
 'writer-single-job','rerun-serialization','permissions-reviewed','protection-reviewed','manual-authorization'}


def main():
    parser=argparse.ArgumentParser(description='Disabled operating transport source preflight')
    parser.add_argument('mode',choices=['preflight']);parser.add_argument('--source',required=True)
    parser.add_argument('--template',required=True)
    args=parser.parse_args()
    try:
        if not re.fullmatch('[a-f0-9]{40}',args.source):raise ValueError()
        root=Path(__file__).resolve().parents[2]
        env={k:v for k,v in os.environ.items() if k in {'PATH','SYSTEMROOT','SystemRoot','WINDIR','COMSPEC','ComSpec','PATHEXT','TEMP','TMP','TMPDIR','LANG','LC_ALL','TZ'}}
        env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0')
        command=['git','--no-replace-objects','-C',str(root)]
        # Public source only; no operating connection or token is consulted.
        manifest=subprocess.check_output(command+['show',args.source+':tool/version-control/release-transport.manifest.tsv'],stderr=subprocess.DEVNULL,env=env)
        rows=manifest.decode('ascii').splitlines()
        if rows[0]!='format\t1' or not manifest.endswith(b'\n'):raise ValueError()
        names=[]
        for row in rows[1:]:
            kind,name,expected=row.split('\t');names.append(name)
            if kind!='file' or not re.fullmatch('[a-f0-9]{64}',expected):raise ValueError()
            data=subprocess.check_output(command+['show',args.source+':'+name],stderr=subprocess.DEVNULL,env=env)
            if hashlib.sha256(data).hexdigest()!=expected:raise ValueError()
        if names!=sorted(FILES):raise ValueError()
        value=json.loads(Path(args.template).read_text())
        if set(value)!=FIELDS or type(value['format']) is not int or value['format']!=1:raise ValueError()
        unresolved=sorted(k for k,v in value.items() if v in (None,'UNRESOLVED',False,[]) and k!='format')
        # Even resolved input text cannot enable transport. Separate source/ref/
        # Environment provenance and authenticated operating authorization are needed.
        print(json.dumps({'kind':'transport-source-preflight','source':args.source,
              'manifest':hashlib.sha256(manifest).hexdigest(),'unresolved':unresolved,
              'enabled':False,'production_certification':False},sort_keys=True))
        return 0
    except (OSError,ValueError,KeyError,subprocess.SubprocessError):
        print('release-transport: refused',file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
