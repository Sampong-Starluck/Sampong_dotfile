# This script will install the following apps using winget:
# - Visual Studio Code
# - Arc browser
# - Zen browser
# - Firefox aurora
# - Notepad++
# - PowerShell
# - Tabby terminal
# - OBSStudio
# - JetBrains Toolbox
# - Nushell
# - Telegram/Unigram
# - Version-fox(vfox)
# - Nilesoft

# Create a list of apps to install
$apps = @(
    "Microsoft.PowerShell",
    "Eugeny.Tabby",
    "Mozilla.Firefox.DeveloperEdition",
    "Microsoft.VisualStudioCode",
    "JetBrains.Toolbox",
    "Notepad++.Notepad++",
    "Nilesoft.Shell",
    "version-fox.vfox",
    "OBSProject.OBSStudio",
    "TheBrowserCompany.Arc",
    "Telegram.TelegramDesktop",
    "Telegram.Unigram",
    "Zen-Team.Zen-Browser",
    "Nushell.Nushell"
)

# Check if winget is installed
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget is not installed. Attempting to install..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://aka.ms/getwinget" -OutFile "$HOME\Downloads\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    Add-AppxPackage -Path "$HOME\Downloads\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Error "winget installation failed. Please install winget manually and try again."
        exit
    }
    Write-Host "winget successfully installed." -ForegroundColor Green
}

# Loop through the list of apps and install them
foreach ($app in $apps) {
    try {
        Write-Host "Attempting to install: $app" -ForegroundColor Cyan
        winget install -e --id $app --accept-source-agreements --accept-package-agreements
    } catch {
        Write-Error "Failed to install: $app. Error: $_"
    }
}

########################################################################
#                        Shell configuration script                    #
#**********************************************************************#
#                      Commend this part if not needed                 #
########################################################################

# Add oh-my-posh initialization command to NuShell environment
$nuEnvPath = "$Home\AppData\Roaming\nushell\env.nu"
$nuConfigPath = "$Home\AppData\Roaming\nushell\config.nu"
$ohMyPoshCommand = 'let-env PROMPT_COMMAND = (oh-my-posh init nu --config "$HOME/AppData/Local/Programs/oh-my-posh/themes/spaceship.omp.json")'

if (Test-Path -Path $nuEnvPath) {
    Add-Content -Path $nuEnvPath -Value "`n$ohMyPoshCommand"
    Write-Host "oh-my-posh initialization command added to NuShell env.nu" -ForegroundColor Green
} else {
    Write-Error "NuShell environment file not found at $nuEnvPath. Please ensure NuShell is installed and the path is correct or update accordingly."
}

# Add additional commands to NuShell config
$nuAdditionalCommands = @(
    'source ~/.oh-my-posh.nu',
    '$env.EDITOR = "nvim"',
    'use ~/Documents/Sampong_dotfile/nu/main_profile.nu',
    'use main_profile *'
)

if (Test-Path -Path $nuConfigPath) {
    Add-Content -Path $nuConfigPath -Value ($nuAdditionalCommands -join "`n")
    Write-Host "Update configuration file for Nu Shell in config.nu" -ForegroundColor Green
} else {
    Write-Error "NuShell configuration file not found at $nuConfigPath. Please ensure NuShell is installed and the path is correct or update accordingly."
}

# Create PowerShell profile file if it doesn't exist
if (-not (Test-Path $PROFILE.CurrentUserAllHosts)) {
    New-Item $PROFILE.CurrentUserAllHosts -ItemType File -Force
}

# Add oh-my-posh import command to PowerShell profile
$poshProfileCommand = 'Import-Module (Resolve-Path "$HOME\PowerShell\posh_profile.ps1")'
Add-Content -Path $PROFILE.CurrentUserAllHosts -Value "`n$poshProfileCommand"

# Create ~/.bashrc file and add commands
$bashrcPath = "$HOME/.bashrc"
$bashrcCommands = @(
    'export DIR="<path>/bash"',
    'if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi',
    '. "$DIR/main.sh"'
)
if (-not (Test-Path $bashrcPath)) {
    New-Item -Path $bashrcPath -ItemType File -Force
}
Add-Content -Path $bashrcPath -Value ($bashrcCommands -join "`n")

########################################################################
#                    End Shell configuration script                    #
########################################################################

# Pause to let the user check the results
Write-Host "Press Enter to continue..."
$input = Read-Host
