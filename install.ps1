<#
  install_env.ps1
  ----------------
  Interactive Windows development environment setup.

  - Installs winget (if missing)
  - Lets you select & install apps from apps.json
  - Lets you select & configure shells from shells.json
  - "All in one" option

  Prerequisite: PowerShell 7+ recommended.
#>

#==== 1) Load JSON catalogs ====#

# Path to apps.json
$appJson = Join-Path $PSScriptRoot 'json/apps.json'
if (Test-Path $appJson) {
    $appSections = Get-Content $appJson -Raw | ConvertFrom-Json

    $appCatalog = @()
    foreach ($section in $appSections) {
        # Add "Select All" option for this section
        $appCatalog += [PSCustomObject]@{
            section = $section.section
            name    = "-- All in $($section.section) --"
            id      = "section-all-$($section.section)"
        }

        # Add real apps
        foreach ($app in $section.apps) {
            $appCatalog += [PSCustomObject]@{
                section = $section.section
                name    = $app.name
                id      = $app.id
            }
        }
    }

    # Example: Output grouped apps
    foreach ($section in $appSections) {
        Write-Host "=== $($section.section) ===" -ForegroundColor Cyan
        foreach ($app in $section.apps) {
            Write-Host "  - $($app.name)"
        }
    }
} else {
    Write-Error "File not found: $appJson"
}

# Path to shells.json
$shellJson = Join-Path $PSScriptRoot 'json/shells.json'

if (Test-Path $shellJson) {
    $shellAll = (Get-Content $shellJson -Raw | ConvertFrom-Json).shells
    $shellCatalog = $shellAll | Where-Object { -not $_.hidden }

    # Example: Output visible shells
    foreach ($shell in $shellCatalog) {
        Write-Host "Shell: $($shell.name)"
    }
} else {
    Write-Error "File not found: $shellJson"
}

#==== 2) Helper: Interactive checkbox list ====#
function Show-CheckboxList {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [psobject[]]$Items,
        [string]$Prompt = 'Up/Down to move, Space to toggle, Enter to confirm'
    )

    # State arrays
    $count = $Items.Count
    $selected = New-Object bool[] $count
    $pos = 0
    $done = $false

    while (-not $done) {
        Clear-Host
        Write-Host $Prompt -ForegroundColor Cyan

        $currentSection = $null
        for ($i = 0; $i -lt $count; $i++) {
            $item = $Items[$i]

            # Print section header if new
            if ($item.section -and $item.section -ne $currentSection) {
                $currentSection = $item.section
                Write-Host "`n=== $currentSection ===" -ForegroundColor Magenta
            }

            $box = if ($selected[$i]) { '[x]' } else { '[ ]' }
            $label = $item.name
            if ($i -eq $pos) {
                Write-Host " > $box $label" -ForegroundColor Yellow
            }
            else {
                Write-Host "   $box $label"
            }
        }

        # Read a key
        $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        switch ($key.VirtualKeyCode) {
            38 { $pos = ($pos - 1 + $count) % $count }   # Up
            40 { $pos = ($pos + 1) % $count }            # Down
            32 {
                $item = $Items[$pos]
                if ($item.id -like "section-all-*") {
                    # Toggle all apps in this section
                    $sectionName = $item.section
                    $toggleTo = -not $selected[$pos]
                    for ($j = 0; $j -lt $count; $j++) {
                        if ($Items[$j].section -eq $sectionName -and
                                $Items[$j].id -notlike "section-all-*") {
                            $selected[$j] = $toggleTo
                        }
                    }
                    $selected[$pos] = $toggleTo
                }
                else {
                    $selected[$pos] = -not $selected[$pos]
                }
            }
            13 { $done = $true }                         # Enter
        }
    }

    # Return only checked items (skip section toggles)
    $result = @()
    for ($i = 0; $i -lt $count; $i++) {
        if ($selected[$i] -and $Items[$i].id -notlike "section-all-*") {
            $result += $Items[$i]
        }
    }
    return $result
}


#==== 3) winget installer ====#
function Install-Winget {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host 'winget is already installed.' -ForegroundColor Green
        return
    }

    Write-Host 'Installing winget...' -ForegroundColor Yellow
    $uri = 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
    $out = Join-Path $env:TEMP 'DesktopAppInstaller.msixbundle'
    Invoke-WebRequest -Uri $uri -OutFile $out -UseBasicParsing
    Add-AppxPackage -Path $out

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host 'winget installed successfully.' -ForegroundColor Green
    }
    else {
        Write-Host 'Failed to install winget. Please install manually.' -ForegroundColor Red
        Pause
        exit 1
    }
}


#==== 4) Install applications via winget ====#
function Install-Apps {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [psobject[]]$AppsToInstall
    )

    $total = $AppsToInstall.Count
    if ($total -eq 0) { return }

    for ($i = 0; $i -lt $total; $i++) {
        $app = $AppsToInstall[$i]
        $percent = [int]((($i + 1) / $total) * 100)

        # overall progress bar
        Write-Progress -Activity 'Installing Applications' -Status "[$($i+1)/$total] $($app.name)" -PercentComplete $percent

        # header
        Write-Host "-> [$($app.section)] $($app.name) ($percent%)" -ForegroundColor Cyan

        # show winget's native progress
        & winget install -e --id $app.id --accept-source-agreements --accept-package-agreements

        if ($LASTEXITCODE -eq 0) {
            Write-Host '   [OK]' -ForegroundColor Green
        }
        else {
            Write-Host '   [FAILED]' -ForegroundColor Red
        }
    }

    # clear progress bar
    Write-Progress -Activity 'Installing Applications' -Completed
    Write-Host "All installs finished." -ForegroundColor Cyan
    Pause
}


#==== 5) Shell configuration functions ====#
function Set-Nu {
    [CmdletBinding()]
    param()

    Write-Host "Configuring NuShell..." -ForegroundColor Cyan

    # 1) Create ~/Documents/Sampong_dotfile/nu
    $dotDir = Join-Path $HOME'\Documents\Sampong_dotfile'
    $nuDir = Join-Path $dotDir'\nu'
    if (-not (Test-Path $nuDir)) {
        New-Item -Path $nuDir -ItemType Directory -Force | Out-Null
        '# NuShell main profile' | Set-Content (Join-Path $nuDir 'main_profile.nu')
        Write-Host '-> Created NuShell dotfiles.' -ForegroundColor Green
    }

    # 2) Create appdata nushell dir & files
    $nuCfg = Join-Path $env:APPDATA'\nushell'
    $envNu = Join-Path $nuCfg'\env.nu'
    $confNu = Join-Path $nuCfg'\config.nu'
    New-Item -Path $nuCfg -ItemType Directory -Force | Out-Null
    New-Item -Path $envNu,$confNu -ItemType File -Force | Out-Null

    # 3) Apply Oh-My-Posh theme if found
    $themePaths = @(
        Join-Path $env:LOCALAPPDATA'\Programs\oh-my-posh\themes\spaceship.omp.json'
        Join-Path $env:PROGRAMFILES'\oh-my-posh\themes\spaceship.omp.json'
    )
    $theme = $themePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($theme) {
        # build the line without any backtick-escape
        $line = 'oh-my-posh init nu --config "' + $theme + '" '
        if (-not (Select-String -Path $envNu -Pattern 'oh-my-posh init nu' -Quiet)) {
            Add-Content -Path $envNu -Value "`n$line"
            Write-Host '-> Applied Oh-My-Posh to NuShell.' -ForegroundColor Green
        }
    }
    else {
        Write-Host 'Warning: spaceship theme not found for NuShell.' -ForegroundColor Yellow
    }

    # 4) Source your custom profile
    $include = 'use ~/Documents/Sampong_dotfile/nu/main_profile.nu'
    if (-not (Select-String -Path $confNu -Pattern [regex]::Escape($include) -Quiet)) {
        Add-Content -Path $confNu -Value $include
    }

    Write-Host 'NuShell configuration complete.' -ForegroundColor Green
    Pause
}

function Set-Bash {
    Write-Host "Configuring Bash..." -ForegroundColor Cyan

    $dotDir = Join-Path $HOME'\Documents\Sampong_dotfile'
    $bashDir = Join-Path $dotDir'\bash'
    $mainSh = Join-Path $bashDir'\main.sh'
    if (-not (Test-Path $bashDir)) {
        New-Item $bashDir -ItemType Directory -Force | Out-Null
        '# Bash main script' | Set-Content $mainSh
        Write-Host '-> Created Bash dotfiles.' -ForegroundColor Green
    }

    $bashrc = Join-Path $HOME'\.bashrc'
    if (-not (Test-Path $bashrc)) {
        New-Item $bashrc -ItemType File -Force | Out-Null
    }
    $sourceLine = "source `"$mainSh`""
    if (-not (Select-String -Path $bashrc -Pattern [regex]::Escape($sourceLine) -Quiet)) {
        "`n# Source Sampong bash customizations`n$sourceLine" | Add-Content $bashrc
        Write-Host '-> Updated .bashrc.' -ForegroundColor Green
    }

    Write-Host 'Bash configuration complete.' -ForegroundColor Green
    Pause
}

function Set-Posh {
    [CmdletBinding()]
    param(
        [ValidateSet('spaceship','paradox','jandedobbeleer')]
        [string]$Theme = 'spaceship'
    )

    Write-Host "Configuring PowerShell profile..." -ForegroundColor Cyan

    try {
        # Determine profile path & directory
        $profilePath = $PROFILE
        $profileDir  = Split-Path -Path $profilePath -Parent

        # Create folder & file if missing
        if (-not (Test-Path -Path $profileDir -PathType Container)) {
            New-Item -Path $profileDir -ItemType Directory -Force | Out-Null
        }
        if (-not (Test-Path -Path $profilePath -PathType Leaf)) {
            New-Item -Path $profilePath -ItemType File -Force | Out-Null
        }

        # Optional: install modules if not already present
        # if (-not (Get-Module -ListAvailable -Name oh-my-posh)) {
        #     Install-Module oh-my-posh -Scope CurrentUser -Force
        # }
        # if (-not (Get-Module -ListAvailable -Name PSReadLine)) {
        #     Install-Module PSReadLine -Scope CurrentUser -Force
        # }

        # Lines to ensure in profile
        $entries = @(
            "Import-Module (Resolve-Path '~/Documents/Sampong_dotfile/PowerShell/posh_profile.ps1')",
            'Import-Module -Name Microsoft.WinGet.CommandNotFound',
            'Invoke-Expression "$(vfox activate pwsh)"'
        )

        foreach ($entry in $entries) {
            $escaped = [regex]::Escape($entry)
            if (-not (Select-String -Path $profilePath -Pattern $escaped -Quiet)) {
                # prepend newline so added entries stay on their own line
                Add-Content -Path $profilePath -Value "`n$entry"
            }
        }

        Write-Host "-> PowerShell profile updated at $profilePath" `
                  -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to configure profile: $_"
    }

    Read-Host -Prompt "Press Enter to continue"
}

#==== 6) Menu display ====#
function Show-Menu {
    Clear-Host
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '      DEV ENVIRONMENT SETUP MENU        ' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '1) Install winget (if missing)'
    Write-Host '2) Install applications'
    Write-Host '3) Configure shells'
    Write-Host '4) Run ALL steps'
    Write-Host '0) Exit'
}


#==== 7) Main loop ====#
$done = $false
do {
    Show-Menu
    $opt = Read-Host 'Select an option'

    switch ($opt) {
        '1' {
            Install-Winget
            Pause
        }

        '2' {
            # Create a Back option
            $appBackOption = [PSCustomObject]@{
                id      = "back"
                name    = "-- Back to Main Menu --"
                section = ""
            }

            # Add it to the app list
            $appListWithBack = @($appBackOption) + $appCatalog

            # Select apps
            $toInstall = Show-CheckboxList -Items $appListWithBack -Prompt 'Select apps to install: Up/Down, Space, Enter'

            if ($toInstall.id -contains "back") {
                Write-Host "Returning to main menu..." -ForegroundColor Cyan
                Pause
            }
            elseif ($toInstall.Count -eq 0) {
                Write-Host 'No apps selected.' -ForegroundColor Red
                Pause
            }
            else {
                Install-Apps -AppsToInstall $toInstall
            }
        }

        '3' {
            # Create a Back option using Select-Object
            $backOption = New-Object PSObject
            $backOption | Add-Member -MemberType NoteProperty -Name "id" -Value "back"
            $backOption | Add-Member -MemberType NoteProperty -Name "name" -Value "-- Back to Main Menu --"
            $backOption | Add-Member -MemberType NoteProperty -Name "function" -Value ""

            # Add it to the shell list
            $shellListWithBack = @($backOption) + $shellCatalog

            # Let user pick shells
            $selShells = Show-CheckboxList -Items $shellListWithBack -Prompt 'Select shells to configure: Up/Down move, Space toggle, Enter confirm'

            # Check if Back was selected or nothing was selected
            if ($selShells.id -contains "back") {
                Write-Host "Returning to main menu..." -ForegroundColor Cyan
                Pause
            }
            elseif ($selShells.Count -eq 0) {
                Write-Host 'No shells selected.' -ForegroundColor Red
                Pause
            }
            else {
                # Filter out the "back" option if it was selected along with other options
                $selShells = $selShells | Where-Object { $_.id -ne "back" }

                # If "All Shells" chosen, expand to every non-hidden (except the all stub)
                if ($selShells.id -contains 'all') {
                    $selShells = $shellCatalog | Where-Object { $_.id -ne 'all' }
                }

                # Dispatch based on the .function field
                foreach ($shell in $selShells) {
                    $fn = $shell.function
                    if ([string]::IsNullOrEmpty($fn)) {
                        Write-Host "Warning: No function specified for '$($shell.name)'. Skipping." -ForegroundColor Yellow
                        continue
                    }
                    # check that function/cmdlet exists
                    if (Get-Command $fn -ErrorAction SilentlyContinue) {
                        Write-Host "Running $fn for $($shell.name)" -ForegroundColor Cyan
                        & $fn
                    }
                    else {
                        Write-Host "Warning: Function '$fn' not found. Cannot configure $($shell.name)." -ForegroundColor Yellow
                    }
                }
            }
        }

        '4' {
            # Install winget & apps
            Install-Winget
            Install-Apps -AppsToInstall $appCatalog

            # Use already loaded shell data
            $shellsToRun = $shellAll | Where-Object { -not $_.hidden -and $_.id -ne 'all' }

            # Dispatch each by its .function field
            foreach ($shell in $shellsToRun) {
                $fn = $shell.function
                if ([string]::IsNullOrEmpty($fn)) {
                    Write-Host "Warning: No function defined for '$($shell.name)'. Skipping." -ForegroundColor Yellow
                    continue
                }

                if (Get-Command $fn -ErrorAction SilentlyContinue) {
                    Write-Host "Configuring $($shell.name) using $fn()" -ForegroundColor Cyan
                    & $fn
                }
                else {
                    Write-Host "Warning: Function '$fn' not found. Cannot configure $($shell.name)." -ForegroundColor Yellow
                }
            }
        }

        '0' {
            Write-Host "Goodbye!" -ForegroundColor Cyan
            $done = $true
        }

        Default {
            Write-Host 'Invalid choice. Try again!' -ForegroundColor Red
            Pause
        }
    }
} while (-not $done)
