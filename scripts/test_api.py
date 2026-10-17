import pandas as pd

wide = pd.read_csv("data/raw/scb_TAB1212_flyttningar_20261002_020520.csv", encoding="cp1252")
print("Form:", wide.shape)   

long = wide.melt(id_vars=["Region - region", "Alder - ålder"],
                 var_name="kolumn", value_name="antal")

d = long["kolumn"].str.extract(r"^(BE\w+) - .+ (\d{4}) - \d{4}$")
long["matt_kod"], long["ar"] = d[0], d[1].astype(int)

matt_namn = {
    "BE0101A2": "inflyttningar",
    "BE0101A3": "utflyttningar",
    "BE0101A4": "overskott",
}
long["matt"] = long["matt_kod"].map(matt_namn)

r = long["Region - region"].str.extract(r"^(\d{4}) - \d{4} (.+)$")
long["kommun_kod"], long["kommun_namn"] = r[0], r[1]

tabell = (long.pivot_table(index=["kommun_kod", "kommun_namn", "ar"],
                           columns="matt", values="antal", aggfunc="first")
              .reset_index())
tabell.columns.name = None

print(tabell.head())
print("Antal kommuner:", tabell["kommun_kod"].nunique())
print("Inga tomma celler:", tabell.isnull().sum().sum() == 0)
print("Inga dubbletter:", tabell.duplicated(subset=["kommun_kod", "ar"]).sum() == 0)
print("Inflyttning aldrig negativ:", (tabell["inflyttningar"] >= 0).all())
print("Utflyttning aldrig negativ:", (tabell["utflyttningar"] >= 0).all())
print("in - ut = överskott:",
      (tabell["inflyttningar"] - tabell["utflyttningar"] == tabell["overskott"]).all())

sthlm_2021 = tabell[(tabell["kommun_kod"] == "0180") & (tabell["ar"] == 2021)]
print("Stockholm 2021 överskott (väntat -11399):", sthlm_2021["overskott"].values)