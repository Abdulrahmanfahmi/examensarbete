from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "db" / "flyttningar.duckdb"


def senaste_api_fil():
    """Hittar den nyaste filen som extract.py har sparat."""
    filer = sorted(RAW_DIR.glob("scb_TAB1212_flyttningar_*.csv"))
    if not filer:
        raise FileNotFoundError("Ingen API-fil i data/raw. Kör först: python src/extract.py")
    return filer[-1]


def main():
    fil = senaste_api_fil()
    # SCB:s CSV är i Windows-1252, inte UTF-8
    df = pd.read_csv(fil, encoding="cp1252")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE raw_flyttningar AS SELECT * FROM df")
    antal = con.execute("SELECT COUNT(*) FROM raw_flyttningar").fetchone()[0]
    con.close()
    print(f"Läste {fil.name} → raw_flyttningar ({antal} rader)")


if __name__ == "__main__":
    main()