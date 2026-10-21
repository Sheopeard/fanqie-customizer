param(
    [Parameter(Mandatory=$true)][string]$SdkRoot,
    [string]$JdkRoot = 'C:\Program Files\Zulu\zulu-25',
    [string]$BuildDirectory = (Join-Path $PSScriptRoot 'build')
)
$ErrorActionPreference='Stop'
$classes=Join-Path $BuildDirectory 'classes'
if(-not (Test-Path -LiteralPath $classes)){throw 'Build the module first, using build.ps1 with the same output directory.'}
$sdkJar=Get-ChildItem $SdkRoot -Recurse -Filter android.jar | Select-Object -First 1 -ExpandProperty FullName
if(-not $sdkJar){throw 'Android SDK platform android.jar is required.'}
$testClasses=Join-Path $BuildDirectory 'test-classes'
New-Item -ItemType Directory -Force $testClasses | Out-Null
$classPath="$classes;$sdkJar;$(Join-Path $PSScriptRoot 'libs\api-102.0.0.jar')"
$tests=Get-ChildItem (Join-Path $PSScriptRoot 'tests') -Filter '*.java' | Select-Object -ExpandProperty FullName
& (Join-Path $JdkRoot 'bin\javac.exe') --release 17 -encoding UTF-8 -cp $classPath -d $testClasses @tests
if($LASTEXITCODE -ne 0){throw 'Test compilation failed'}
foreach($test in (Get-ChildItem (Join-Path $PSScriptRoot 'tests') -Filter '*Test.java' | Sort-Object Name | Select-Object -ExpandProperty BaseName)) {
    $class=if($test -eq 'RulesTest'){$test}else{'io.github.mianxyz.fanqiecustomizer.'+$test}
    & (Join-Path $JdkRoot 'bin\java.exe') -cp "$testClasses;$classPath" $class
    if($LASTEXITCODE -ne 0){throw "$test failed"}
}
