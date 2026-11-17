$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RacineProjet = Split-Path -Parent $PSScriptRoot
Push-Location $RacineProjet
try {
    $Etapes = @(
        "construire_fichier_decrochage.py",
        "valider_coherence_indicateurs.py",
        "transformer_indicateurs.py",
        "evaluer_prevision.py",
        "interpreter_priorites.py",
        "generer_fiche_decideur.py"
    )
    foreach ($Etape in $Etapes) {
        Write-Host "Execution : $Etape"
        & python (Join-Path $PSScriptRoot $Etape)
        if ($LASTEXITCODE -ne 0) {
            throw "Echec de l'etape $Etape"
        }
    }

    & python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "Echec des tests finaux"
    }
    Write-Host "Pipeline SCO-RISK termine et verifie."
}
finally {
    Pop-Location
}
