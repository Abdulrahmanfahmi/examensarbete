from datetime import datetime
from pathlib import Path

import requests

BASE = "https://statistikdatabasen.scb.se/api/v2/tables/TAB1212/data"
PARAMS = {
    "lang": "sv",
    "outputFormat": "csv",
    "outputFormatParams": "UseCodesAndTexts",
    "codelist[Region]": "vs_RegionKommun07EjAggr",
    "valueCodes[Region]": "*",
    "valueCodes[Alder]": "tot",
    "valueCodes[ContentsCode]": "BE0101A2,BE0101A3,BE0101A4",
    "valueCodes[Tid]": "from(2015)",
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(BASE, params=PARAMS, timeout=60)
    r.raise_for_status()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RAW_DIR / f"scb_TAB1212_flyttningar_{stamp}.csv"
    path.write_bytes(r.content)
    print(f"Sparade {path} ({len(r.content)} bytes)")


if __name__ == "__main__":
    main()
