from __future__ import annotations

import os
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEFAULT_WORKBOOK = Path(r"C:\Users\olivi\Dropbox\le programme2026.xlsm")
WORKBOOK = Path(os.environ.get("TELEMETRY_XLSM", DEFAULT_WORKBOOK))
SHEET_NAME = "Situation 2021 - 2026"
BEGIN = "<!-- TELEMETRY:BEGIN -->"
END = "<!-- TELEMETRY:END -->"


# Corrige les libellés venant d'Excel pour garder un README propre et homogène.
LABELS = {
    "Phisuqe et Electronic": "Physique et électronique",
    "Database - SQL ": "Database - SQL",
    "Code Review + test + tps IA": "Code review + tests + temps IA",
    "DevOps (Github Action, CI/CD)": "DevOps, GitHub Actions, CI/CD",
    "Généralités + Livres techniques": "Généralités + livres techniques",
    "Intelligence Artificielle": "Intelligence artificielle",
    "Math et Algorithmique": "Math et algorithmique",
    "Magazine + Encyclopédie": "Magazine + encyclopédie",
    "FireBase": "Firebase",
    "React Js": "React JS",
    "Typescript": "TypeScript",
    "Wordpress": "WordPress",
    "Excel Access MS Office": "Excel, Access, MS Office",
    "Regex (expressions régulières)": "Regex",
    "GitHub + Gitlab + VS Code + Vim": "GitHub + GitLab + VS Code + Vim",
}

# Ces lignes existent dans Excel, mais ce sont des indicateurs globaux, pas des technologies.
EXCLUDED_LABELS = {
    "On doit arriver à",
    "Total",
    "fin 2024",
    "fin 2025",
    "il reste donc",
}


def fmt_hours(value: float) -> str:
    """Affiche 906 au lieu de 906.0, mais conserve les demi-heures comme 905.5."""
    return str(int(value)) if float(value).is_integer() else str(value).rstrip("0").rstrip(".")


def bar(value: float, base: float, width: int = 16) -> str:
    """Crée une barre proportionnelle, avec Laravel comme base 100 %."""
    filled = round((value / base) * width) if base else 0
    if value > 0 and filled == 0:
        return "▏"
    if filled < 1:
        return ""
    if filled == 1:
        return "▌"
    return "█" * min(filled, width)


def clean_label(label: object) -> str:
    """Normalise les noms et fusionne les lignes découpées en '1ère partie', '2ème partie', etc."""
    text = str(label).strip()
    lowered = text.lower()
    if lowered.startswith("laravel ") and "partie" in lowered:
        return "Laravel"
    if lowered.startswith("vue js ") and "partie" in lowered:
        return "Vue JS"
    if lowered.startswith("javascript ") and "partie" in lowered:
        return "JavaScript"
    if lowered.startswith("node & express js ") and "partie" in lowered:
        return "Node & Express JS"
    return LABELS.get(text, text)


def read_workbook() -> tuple[list[tuple[str, float]], dict[str, float]]:
    """Lit la feuille Excel, agrège les heures par technologie et récupère les totaux."""
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True, keep_vba=True)
    ws = wb[SHEET_NAME]
    totals: dict[str, float] = {}
    summary: dict[str, float] = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        label = row[1] if len(row) > 1 else None
        hours = row[2] if len(row) > 2 else None
        if not label or not isinstance(hours, (int, float)):
            continue
        raw_label = str(label).strip()
        label = clean_label(raw_label)
        if raw_label in EXCLUDED_LABELS or label in EXCLUDED_LABELS:
            summary[raw_label] = float(hours)
            continue
        totals[label] = totals.get(label, 0.0) + float(hours)

    return sorted(totals.items(), key=lambda item: item[1], reverse=True), summary


def group_name(index: int) -> str:
    """Répartit les technologies dans des blocs de lecture pour garder l'effet console."""
    if index < 10:
        return "[SOCLE PRINCIPAL]"
    if index < 24:
        return "[INTERFACE, PRODUIT & RECHERCHE]"
    return "[EXPLORATIONS & FONDATIONS]"


def build_block(items: list[tuple[str, float]], summary: dict[str, float]) -> str:
    """Construit le bloc Markdown qui sera injecté dans README.md."""
    if not items:
        raise RuntimeError("Aucune technologie lisible dans le fichier Excel.")

    base = items[0][1]
    total = summary.get("Total", sum(hours for _, hours in items))
    target = summary.get("On doit arriver à", 5000)
    max_label = min(max(len(label) for label, _ in items), 33)
    lines = [
        BEGIN,
        "<!-- Généré depuis le programme2026.xlsm avec scripts/update-telemetry-from-excel.py. -->",
        '<p align="center">',
        f'  <img src="https://img.shields.io/badge/BASE-Laravel%20{fmt_hours(base)}h-B79C6A?style=for-the-badge&labelColor=0B0D10" alt="Base Laravel {fmt_hours(base)} h">',
        f'  <img src="https://img.shields.io/badge/Suivi-{fmt_hours(total)}h-D6C3A3?style=for-the-badge&labelColor=11151B" alt="{fmt_hours(total)} heures suivies">',
        f'  <img src="https://img.shields.io/badge/Objectif-{fmt_hours(target)}h-8C7355?style=for-the-badge&labelColor=0B0D10" alt="Objectif {fmt_hours(target)} heures">',
        "</p>",
        "",
        "```txt",
    ]

    current_group = ""
    for index, (label, hours) in enumerate(items):
        group = group_name(index)
        if group != current_group:
            if current_group:
                lines.append("")
            lines.append(group)
            current_group = group

        display = label if len(label) <= max_label else label[: max_label - 1] + "…"
        ratio = round((hours / base) * 100) if base else 0
        lines.append(
            f"{display:<{max_label}} {bar(hours, base):<16} {fmt_hours(hours):>7}h {ratio:>5}%"
        )

    lines.extend(
        [
            "",
            "[SYSTÈMES TERRAIN]",
            "LIBATELI                         ● PRODUCTION",
            "WADORIA                          ● DEPLOYMENT",
            "EKOKELO                          ● R&D",
            "O:DS                             ● ECOSYSTEM",
            "```",
            END,
        ]
    )
    return "\n".join(lines)


def update_readme(block: str) -> None:
    """Remplace uniquement la zone balisée du README, sans toucher aux autres sections."""
    content = README.read_text(encoding="utf-8")
    if BEGIN not in content or END not in content:
        raise RuntimeError(f"Marqueurs {BEGIN} / {END} introuvables dans README.md.")
    start = content.index(BEGIN)
    end = content.index(END) + len(END)
    README.write_text(content[:start] + block + content[end:], encoding="utf-8", newline="\n")


if __name__ == "__main__":
    items, summary = read_workbook()
    update_readme(build_block(items, summary))
    print(f"README telemetry updated from: {WORKBOOK}")
