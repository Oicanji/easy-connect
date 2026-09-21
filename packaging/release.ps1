#Requires -Version 5.1
param(
    [switch]$Minor,
    [switch]$Major,
    [switch]$SkipBump,
    [string]$Version
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root "pyproject.toml"))) {
    $Root = $PSScriptRoot
}
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Python do venv nao encontrado: $Python"
}

function Get-CurrentVersion {
    $init = Get-Content -Raw (Join-Path $Root "src\easy_connect\__init__.py")
    if ($init -match '__version__\s*=\s*"([^"]+)"') {
        return $Matches[1]
    }
    throw "Nao foi possivel ler a versao atual em src\easy_connect\__init__.py"
}

function Get-NextVersion {
    param([string]$Current)

    if ($Version) {
        if ($Version -notmatch '^\d+\.\d+\.\d+$') {
            throw "Versao invalida: $Version (use X.Y.Z)"
        }
        return $Version
    }

    $parts = $Current.Split('.') | ForEach-Object { [int]$_ }
    if ($parts.Count -ne 3) {
        throw "Versao atual invalida: $Current"
    }

    $flags = @($Major.IsPresent, $Minor.IsPresent) | Where-Object { $_ }
    if ($flags.Count -gt 1) {
        throw "Use apenas um de -Major ou -Minor"
    }

    if ($Major) {
        return "{0}.0.0" -f ($parts[0] + 1)
    }
    if ($Minor) {
        return "{0}.{1}.0" -f $parts[0], ($parts[1] + 1)
    }
    return "{0}.{1}.{2}" -f $parts[0], $parts[1], ($parts[2] + 1)
}

function Set-FileText {
    param(
        [string]$Path,
        [string]$Content
    )
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

function Update-VersionFiles {
    param(
        [string]$OldVersion,
        [string]$NewVersion
    )

    $tuple = ($NewVersion.Split('.') + @('0'))[0..3] -join ', '
    $files = @{
        (Join-Path $Root "src\easy_connect\__init__.py") = {
            param($text)
            $text -replace '__version__\s*=\s*"[^"]+"', "__version__ = `"$NewVersion`""
        }
        (Join-Path $Root "pyproject.toml") = {
            param($text)
            $text -replace '(?m)^version\s*=\s*"[^"]+"', "version = `"$NewVersion`""
        }
        (Join-Path $Root "packaging\windows_setup.py") = {
            param($text)
            $text -replace 'APP_VERSION\s*=\s*"[^"]+"', "APP_VERSION = `"$NewVersion`""
        }
        (Join-Path $Root "packaging\easyconnect.iss") = {
            param($text)
            $text -replace '#define MyAppVersion "[^"]+"', "#define MyAppVersion `"$NewVersion`""
        }
    }

    foreach ($path in $files.Keys) {
        if (-not (Test-Path $path)) {
            throw "Arquivo nao encontrado: $path"
        }
        $bytes = [System.IO.File]::ReadAllBytes($path)
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $text = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
        } else {
            $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        }
        $updated = & $files[$path] $text
        if ($updated -eq $text -and $OldVersion -ne $NewVersion) {
            throw "Falha ao atualizar versao em $path"
        }
        Set-FileText -Path $path -Content $updated
    }

    $versionInfo = @"
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($tuple),
    prodvers=($tuple),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Easy Connect'),
        StringStruct(u'FileDescription', u'Easy Connect v$NewVersion'),
        StringStruct(u'FileVersion', u'$NewVersion'),
        StringStruct(u'InternalName', u'EasyConnect'),
        StringStruct(u'OriginalFilename', u'EasyConnect.exe'),
        StringStruct(u'ProductName', u'Easy Connect'),
        StringStruct(u'ProductVersion', u'$NewVersion')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"@
    Set-FileText -Path (Join-Path $Root "packaging\file_version_info.txt") -Content $versionInfo
}

function Invoke-PyInstaller {
    param([string]$SpecPath)

    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    & $Python -m PyInstaller --noconfirm --clean $SpecPath
    $code = $LASTEXITCODE
    $ErrorActionPreference = $previous
    if ($code -ne 0) {
        throw "Falha no PyInstaller: $SpecPath"
    }
}

function Invoke-Build {
    param([string]$ExpectedVersion)

    Write-Host "Compilando aplicativo..."
    Invoke-PyInstaller -SpecPath (Join-Path $Root "packaging\easyconnect.spec")

    Write-Host "Compilando instalador..."
    Invoke-PyInstaller -SpecPath (Join-Path $Root "packaging\setup.spec")

    $portable = Join-Path $Root "dist\EasyConnect-Portable.zip"
    if (Test-Path $portable) {
        Remove-Item $portable -Force
    }
    Write-Host "Gerando pacote portatil..."
    Compress-Archive -Path (Join-Path $Root "dist\EasyConnect") -DestinationPath $portable

    $appExe = Join-Path $Root "dist\EasyConnect\EasyConnect.exe"
    $setupExe = Join-Path $Root "dist\EasyConnect-Setup.exe"
    foreach ($path in @($appExe, $setupExe, $portable)) {
        if (-not (Test-Path $path)) {
            throw "Artefato nao gerado: $path"
        }
    }

    $appInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($appExe)
    $setupInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($setupExe)
    if ($appInfo.ProductVersion -ne $ExpectedVersion) {
        throw "Versao do app ($($appInfo.ProductVersion)) difere de $ExpectedVersion"
    }
    if ($setupInfo.ProductVersion -ne $ExpectedVersion) {
        throw "Versao do instalador ($($setupInfo.ProductVersion)) difere de $ExpectedVersion"
    }

    Write-Host ""
    Write-Host "Versao: $ExpectedVersion"
    Get-Item $appExe, $setupExe, $portable | ForEach-Object {
        "{0,8:N1} MB  {1}" -f ($_.Length / 1MB), $_.FullName
    }
}

$current = Get-CurrentVersion
if ($SkipBump) {
    $target = $current
    Write-Host "Mantendo versao $target"
} else {
    $target = Get-NextVersion -Current $current
    Write-Host "Bump $current -> $target"
    Update-VersionFiles -OldVersion $current -NewVersion $target
}

Invoke-Build -ExpectedVersion $target
