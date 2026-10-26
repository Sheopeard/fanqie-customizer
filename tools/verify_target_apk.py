"""Check the declared 7.4.1.32 reflection contract without running the host app."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from dex_index import parse

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk',type=Path)
    args=parser.parse_args()
    contract=json.loads((Path(__file__).resolve().parents[1]/'tests/apk-contract-74132.json').read_text(encoding='utf8'))
    digest=hashlib.sha256(args.apk.read_bytes()).hexdigest()
    classes={}
    with zipfile.ZipFile(args.apk) as archive:
        for name in archive.namelist():
            if name.endswith('.dex'):
                classes.update(parse(archive.read(name)))
    failures=[]
    for group,key in [('methods','method'),('fields','field')]:
        for target in contract[group]:
            actual=classes.get(target['class'],{}).get(group,[])
            # Parser tuples become JSON arrays in the committed contract.
            if target[key] not in json.loads(json.dumps(actual)):
                failures.append(f"{target['class']}: {target[key]}")
    print(f"APK SHA256: {digest}")
    print(f"Matches inspected APK: {digest==contract['apk_sha256']}")
    for failure in failures:
        print('MISSING: '+failure)
    if failures:
        raise SystemExit(1)
    print(f"PASS: {len(contract['methods'])} method and {len(contract['fields'])} field contracts")
    print('Static checks only; phone UI behavior still needs manual verification.')

if __name__=='__main__':
    main()
