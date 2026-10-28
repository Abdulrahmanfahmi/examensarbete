import re
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "db" / "flyttningar.duckdb"

MATT = {
    "BE0101A2": "inflyttningar",
    "BE0101A3": "utflyttningar",
    "BE0101A4": "flyttnetto",
}
KOLUMN_RE = re.compile(r"^(BE\w+) - .+ (\d{4}) - \d{4}$")
REGION_RE = re.compile(r"^(\d{4}) - \d{4} (.+)$")


def gor_lang(raw: pd.DataFrame) -> pd.DataFrame:
    """Gör om bred tabell (en kolumn per mått och år) till en rad per kommun och år."""
    region_kolumn = raw.columns[0]
    varde_kolumner = [c for c in raw.columns if KOLUMN_RE.match(c)]

    lang = raw.melt(
        id_vars=[region_kolumn], value_vars=varde_kolumner,
        var_name="kolumn", value_name="varde",
    )
    delar = lang["kolumn"].str.extract(KOLUMN_RE)
    lang["matt"] = delar[0].map(MATT)
    lang["ar"] = delar[1].astype(int)

    reg = lang[region_kolumn].str.extract(REGION_RE)
    lang["kommun_kod"] = reg[0]
    lang["kommun"] = reg[1]

    ut = lang.pivot(index=["kommun_kod", "kommun", "ar"], columns="matt", values="varde")
    ut = ut.reset_index()
    ut.columns.name = None
    return ut[["kommun_kod", "kommun", "ar", "inflyttningar", "utflyttningar", "flyttnetto"]]


def main():
    con = duckdb.connect(str(DB_PATH))
    raw = con.execute("SELECT * FROM raw_flyttningar").df()
    flytt = gor_lang(raw)
    con.execute("CREATE OR REPLACE TABLE flyttningar AS SELECT * FROM flytt")
    antal = con.execute("SELECT COUNT(*) FROM flyttningar").fetchone()[0]
    con.close()
    print(f"raw_flyttningar → flyttningar ({antal} rader)")


if __name__ == "__main__":
    main()