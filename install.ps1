# rocky-skills installer (Windows PowerShell)
#
# Installs the hail-mary-rocky Claude Code skill. Other agents (Cursor, Codex,
# Gemini, Windsurf, Cline) are project-scoped — copy their adapter files into
# the project root manually. See README.md > Multi-agent support.
#
# Usage:
#   irm https://raw.githubusercontent.com/CaesiumY/rocky-skills/main/install.ps1 | iex
#   .\install.ps1 -Target project        # install into .\.claude\skills\ instead of ~\.claude\skills\
#   .\install.ps1 -WithSpinner           # also merge spinner verbs into settings.json
#   .\install.ps1 -Ref v1.2.3            # pin to a tag/branch (default: main)

[CmdletBinding()]
param(
    [ValidateSet('global','project')] [string]$Target = 'global',
    [switch]$WithSpinner,
    [string]$Ref = 'main'
)

$ErrorActionPreference = 'Stop'
$Repo = 'CaesiumY/rocky-skills'

if ($Target -eq 'project') {
    $skillsDir   = Join-Path $PWD '.claude\skills'
    $settingsFile = Join-Path $PWD '.claude\settings.json'
} else {
    $skillsDir   = Join-Path $HOME '.claude\skills'
    $settingsFile = Join-Path $HOME '.claude\settings.json'
}

$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ("rocky-skills." + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $workDir -Force | Out-Null

try {
    $tarballUrl = "https://codeload.github.com/$Repo/zip/refs/heads/$Ref"
    Write-Host "↓ downloading $Repo@$Ref"
    $zipPath = Join-Path $workDir 'repo.zip'
    Invoke-WebRequest -Uri $tarballUrl -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath $workDir -Force

    $extracted = Get-ChildItem -Path $workDir -Directory | Where-Object { $_.Name -like 'rocky-skills-*' } | Select-Object -First 1
    if (-not $extracted -or -not (Test-Path (Join-Path $extracted.FullName 'skills\hail-mary-rocky'))) {
        throw "could not find skills/hail-mary-rocky in archive"
    }

    New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
    $destPath = Join-Path $skillsDir 'hail-mary-rocky'
    if (Test-Path $destPath) {
        Remove-Item $destPath -Recurse -Force
    }
    Copy-Item -Path (Join-Path $extracted.FullName 'skills\hail-mary-rocky') -Destination $skillsDir -Recurse -Force
    Write-Host "✔ installed skill -> $destPath\"

    if ($WithSpinner) {
        $spinnerSrc = Join-Path $extracted.FullName 'skills\hail-mary-rocky\assets\spinner-verbs.json'
        if (-not (Test-Path $spinnerSrc)) {
            Write-Warning "spinner-verbs.json missing in archive, skipping spinner install"
        } else {
            $spinnerObj = Get-Content $spinnerSrc -Raw | ConvertFrom-Json
            $settingsDir = Split-Path $settingsFile -Parent
            New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
            if (Test-Path $settingsFile) {
                $current = Get-Content $settingsFile -Raw | ConvertFrom-Json
            } else {
                $current = [pscustomobject]@{}
            }
            if ($current.PSObject.Properties.Name -contains 'spinnerVerbs') {
                $current.spinnerVerbs = $spinnerObj.spinnerVerbs
            } else {
                $current | Add-Member -NotePropertyName spinnerVerbs -NotePropertyValue $spinnerObj.spinnerVerbs -Force
            }
            $current | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsFile -Encoding UTF8
            Write-Host "✔ merged spinner verbs into $settingsFile"
        }
    }

    Write-Host ""
    Write-Host "Done."
    Write-Host ""
    Write-Host "Other agents (project-scoped — copy these files into your project root):"
    Write-Host "  Cursor     -> .cursor/rules/rocky.md"
    Write-Host "  Windsurf   -> .windsurf/rules/rocky.md"
    Write-Host "  Cline      -> .clinerules"
    Write-Host "  Codex etc. -> AGENTS.md"
    Write-Host "  Gemini CLI -> GEMINI.md"
    Write-Host ""
    Write-Host 'Trigger phrases: "rocky", "로키", "rocky mode", "caveman mode", "헤일메리".'
    Write-Host "Full rules: $skillsDir\hail-mary-rocky\SKILL.md"
}
finally {
    if (Test-Path $workDir) { Remove-Item -Recurse -Force $workDir }
}
