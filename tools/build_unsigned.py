"""Portable, key-free build and rule tests for GitHub Actions and local checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ANDROID = '{http://schemas.android.com/apk/res/android}'

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def run(args, log):
    with log.open('a', encoding='utf8') as stream:
        subprocess.run([str(a) for a in args], cwd=ROOT, check=True,
                       stdout=stream, stderr=subprocess.STDOUT)

def build(sdk, output, jdk=None):
    sdk, output = sdk.resolve(), output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # A fresh private staging directory prevents stale classes from entering the APK.
    with tempfile.TemporaryDirectory(prefix='fanqie-build-', dir=output) as temporary:
        stage = Path(temporary)
        tools = sdk / 'build-tools' / '36.0.0'
        platform = sdk / 'platforms' / 'android-36' / 'android.jar'
        suffix = '.exe' if os.name == 'nt' else ''
        def java(name):
            path = jdk / 'bin' / (name + suffix) if jdk else shutil.which(name)
            if not path or not Path(path).is_file():
                raise ValueError(f'Missing JDK tool: {name}')
            return path
        def android(name):
            ext = '.bat' if os.name == 'nt' and name == 'd8' else suffix
            path = tools / (name + ext)
            if not path.is_file():
                raise ValueError(f'Missing Android build tool: {name}')
            return path
        if not platform.is_file():
            raise ValueError('Android platform android-36 is required')
        # Verify vendored dependencies before any of their class files are processed.
        for line in (ROOT / 'libs/SHA256SUMS.txt').read_text().splitlines():
            expected, filename = line.split(maxsplit=1)
            filename = filename.lstrip('*').replace('libs/', '').replace('libs\\', '')
            if Path(filename).name != filename or digest(ROOT / 'libs' / filename) != expected.lower():
                raise ValueError('Vendored dependency checksum mismatch')
        api = ROOT / 'libs/api-102.0.0.jar'
        service = ROOT / 'libs/service-102.0.0.jar'
        interface = ROOT / 'libs/interface-102.0.0.jar'
        classes, dex, tests = stage / 'classes', stage / 'dex', stage / 'test-classes'
        for folder in (classes, dex, tests):
            folder.mkdir()
        log = output / 'build-and-tests.log'
        log.write_text('', encoding='utf8')
        classpath = os.pathsep.join(map(str, (platform, api, service, interface)))
        sources = sorted((ROOT / 'src').rglob('*.java'))
        run([java('javac'), '--release', '17', '-encoding', 'UTF-8', '-cp', classpath,
             '-d', classes, *sources], log)
        jar = stage / 'classes.jar'
        run([java('jar'), '--create', '--file', jar, '-C', classes, '.'], log)
        # d8.bat uses JAVA_HOME; setting it here also supports explicit local JDK selection.
        previous = os.environ.get('JAVA_HOME')
        if jdk:
            os.environ['JAVA_HOME'] = str(jdk)
        try:
            run([android('d8'), '--lib', platform, '--classpath', api, '--min-api', '28',
                 '--output', dex, jar, service, interface], log)
        finally:
            if jdk:
                if previous is None:
                    os.environ.pop('JAVA_HOME', None)
                else:
                    os.environ['JAVA_HOME'] = previous
        resources = stage / 'resources.zip'
        run([android('aapt2'), 'compile', '--dir', ROOT / 'res', '-o', resources], log)
        unsigned = stage / 'unsigned.apk'
        run([android('aapt2'), 'link', '-o', unsigned, '-I', platform, '--manifest',
             ROOT / 'AndroidManifest.xml', '--min-sdk-version', '28',
             '--target-sdk-version', '35', resources], log)
        with zipfile.ZipFile(unsigned, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(dex.glob('classes*.dex')):
                archive.write(path, path.name)
            for name in ('java_init.list', 'scope.list', 'module.prop'):
                archive.write(ROOT / 'resources/META-INF/xposed' / name, 'META-INF/xposed/' + name)
            archive.write(ROOT / 'LICENSE-APACHE-2.0.txt', 'META-INF/licenses/libxposed-LICENSE.txt')
            archive.write(ROOT / 'THIRD_PARTY_NOTICES.md', 'META-INF/licenses/libxposed-NOTICES.txt')
        manifest = ET.parse(ROOT / 'AndroidManifest.xml').getroot()
        version = manifest.attrib[ANDROID + 'versionName']
        if not re.fullmatch(r'[0-9.]+', version):
            raise ValueError('Unexpected module version name')
        apk = output / f'fanqie-customizer-{version}-unsigned.apk'
        run([android('zipalign'), '-f', '-p', '4', unsigned, apk], log)
        run([android('zipalign'), '-c', '-p', '4', apk], log)
        testpath = os.pathsep.join(map(str, (classes, platform, api)))
        testfiles = sorted((ROOT / 'tests').glob('*Test.java'))
        run([java('javac'), '--release', '17', '-encoding', 'UTF-8', '-cp', testpath,
             '-d', tests, *testfiles], log)
        passed = []
        for path in testfiles:
            match = re.search(r'^package\s+([\w.]+);', path.read_text(encoding='utf8'), re.M)
            name = (match.group(1) + '.' if match else '') + path.stem
            run([java('java'), '-cp', str(tests) + os.pathsep + testpath, name], log)
            passed.append(path.stem)
        result = {'artifact': apk.name, 'sha256': digest(apk), 'signed': False,
                  'phone_verified': False, 'package': manifest.attrib['package'],
                  'version_name': version, 'version_code': int(manifest.attrib[ANDROID + 'versionCode']),
                  'tests_passed': passed}
        (output / 'build-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        print(json.dumps(result))
        return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, default=os.environ.get('ANDROID_HOME'))
    parser.add_argument('--output', type=Path, default=ROOT / 'build/cloud')
    parser.add_argument('--jdk', type=Path, default=os.environ.get('JAVA_HOME'))
    args = parser.parse_args()
    if not args.sdk:
        parser.error('--sdk or ANDROID_HOME is required')
    build(args.sdk, args.output, args.jdk)
