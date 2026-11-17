from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BLEU = colors.HexColor("#073B5C")
BLEU_CLAIR = colors.HexColor("#E8F4F8")
CYAN = colors.HexColor("#0E7490")
ORANGE = colors.HexColor("#D97706")
ROUGE = colors.HexColor("#B91C1C")
VERT = colors.HexColor("#15803D")
GRIS = colors.HexColor("#475569")
GRIS_CLAIR = colors.HexColor("#F1F5F9")
BLANC = colors.white


def enregistrer_polices() -> tuple[str, str]:
    normal = Path(r"C:\Windows\Fonts\arial.ttf")
    gras = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if normal.exists() and gras.exists():
        pdfmetrics.registerFont(TTFont("Arial", normal))
        pdfmetrics.registerFont(TTFont("Arial-Bold", gras))
        return "Arial", "Arial-Bold"
    return "Helvetica", "Helvetica-Bold"


def p(texte: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(texte, style)


def carte_kpi(valeur: str, libelle: str, couleur: colors.Color, styles: dict) -> Table:
    contenu = [
        [p(valeur, styles["kpi_valeur"])],
        [p(libelle, styles["kpi_libelle"])],
    ]
    table = Table(contenu, colWidths=[40 * mm], rowHeights=[10 * mm, 9 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), couleur),
                ("BOX", (0, 0), (-1, -1), 0.5, couleur),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def generer(priorites_path: Path, regions_path: Path, sortie: Path) -> None:
    priorites = pd.read_csv(priorites_path)
    regions = pd.read_csv(regions_path)
    police, police_gras = enregistrer_polices()
    styles_base = getSampleStyleSheet()
    styles = {
        "titre": ParagraphStyle(
            "titre", parent=styles_base["Title"], fontName=police_gras,
            fontSize=20, leading=22, textColor=BLANC, alignment=TA_LEFT,
        ),
        "sous_titre": ParagraphStyle(
            "sous_titre", parent=styles_base["Normal"], fontName=police,
            fontSize=9.2, leading=12, textColor=colors.HexColor("#DFF6FF"),
        ),
        "section": ParagraphStyle(
            "section", parent=styles_base["Heading2"], fontName=police_gras,
            fontSize=11.5, leading=14, textColor=BLEU, spaceAfter=4,
        ),
        "normal": ParagraphStyle(
            "normal", parent=styles_base["Normal"], fontName=police,
            fontSize=7.7, leading=10, textColor=colors.HexColor("#1E293B"),
        ),
        "petit": ParagraphStyle(
            "petit", parent=styles_base["Normal"], fontName=police,
            fontSize=6.7, leading=8.2, textColor=GRIS,
        ),
        "table_entete": ParagraphStyle(
            "table_entete", parent=styles_base["Normal"], fontName=police_gras,
            fontSize=6.8, leading=8, textColor=BLANC, alignment=TA_CENTER,
        ),
        "table_cellule": ParagraphStyle(
            "table_cellule", parent=styles_base["Normal"], fontName=police,
            fontSize=6.6, leading=8, textColor=colors.HexColor("#1E293B"),
        ),
        "kpi_valeur": ParagraphStyle(
            "kpi_valeur", parent=styles_base["Normal"], fontName=police_gras,
            fontSize=16, leading=17, textColor=BLANC, alignment=TA_CENTER,
        ),
        "kpi_libelle": ParagraphStyle(
            "kpi_libelle", parent=styles_base["Normal"], fontName=police,
            fontSize=6.8, leading=8, textColor=BLANC, alignment=TA_CENTER,
        ),
        "encadre": ParagraphStyle(
            "encadre", parent=styles_base["Normal"], fontName=police,
            fontSize=7.2, leading=9.3, textColor=colors.HexColor("#1E293B"),
        ),
    }

    doc = SimpleDocTemplate(
        str(sortie), pagesize=A4,
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=10 * mm, bottomMargin=9 * mm,
        title="SCO-RISK Burkina - Fiche d'aide à la décision 2024-2025",
        author="Equipe Data Challenge Burkina - Défi 1",
    )
    largeur = A4[0] - 24 * mm
    elements = []

    entete = Table(
        [[p("SCO-RISK Burkina", styles["titre"])],
         [p("Fiche d'aide à la décision - Risque de décrochage au primaire - Année observée 2024-2025", styles["sous_titre"])]],
        colWidths=[largeur], rowHeights=[11 * mm, 8 * mm],
    )
    entete.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLEU),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.extend([entete, Spacer(1, 4 * mm)])

    compte = priorites["priorite_decision"].value_counts()
    kpis = Table(
        [[
            carte_kpi("45", "provinces observées", BLEU, styles),
            carte_kpi(str(int(compte.get("Priorité immédiate", 0))), "priorités immédiates", ROUGE, styles),
            carte_kpi(str(int(compte.get("Surveillance renforcée", 0))), "surveillances renforcées", ORANGE, styles),
            carte_kpi("8", "années scolaires analysées", CYAN, styles),
        ]],
        colWidths=[largeur / 4] * 4,
    )
    kpis.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.extend([kpis, Spacer(1, 4 * mm)])

    top = priorites.head(8)
    lignes_top = [[
        p("Rang", styles["table_entete"]), p("Province", styles["table_entete"]),
        p("Région historique", styles["table_entete"]), p("Score", styles["table_entete"]),
        p("Tendance", styles["table_entete"]), p("Contribution dominante", styles["table_entete"]),
    ]]
    for _, ligne in top.iterrows():
        lignes_top.append([
            p(str(int(ligne["rang_national"])), styles["table_cellule"]),
            p(str(ligne["province"]), styles["table_cellule"]),
            p(str(ligne["region_historique"]), styles["table_cellule"]),
            p(f"{float(ligne['score_risque']):.1f}", styles["table_cellule"]),
            p(f"{ligne['tendance_recente']}<br/><font size='6'>({float(ligne['tendance_score_3_ans']):+.1f} pt/an)</font>", styles["table_cellule"]),
            p(str(ligne["facteur_dominant"]), styles["table_cellule"]),
        ])
    table_top = Table(
        lignes_top,
        colWidths=[12 * mm, 28 * mm, 34 * mm, 15 * mm, 35 * mm, 48 * mm],
        repeatRows=1,
    )
    style_top = [
        ("BACKGROUND", (0, 0), (-1, 0), BLEU),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for index in range(1, len(lignes_top)):
        if index % 2 == 0:
            style_top.append(("BACKGROUND", (0, index), (-1, index), GRIS_CLAIR))
    table_top.setStyle(TableStyle(style_top))

    elements.extend([
        p("Où agir en priorité ?", styles["section"]),
        p("Classement relatif des huit premières provinces selon l'indice observé 2024-2025.", styles["petit"]),
        Spacer(1, 2 * mm),
        table_top,
        Spacer(1, 4 * mm),
    ])

    actions_data = [
        [p("Contribution", styles["table_entete"]), p("Action proposée", styles["table_entete"])],
        [p("Abandon provincial", styles["table_cellule"]), p("Suivi précoce des absences, recherche des élèves sortis et accompagnement du retour à l'école.", styles["table_cellule"])],
        [p("Redoublement provincial", styles["table_cellule"]), p("Soutien pédagogique ciblé, rattrapage et suivi des classes les plus concernées.", styles["table_cellule"])],
        [p("Non-achèvement régional", styles["table_cellule"]), p("Plan régional de maintien jusqu'au CM2 et examen des obstacles à la continuité du parcours.", styles["table_cellule"])],
    ]
    actions = Table(actions_data, colWidths=[35 * mm, 47 * mm])
    actions.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLEU),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    gauche = [
        p("Lecture régionale", styles["section"]),
        p(
            f"Les 45 provinces sont regroupées dans <b>{regions['region_historique'].nunique()} régions historiques</b>. "
            "La carte interactive permet de sélectionner une région, d'afficher ses provinces et de suivre leur évolution de 2017-2018 à 2024-2025.",
            styles["normal"],
        ),
        Spacer(1, 3 * mm),
        p("Comment décider ?", styles["section"]),
        actions,
    ]

    droite = [
        p("Comment lire l'alerte ?", styles["section"]),
        p(
            "<b>Priorité immédiate :</b> score critique, ou score élevé accompagné d'une hausse récente.<br/>"
            "<b>Surveillance renforcée :</b> score élevé stable, ou score modéré en forte hausse.<br/>"
            "<b>Veille :</b> risque plus faible dans le classement relatif, à continuer de suivre.",
            styles["encadre"],
        ),
        Spacer(1, 3 * mm),
        p("Anticipation 2025-2027", styles["section"]),
        p(
            "Le modèle Ridge réduit l'erreur absolue moyenne à <b>9,55 points</b>, contre "
            "<b>13,97</b> pour la référence naïve. Il retrouve 6 provinces sur 10 du groupe "
            "prioritaire lors du test 2024-2025. À deux ans, la MAE est de <b>10,13 points</b> "
            "contre <b>12,72</b> pour la référence naïve. Les deux projections servent à déclencher une revue humaine, pas à décider automatiquement.",
            styles["encadre"],
        ),
        Spacer(1, 3 * mm),
        p("Limites à garder visibles", styles["section"]),
        p(
            "- Indice relatif aux 45 provinces historiques.<br/>"
            "- Abandon et redoublement : moyennes non pondérées des niveaux.<br/>"
            "- Achèvement disponible au niveau régional.<br/>"
            "- Contribution dominante ≠ cause démontrée.<br/>"
            "- Les 47 provinces de 2025 ne sont pas reconstruites artificiellement.",
            styles["encadre"],
        ),
    ]

    corps = Table(
        [[gauche, droite]],
        colWidths=[largeur * 0.58, largeur * 0.42],
    )
    corps.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("LINEBEFORE", (1, 0), (1, 0), 0.6, colors.HexColor("#CBD5E1")),
    ]))
    elements.extend([corps, Spacer(1, 4 * mm)])

    pied = Table(
        [[p(
            "Sources : DGESS - statistiques du préscolaire et du primaire 2016-2025 ; annuaires statistiques du primaire CNS 2017-2018 à 2024-2025 ; cartographie administrative publique. "
            "Unité : province-année scolaire. Outil : SCO-RISK Burkina.",
            styles["petit"],
        )]],
        colWidths=[largeur],
    )
    pied.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLEU_CLAIR),
        ("BOX", (0, 0), (-1, -1), 0.5, CYAN),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(pied)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    doc.build(elements)


def arguments() -> argparse.Namespace:
    parseur = argparse.ArgumentParser(description="Génère la fiche décideur SCO-RISK.")
    parseur.add_argument("--priorites", default="05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_priorites-2024-2025_v1.csv")
    parseur.add_argument("--regions", default="05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_synthese-regions-2024-2025_v1.csv")
    parseur.add_argument("--sortie", default="05_interpretation/SCO-RISKBurkina_05-interpretation_D1_analyst_fiche-decideur-2024-2025_v1.pdf")
    return parseur.parse_args()


def main() -> int:
    args = arguments()
    racine = Path(__file__).resolve().parents[1]

    def chemin(valeur: str) -> Path:
        pth = Path(valeur)
        return pth if pth.is_absolute() else racine / pth

    generer(chemin(args.priorites), chemin(args.regions), chemin(args.sortie))
    print("Fiche décideur générée sur une page.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
