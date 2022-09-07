# oh-my-posh init pwsh | Invoke-Expression

# Add Icon Terminal
Import-Module Terminal-Icons

#Add themes to CLI
oh-my-posh init pwsh --config "C:\Users\Sampong Lim\AppData\Local\Programs\oh-my-posh\themes\spaceship.omp.json" | Invoke-Expression

# Configure the fuck command
$env:PYTHONIOENCODING="utf-8"
iex "$(thefuck --alias)"


# Add Volta
# if (Test-Path "C:\Users\Sampong Lim\.jabba\jabba.ps1") { . "C:\Users\Sampong Lim\.jabba\jabba.ps1" }

