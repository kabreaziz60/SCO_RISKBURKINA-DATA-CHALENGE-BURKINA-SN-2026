$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RacineProjet = Split-Path -Parent $PSScriptRoot
Push-Location $RacineProjet
try {
    python -c "import streamlit, plotly, pandas; print('Environnement application : OK')"
    if ($LASTEXITCODE -ne 0) {
        throw "Une dépendance de l'application est absente."
    }
    python -m streamlit run ".\application\app.py"
}
finally {
    Pop-Location
}

