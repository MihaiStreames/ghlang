import json
from pathlib import Path

from loguru import logger
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import requests
import yaml


LINGUIST_LANGUAGES_URL = (
    "https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml"
)

CLOC_TO_LINGUIST: dict[str, str | None] = {
    "ADSO/IDSM": None,
    "AMPLE": "AMPL",
    "ANTLR Grammar": "ANTLR",
    "AnsProlog": "Answer Set Programming",
    "Ant": "Ant Build System",
    "Apex Class": "Apex",
    "Apex Trigger": "Apex",
    "ArkTs": "ArkTS",
    "Arturo": None,
    "ASP": "Classic ASP",
    "awk": "Awk",
    "Bazel": "Starlark",
    "BizTalk Orchestration": "XML",
    "BizTalk Pipeline": "XML",
    "Bourne Again Shell": "Shell",
    "Bourne Shell": "Shell",
    "BrightScript": "Brightscript",
    "builder": "Ruby",
    "C Shell": "Tcsh",
    "C# Designer": "C#",
    "C/C++ Header": "C++",
    "Cake Build Script": "C#",
    "CCS": None,
    "Civet": "JavaScript",
    "ClojureC": "Clojure",
    "ClojureScript": "Clojure",
    "CoCoA 5": None,
    "Containerfile": "Dockerfile",
    "Constraint Grammar": "Text",
    "Coq": "Rocq Prover",
    "CUDA": "Cuda",
    "Cucumber": "Gherkin",
    "DAL": "AL",
    "Delphi Form": "Pascal",
    "Derw": None,
    "dhall": "Dhall",
    "diff": "Diff",
    "DITA": "XML",
    "DIET": None,
    "DNS Zone": "DNS Zone",
    "DOS Batch": "Batchfile",
    "DOORS Extension Language": "Text",
    "Drools": "Java",
    "dtrace": "DTrace",
    "DTD": "XML",
    "ECPP": "C++",
    "EEx": "HTML+EEX",
    "Elixir Script": "Elixir",
    "Embedded Crystal": "Crystal",
    "ERB": "HTML+ERB",
    "Expect": "Tcl",
    "F# Script": "F#",
    "Finite State Language": "Text",
    "Fish Shell": "fish",
    "Flatbuffers": "Protocol Buffer",
    "Focus": None,
    "Fortran 2003": "Fortran Free Form",
    "Fortran 77": "Fortran",
    "Fortran 90": "Fortran",
    "Fortran 95": "Fortran",
    "FXML": "XML",
    "GDScript": "GDScript",
    "Gencat NLS": "Gettext Catalog",
    "Glimmer JavaScript": "Glimmer JS",
    "Glimmer TypeScript": "Glimmer TS",
    "Glade": "XML",
    "Godot Scene": "Godot Resource",
    "Godot Shaders": "GDShader",
    "Grails": "Groovy Server Pages",
    "Hoon": "hoon",
    "HTML EEx": "HTML+EEX",
    "Igor Pro": "IGOR Pro",
    "InstallShield": "Inno Setup",
    "IPL": None,
    "JavaServer Faces": "Java Server Pages",
    "JSP": "Java Server Pages",
    "JSX": "JavaScript",
    "Jinja Template": "Jinja",
    "Juniper Junos": "Text",
    "Kermit": "Text",
    "Korn Shell": "Shell",
    "Lem": None,
    "LESS": "Less",
    "lex": "Lex",
    "Lisp": "Common Lisp",
    "Literate Idris": "Idris",
    "liquid": "Liquid",
    "LiveLink OScript": "ObjectScript",
    "LLVM IR": "LLVM",
    "m4": "M4",
    "make": "Makefile",
    "Mathematica": "Wolfram Language",
    "Maven": "Maven POM",
    "Modula3": "Modula-3",
    "Mojom": "Thrift",
    "MUMPS": "M",
    "MSBuild script": "XML",
    "MXML": "XML",
    "NAnt script": "XML",
    "NASTRAN DMAP": None,
    "Nushell Object Notation": "Nushell",
    "Org Mode": "Org",
    "Oracle Forms": "PLSQL",
    "Oracle PL/SQL": "PLSQL",
    "Oracle Reports": "PLSQL",
    "Pascal/Pawn": "Pascal",
    "Pascal/Puppet": "Pascal",
    "Patran Command Language": None,
    "peg.js": "PEG.js",
    "PEG": "PEG.js",
    "peggy": "PEG.js",
    "Pek": None,
    "Pest": None,
    "PHP/Pascal/Fortran/Pawn": None,
    "Pig Latin": "PigLatin",
    "PL/I": None,
    "PL/M": None,
    "PO File": "Gettext Catalog",
    "Prisma Schema": "Prisma",
    "Properties": "Java Properties",
    "Protocol Buffers": "Protocol Buffer",
    "ProGuard": "Proguard",
    "PRQL": "SQL",
    "Qt Linguist": "XML",
    "Qt Project": "QMake",
    "Raku/Prolog": "Raku",
    "RapydScript": "Python",
    "Razor": "HTML+Razor",
    "ReasonML": "Reason",
    "Rego": "Open Policy Agent",
    "Rexx": "REXX",
    "Rmd": "RMarkdown",
    "Ruby HTML": "HTML+ERB",
    "sed": "sed",
    "SKILL++": None,
    "SKILL/.NET IL": "CIL",
    "SparForte": None,
    "Specman e": "E",
    "SQL Data": "SQL",
    "SQL Stored Procedure": "SQL",
    "SurrealQL": "SQL",
    "TableGen": "LLVM",
    "Tcl/Tk": "Tcl",
    "TEAL": "Teal",
    "Teamcenter met": "Text",
    "Teamcenter mth": "Text",
    "Templ": "templ",
    "Text": None,
    "TITAN Project File Information": None,
    "TITAN Project File Information (tpd)": None,
    "Titanium Style Sheet": "CSS",
    "TLA+": "TLA",
    "TNSDL": None,
    "tspeg": "PEG.js",
    "TTCN": None,
    "Umka": None,
    "Unity-Prefab": "Unity3D Asset",
    "UXML": "XML",
    "USS": "CSS",
    "VB for Applications": "VBA",
    "Verilog-SystemVerilog": "SystemVerilog",
    "vim script": "Vim Script",
    "Visual Basic": "Visual Basic 6.0",
    "Visual Basic Script": "VBScript",
    "Visual Fox Pro": "xBase",
    "Visual Studio Solution": "Microsoft Visual Studio Solution",
    "Visualforce Component": "Apex",
    "Visualforce Page": "Apex",
    "Vuejs Component": "Vue",
    "Web Services Description": "XML",
    "Windows Message File": "Win32 Message File",
    "Windows Module Definition": "Module Management System",
    "Windows Resource File": "C",
    "WiX include": "XML",
    "WiX source": "XML",
    "WiX string localization": "XML",
    "WXML": "XML",
    "WXSS": "CSS",
    "X++": "C#",
    "XAML": "XML",
    "xBase Header": "xBase",
    "XHTML": "HTML",
    "XMI": "XML",
    "XML-Qt-GTK": "XML",
    "XSD": "XML",
    "yacc": "Yacc",
    "Yang": "YANG",
    "zsh": "Shell",
}


def normalize_language(lang: str) -> str | None:
    """Normalize cloc language name to GitHub linguist name"""
    if lang in CLOC_TO_LINGUIST:
        return CLOC_TO_LINGUIST[lang]
    return lang


def normalize_language_stats(stats: dict[str, int]) -> dict[str, int]:
    """Normalize language names and merge duplicates"""
    normalized: dict[str, int] = {}

    for lang, count in stats.items():
        norm_lang = normalize_language(lang)

        if norm_lang is None:
            continue

        normalized[norm_lang] = normalized.get(norm_lang, 0) + count

    return normalized


def load_github_colors(output_file: Path | None = None) -> dict[str, str]:
    """Fetch GitHub's language colors from linguist YAML"""
    logger.info("Grabbing language colors from GitHub")

    try:
        r = requests.get(LINGUIST_LANGUAGES_URL, timeout=10)
        r.raise_for_status()
        data = yaml.safe_load(r.text)
        colors = {}

        for lang, props in data.items():
            if isinstance(props, dict) and "color" in props:
                colors[lang] = props["color"]

        logger.success(f"Loaded {len(colors)} language colors")

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with output_file.open("w") as f:
                json.dump(colors, f, indent=2)

            logger.debug(f"Saved color data to {output_file}")

        return colors

    except Exception as e:
        logger.warning(f"Couldn't load GitHub colors: {e}")
        return {}


def generate_pie(
    language_stats: dict[str, int],
    colors: dict[str, str],
    output: Path,
    min_percentage: float = 1.5,
) -> None:
    """Generate a pie chart showing language distribution"""
    logger.debug(f"Generating pie chart with {len(language_stats)} languages...")

    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total = sum(language_stats.values()) or 1

    labels = [lang for lang, _ in items]
    sizes = [count for _, count in items]
    chart_colors = [colors.get(lang, "#cccccc") for lang in labels]

    fig, ax = plt.subplots(figsize=(14, 10))

    wedges, texts, autotexts = ax.pie(
        sizes,
        colors=chart_colors,
        autopct=lambda p: f"{p:.1f}%" if p >= min_percentage else "",
        startangle=90,
        pctdistance=0.85,
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(9)
        autotext.set_weight("bold")

    legend_labels = [f"{lang} ({count / total * 100:.1f}%)" for lang, count in items]
    ax.legend(
        wedges,
        legend_labels,
        title="Languages",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9,
        title_fontsize=11,
    )

    ax.set_title(
        "Language Distribution",
        fontsize=16,
        weight="bold",
        pad=20,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=200, bbox_inches="tight")
    plt.close()

    logger.success(f"Saved pie chart to {output}")


def generate_bar(
    language_stats: dict[str, int],
    colors: dict[str, str],
    output: Path,
    top_n: int = 5,
    min_label_width: float = 0.05,
) -> None:
    """Generate a horizontal segmented bar chart showing top N languages"""
    logger.debug(f"Generating segmented bar chart (top {top_n} languages)...")

    items = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    total = sum(language_stats.values()) or 1

    top = items[:top_n]
    other_count = total - sum(count for _, count in top)

    segments = top + ([("Other", other_count)] if other_count > 0 else [])

    fig, ax = plt.subplots(figsize=(12, 4))

    left = 0
    bar_height = 0.6

    for lang, count in segments:
        width = count / total
        color = colors.get(lang, "#cccccc")

        ax.barh(
            0,
            width,
            bar_height,
            left=left,
            color=color,
            edgecolor="white",
            linewidth=2,
        )

        if width >= min_label_width:
            ax.text(
                left + width / 2,
                0,
                f"{width * 100:.1f}%",
                ha="center",
                va="center",
                color="white",
                fontsize=11,
                weight="bold",
            )

        left += width

    legend_elements = [
        mpatches.Patch(
            color=colors.get(lang, "#cccccc"),
            label=f"{lang} ({count / total * 100:.1f}%)",
        )
        for lang, count in segments
    ]

    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=min(len(segments), 3),
        frameon=False,
        fontsize=10,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 0.5)
    ax.axis("off")

    ax.set_title(
        f"Top {top_n} Languages",
        fontsize=14,
        weight="bold",
        pad=15,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=200, bbox_inches="tight")
    plt.close()

    logger.success(f"Saved segmented bar chart to {output}")
