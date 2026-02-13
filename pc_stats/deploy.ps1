param(
    [string]$Port = "COM8",
    [switch]$AsMain
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $scriptRoot ".venv-deploy"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$requirements = Join-Path $scriptRoot "requirements-deploy.txt"

if (-not (Test-Path $venvPython)) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyLauncher) {
        & py -3 -m venv $venvDir
    } else {
        & python -m venv $venvDir
    }
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirements

function Copy-ToDevice {
    param(
        [string]$Source,
        [string]$Target
    )

    & $venvPython -m mpremote connect $Port fs cp $Source ":$Target"
}

Copy-ToDevice -Source "pc_stats/device/lcd_1in28.py" -Target "lcd_1in28.py"
Copy-ToDevice -Source "pc_stats/device/pc_stats_display.py" -Target "pc_stats_display.py"

if ($AsMain) {
    Copy-ToDevice -Source "pc_stats/device/pc_stats_display.py" -Target "main.py"
}

& $venvPython -m mpremote connect $Port reset
