$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RacineProjet = Split-Path -Parent $PSScriptRoot
Push-Location $RacineProjet
try {
    $Etapes = @(
        "valider_coherence_indicateurs.py",
        "transformer_indicateurs.py",
        "evaluer_prevision.py",
        "interpreter_priorites.py",
        "generer_fiche_decideur.py"
    )

    $ClasseurSource = @(
        Get-ChildItem -LiteralPath $RacineProjet -File |
            Where-Object { $_.Extension -in ".xlsx", ".xls", ".xlsm" }
    )
    $TableNettoyee = Join-Path $RacineProjet "02_nettoyage\SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv"

    if ($ClasseurSource.Count -eq 1) {
        Write-Host "Execution : construire_fichier_decrochage.py"
        & python (Join-Path $PSScriptRoot "construire_fichier_decrochage.py")
        if ($LASTEXITCODE -ne 0) {
            throw "Echec de l'etape construire_fichier_decrochage.py"
        }
    }
    elseif (Test-Path -LiteralPath $TableNettoyee) {
        Write-Host "Source brute absente du depot public : utilisation de la table nettoyee publiee."
    }
    else {
        throw "Aucun classeur source ni table nettoyee publiee n'est disponible."
    }

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
