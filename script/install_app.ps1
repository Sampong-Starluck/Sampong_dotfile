# Define apps to install
$apps = @(
    "JetBrains.Toolbox",
    "Mozilla.Firefox.DeveloperEdition",
    "version-fox.vfox",
    "Zen-Team.Zen-Browser",
    "Microsoft.VisualStudioCode",
    "Notepad++.Notepad++",
    "Nilesoft.Shell",
    "OBSProject.OBSStudio",
    "TheBrowserCompany.Arc",
    "Telegram.TelegramDesktop",
    "Eugeny.Tabby",
    "Nushell.Nushell",
    "Google.Chrome",
    "JanDeDobbeleer.OhMyPosh" # Added Oh My Posh installation
)

# Check and install winget if needed
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "Installing winget..." -ForegroundColor Yellow

    # More reliable installation method
    $progressPreference = 'silentlyContinue'
    $latestWingetMsixBundleUri = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    $appInstallerPath = "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"

    Invoke-WebRequest -Uri $latestWingetMsixBundleUri -OutFile $appInstallerPath
    Add-AppxPackage -Path $appInstallerPath

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "winget successfully installed." -ForegroundColor Green
    } else {
        Write-Host "winget installation failed. Please install manually." -ForegroundColor Red
        exit 1
    }
}

# Install apps
Write-Host "Installing applications..." -ForegroundColor Cyan
foreach ($app in $apps) {
    Write-Host "Installing $app..." -ForegroundColor Cyan
    winget install -e --id $app --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install $app. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}

########################################################################
#                        Shell configuration script                    #
#**********************************************************************#
#                      Commend this part if not needed                 #
########################################################################

# Create dotfiles directory if it doesn't exist
$dotfilesDir = "$HOME\Documents\Sampong_dotfile"
if (-not (Test-Path $dotfilesDir)) {
    Write-Host "Creating dotfiles directory at $dotfilesDir" -ForegroundColor Yellow
    New-Item -Path $dotfilesDir -ItemType Directory -Force

    # Create subdirectories for different shell configs
    New-Item -Path "$dotfilesDir\nu" -ItemType Directory -Force
    New-Item -Path "$dotfilesDir\PowerShell" -ItemType Directory -Force
    New-Item -Path "$dotfilesDir\bash" -ItemType Directory -Force

    # Create placeholder files with basic content
    Set-Content -Path "$dotfilesDir\nu\main_profile.nu" -Value '# Your NuShell customizations go here'
    Set-Content -Path "$dotfilesDir\PowerShell\posh_profile.ps1" -Value '# Your PowerShell customizations go here'
    Set-Content -Path "$dotfilesDir\bash\main.sh" -Value '# Your Bash customizations go here'
}

# Configure NuShell
$nuConfigDir = "$HOME\AppData\Roaming\nushell"
$nuEnvPath = "$nuConfigDir\env.nu"
$nuConfigPath = "$nuConfigDir\config.nu"

# Create NuShell config directory if it doesn't exist
if (-not (Test-Path $nuConfigDir)) {
    New-Item -Path $nuConfigDir -ItemType Directory -Force
}

# Create or update env.nu
if (-not (Test-Path $nuEnvPath)) {
    New-Item -Path $nuEnvPath -ItemType File -Force
}

# Find the correct Oh My Posh theme path
# Check common installation locations
$potentialThemePaths = @(
    "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\spaceship.omp.json",
    "$env:PROGRAMFILES\oh-my-posh\themes\spaceship.omp.json",
    "$HOME\AppData\Local\Programs\oh-my-posh\themes\spaceship.omp.json"
)

$themeFound = $false
$themePath = ""

foreach ($path in $potentialThemePaths) {
    if (Test-Path $path) {
        $themePath = $path
        $themeFound = $true
        Write-Host "Found Oh My Posh theme at: $themePath" -ForegroundColor Green
        break
    }
}

# If theme not found, try to locate Oh My Posh installation and find themes directory
if (-not $themeFound) {
    $ohMyPoshExe = Get-Command -Name "oh-my-posh" -ErrorAction SilentlyContinue
    if ($ohMyPoshExe) {
        $ohMyPoshDir = Split-Path -Parent $ohMyPoshExe.Source
        $potentialThemeDir = Join-Path -Path $ohMyPoshDir -ChildPath "themes"

        if (Test-Path $potentialThemeDir) {
            $themePath = Join-Path -Path $potentialThemeDir -ChildPath "spaceship.omp.json"
            $themeFound = Test-Path $themePath

            if ($themeFound) {
                Write-Host "Found Oh My Posh theme at: $themePath" -ForegroundColor Green
            }
        }
    }
}

# Use fallback theme if preferred theme not found
if (-not $themeFound) {
    foreach ($path in $potentialThemePaths) {
        $themeDir = Split-Path -Parent $path
        if (Test-Path $themeDir) {
            # Get the first theme file we can find
            $anyTheme = Get-ChildItem -Path $themeDir -Filter "*.omp.json" | Select-Object -First 1
            if ($anyTheme) {
                $themePath = $anyTheme.FullName
                $themeFound = $true
                Write-Host "Preferred theme not found. Using alternative theme: $themePath" -ForegroundColor Yellow
                break
            }
        }
    }
}

# Check if Oh My Posh initialization is already in env.nu before adding it
if ($themeFound) {
    # Convert Windows path to format compatible with NuShell
    $nuShellPath = $themePath -replace '\\', '\\'

    $ohMyPoshCommand = "let-env PROMPT_COMMAND = { oh-my-posh init nu --config `"$nuShellPath`" }"

    if (-not (Select-String -Path $nuEnvPath -Pattern "oh-my-posh init nu" -Quiet)) {
        Add-Content -Path $nuEnvPath -Value "`n$ohMyPoshCommand"
        Write-Host "Added Oh My Posh to NuShell env.nu" -ForegroundColor Green
    }
} else {
    Write-Host "Oh My Posh theme not found. NuShell will use default prompt." -ForegroundColor Yellow
    $ohMyPoshCommand = "# Oh My Posh theme not found. Using default prompt."
    Add-Content -Path $nuEnvPath -Value "`n$ohMyPoshCommand"
}

# Create or update config.nu
if (-not (Test-Path $nuConfigPath)) {
    New-Item -Path $nuConfigPath -ItemType File -Force
}

# Add NuShell customizations if not already present
$nuCustomizations = @(
    '$env.EDITOR = "nvim"',
    'use ~/Documents/Sampong_dotfile/nu/main_profile.nu'
)

foreach ($line in $nuCustomizations) {
    if (-not (Select-String -Path $nuConfigPath -Pattern ([regex]::Escape($line)) -Quiet)) {
        Add-Content -Path $nuConfigPath -Value $line
    }
}
Write-Host "NuShell configuration updated" -ForegroundColor Green

# Configure PowerShell
if (-not (Test-Path $PROFILE.CurrentUserAllHosts)) {
    New-Item -Path $PROFILE.CurrentUserAllHosts -ItemType File -Force
}

$poshProfileImport = 'Import-Module (Resolve-Path "~\Documents\Sampong_dotfile\PowerShell\posh_profile.ps1")'
if (-not (Select-String -Path $PROFILE.CurrentUserAllHosts -Pattern ([regex]::Escape($poshProfileImport)) -Quiet)) {
    Add-Content -Path $PROFILE.CurrentUserAllHosts -Value "`n$poshProfileImport"
    Write-Host "PowerShell profile updated" -ForegroundColor Green
}

# Configure Bash
$bashrcPath = "$HOME\.bashrc"
$bashContent = @(
    'export DIR="$HOME/Documents/Sampong_dotfile/bash"',
    'if [[ ! -d "$DIR" ]]; then mkdir -p "$DIR"; fi',
    'source "$DIR/main.sh"'
)

if (-not (Test-Path $bashrcPath)) {
    New-Item -Path $bashrcPath -ItemType File -Force
}

# Check if bash config is already present
$bashContentString = $bashContent -join "`n"
if (-not (Select-String -Path $bashrcPath -Pattern "Sampong_dotfile/bash" -Quiet)) {
    Add-Content -Path $bashrcPath -Value "`n$bashContentString"
    Write-Host "Bash profile updated" -ForegroundColor Green
}

########################################################################
#                    End Shell configuration script                    #
########################################################################

Write-Host "Setup complete! Your development environment has been configured." -ForegroundColor Green
Write-Host "Press Enter to exit..."
Read-Host
