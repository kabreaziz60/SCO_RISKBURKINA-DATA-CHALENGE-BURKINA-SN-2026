param(
    [string]$Classeur = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RacineProjet = Split-Path -Parent $PSScriptRoot
$PythonVenv = Join-Path $RacineProjet ".venv\Scripts\python.exe"
$Python = if (Test-Path -LiteralPath $PythonVenv) { $PythonVenv } else { "python" }

Push-Location $RacineProjet
try {
    & $Python -c "import openpyxl; print('openpyxl', openpyxl.__version__)"
    if ($LASTEXITCODE -ne 0) {
        throw "La bibliotheque openpyxl est absente. Executez : python -m pip install -r requirements.txt"
    }

    $ArgumentsClasseur = @()
    if ($Classeur) {
        $ArgumentsClasseur = @("--classeur", $Classeur)
    }

    & $Python "$PSScriptRoot\inventaire_classeur.py" @ArgumentsClasseur
    if ($LASTEXITCODE -ne 0) { throw "Echec de l'inventaire." }

    & $Python "$PSScriptRoot\controle_qualite.py" @ArgumentsClasseur
    if ($LASTEXITCODE -ne 0) { throw "Echec des controles de qualite." }

    $FichierInventaire = Join-Path $RacineProjet "rapports_prives\01_inventaire_classeur.json"
    $Empreinte = (Get-Content -Raw -LiteralPath $FichierInventaire | ConvertFrom-Json).fichier.sha256
    "$Empreinte  classeur_source" | Set-Content -Encoding utf8 -LiteralPath (Join-Path $RacineProjet "rapports_prives\empreintes.sha256.txt")

    Write-Host ""
    Write-Host "Termine. Ouvrez le dossier rapports_prives dans VS Code."
    Write-Host "Le classeur original n'a pas ete modifie."
}
finally {
    Pop-Location
}

