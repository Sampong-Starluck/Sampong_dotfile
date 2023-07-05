# This script will install the following apps using winget:
# - Visual Studio Code
# - Chrome
# - Firefox
# - Notepad++

# Create a list of apps to install
$apps = @(
    "Microsoft.PowerShell"
    "Eugeny.Tabby"
    "Mozilla.Firefox.DeveloperEdition"
    "Microsoft.VisualStudioCode"
    "JetBrains.Toolbox"
    "Git.Git"
    "PremiumSoft.NavicatPremium"
)

# Check if winget is installed
if (Get-Command winget -ErrorAction SilentlyContinue) {
    # Install winget
    winget install winget
}

# Loop through the list of apps and install them
foreach ($app in $apps) {
    winget install -e --id $app
}

# function Set-EnvironmentVariable($variableName, $value) {
#     $env:variableName = $value
# }

# # Find path for git command and git to path
# $git = Get-Command git | Select-Object Path
# Set-EnvironmentVariable "Path" $git
# Start-Process $git

# install NVS for node JS environment
#& "$git" -c """export NVS_HOME="$HOME/.nvs"
#git clone https://github.com/jasongin/nvs "$NVS_HOME"
#. "$NVS_HOME/nvs.sh" install"""

# restart bash CLI
#& "$git" -c "source ~/.bashrc"

# install nodeJs using nvs command
#& "$git" -c "nvs add 18.16.0 && nvs link 18.16.0"

# # Get the value of the NVS_HOME environment variable.
# $NVS_HOME = "$env:USERPROFILE\.nvs"

# $nvsHome = Set-EnvironmentVariable "NVS_HOME" $NVS_HOME

# # Get the value of the PATH environment variable.
# $path = Get-EnvironmentVariable PATH

# # Add the path `%NVS_HOME%\default` to the PATH environment variable.
# $path += ";$nvsHome\default"

# Pause to let the user check the results
Write-Host "Press Enter to continue..."
$input = Read-Host


