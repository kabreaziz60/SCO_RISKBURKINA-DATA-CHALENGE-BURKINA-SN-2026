$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RacineProjet = Split-Path -Parent $PSScriptRoot
Push-Location $RacineProjet
try {
    $Etapes = @(
        "valider_coherence_indicateurs.py",
        "transformer_indicateurs.py",
        "evaluer_prevision.py",
        "integrer_contexte_esu.py",
        "interpreter_priorites.py",
        "generer_fiche_decideur.py"
    )

    $ClasseurSource = @(
        Get-ChildItem -LiteralPath (Join-Path $RacineProjet "01_collecte") -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in ".xlsx", ".xlsm" }
    )
    $TableNettoyee = Join-Path $RacineProjet "02_nettoyage\SCO-RISKBurkina_02-nettoyage_D1_engineer_donnees-decrochage-province-annee_v1.csv"
    $DossierAnnuaires = Join-Path $RacineProjet "01_collecte\data_pack_selection\data\01_Education_MENAPLN_DGESS\CNS_DGESS\Annuaires"

    if ($ClasseurSource.Count -eq 1 -and (Test-Path -LiteralPath $DossierAnnuaires)) {
        Write-Host "Execution : construire_fichier_decrochage.py"
        & python (Join-Path $PSScriptRoot "construire_fichier_decrochage.py") --classeur $ClasseurSource[0].FullName
        if ($LASTEXITCODE -ne 0) {
            throw "Echec de l'etape construire_fichier_decrochage.py"
        }
    }
    elseif (Test-Path -LiteralPath $TableNettoyee) {
        Write-Host "Source Excel conservee dans 01_collecte. Annuaires du Data Pack non dupliques : utilisation de la table nettoyee publiee."
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
