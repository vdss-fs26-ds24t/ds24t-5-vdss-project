"""
Generiert ydata-profiling HTML-Berichte für alle CSV-Dateien in data_acquisition/raw/.

Verwendung:
  # Alle CSVs im raw-Verzeichnis profileren:
  python eda/generate-data-profile.py

  # Einzelne CSV-Datei:
  python eda/generate-data-profile.py --input data_acquisition/raw/standings.csv

  # Ausgabeverzeichnis anpassen:
  python eda/generate-data-profile.py --output-dir eda/reports/

Voraussetzung: uv run python eda/generate-data-profile.py (aus dem Projekt-Root)
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from ydata_profiling import ProfileReport


DEFAULT_RAW_DIR = Path("data_acquisition/raw")
DEFAULT_OUTPUT_DIR = Path("eda/reports")


def profile_csv(csv_path: Path, output_dir: Path) -> None:
    """Liest eine CSV-Datei und speichert einen ydata-profiling HTML-Bericht."""
    print(f"\n📥 Lade: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"  ❌ Fehler beim Laden: {e}")
        return

    print(f"  ✓ {len(df)} Zeilen × {len(df.columns)} Spalten")

    title = f"Data Profile — {csv_path.stem}"
    print(f"  📊 Generiere Profiling-Report ({title})...")
    try:
        profile = ProfileReport(df, title=title, explorative=True)
    except Exception as e:
        print(f"  ❌ Fehler beim Erstellen des Reports: {e}")
        return

    output_path = output_dir / f"{csv_path.stem}_profile.html"
    try:
        profile.to_file(output_path)
        print(f"  ✅ Gespeichert: {output_path}")
    except Exception as e:
        print(f"  ❌ Fehler beim Speichern: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ydata-profiling Berichte für API-Football Rohdaten generieren",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="Pfad zu einer einzelnen CSV-Datei (Standard: alle CSVs in data_acquisition/raw/)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Ausgabeverzeichnis für HTML-Reports (Standard: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    # Ausgabeverzeichnis anlegen
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Einzeldatei oder Verzeichnis-Modus
    if args.input is not None:
        if not args.input.exists():
            print(f"❌ Datei nicht gefunden: {args.input}")
            sys.exit(1)
        csv_files = [args.input]
    else:
        csv_files = sorted(DEFAULT_RAW_DIR.glob("*.csv"))
        if not csv_files:
            print(f"❌ Keine CSV-Dateien in {DEFAULT_RAW_DIR} gefunden.")
            print("   Zuerst das Notebook data_acquisition/fetch_data.ipynb ausführen.")
            sys.exit(1)

    print(f"📂 Ausgabeverzeichnis: {args.output_dir.resolve()}")
    print(f"📋 Dateien zum Profileren: {[f.name for f in csv_files]}")

    for csv_path in csv_files:
        profile_csv(csv_path, args.output_dir)

    print(f"\n🏁 Fertig. Reports in: {args.output_dir.resolve()}")
    print("   HTML-Dateien im Browser öffnen zur Ansicht.")


if __name__ == "__main__":
    main()
