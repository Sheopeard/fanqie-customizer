param(
    [Parameter(Mandatory=$true)][string]$SdkRoot,
    [Parameter(Mandatory=$true)][string]$KeyStorePath,
    [string]$JdkRoot = 'C:\Program Files\Java\jdk-17',
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'build')
)
$ErrorActionPreference='Stop'
$env:JAVA_HOME=$JdkRoot
$env:PATH=(Join-Path $JdkRoot 'bin')+';'+$env:PATH
$platform=Join-Path $SdkRoot 'platforms\android-36\android.jar'
$aapt=Join-Path $SdkRoot 'build-tools\36.0.0\aapt2.exe'
if(-not (Test-Path $platform) -or -not (Test-Path $aapt)){throw 'SDK must contain Android platform 36 and Build Tools 36.0.0'}
$tools=Split-Path $aapt
$api=Join-Path $PSScriptRoot 'libs\api-102.0.0.jar'
$service=Join-Path $PSScriptRoot 'libs\service-102.0.0.jar'
$interface=Join-Path $PSScriptRoot 'libs\interface-102.0.0.jar'
$classpath="$platform;$api;$service;$interface"
New-Item -ItemType Directory -Force $OutputDirectory,(Join-Path $OutputDirectory 'classes'),(Join-Path $OutputDirectory 'dex') | Out-Null
function Check([string]$Step){if($LASTEXITCODE -ne 0){throw "$Step failed ($LASTEXITCODE)"}}
$classes=Join-Path $OutputDirectory 'classes'
$sources=Get-ChildItem (Join-Path $PSScriptRoot 'src') -Recurse -Filter *.java | Select-Object -ExpandProperty FullName
& (Join-Path $JdkRoot 'bin\javac.exe') --release 17 -encoding UTF-8 -cp $classpath -d $classes @sources
Check 'javac'
$classJar=Join-Path $OutputDirectory 'classes.jar'
& (Join-Path $JdkRoot 'bin\jar.exe') "-J-Djava.io.tmpdir=$OutputDirectory" --create --file $classJar -C $classes .
Check 'jar'
& (Join-Path $tools 'd8.bat') --lib $platform --classpath $api --min-api 28 --output (Join-Path $OutputDirectory 'dex') $classJar $service $interface
Check 'd8'
$resources=Join-Path $OutputDirectory 'resources.zip'
& $aapt compile --dir (Join-Path $PSScriptRoot 'res') -o $resources
Check 'resources'
$unsigned=Join-Path $OutputDirectory 'unsigned.apk'
& $aapt link -o $unsigned -I $platform --manifest (Join-Path $PSScriptRoot 'AndroidManifest.xml') --min-sdk-version 28 --target-sdk-version 35 $resources
Check 'link'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[System.IO.Compression.ZipFile]::Open($unsigned,[System.IO.Compression.ZipArchiveMode]::Update)
try {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $OutputDirectory 'dex\classes.dex'),'classes.dex') | Out-Null
    foreach($name in @('java_init.list','scope.list','module.prop')) {
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $PSScriptRoot "resources\META-INF\xposed\$name"),"META-INF/xposed/$name") | Out-Null
    }
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $PSScriptRoot 'LICENSE-APACHE-2.0.txt'),'META-INF/licenses/libxposed-LICENSE.txt') | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $PSScriptRoot 'THIRD_PARTY_NOTICES.md'),'META-INF/licenses/libxposed-NOTICES.txt') | Out-Null
} finally { $zip.Dispose() }
$aligned=Join-Path $OutputDirectory 'aligned.apk'
& (Join-Path $tools 'zipalign.exe') -f -p 4 $unsigned $aligned
Check 'zipalign'
if(-not (Test-Path -LiteralPath $KeyStorePath)) {
    New-Item -ItemType Directory -Force (Split-Path $KeyStorePath) | Out-Null
    & (Join-Path $JdkRoot 'bin\keytool.exe') -genkeypair -keystore $KeyStorePath -storepass android -keypass android -alias fanqie-dev -dname 'CN=Fanqie Local Development' -keyalg RSA -keysize 2048 -validity 3650
    Check 'keytool'
}
$apk=Join-Path $OutputDirectory 'fanqie-customizer-5.0.5.74132.apk'
& (Join-Path $tools 'apksigner.bat') sign --ks $KeyStorePath --ks-key-alias fanqie-dev --ks-pass pass:android --key-pass pass:android --out $apk $aligned
Check 'sign'
& (Join-Path $tools 'apksigner.bat') verify --verbose $apk
Check 'verify'
Get-FileHash -Algorithm SHA256 $apk
