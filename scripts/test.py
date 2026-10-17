import pandas as pd

wide = pd.read_csv("data/raw/scb_flyttningar_2015_2024_web.csv",
                   encoding="cp1252", skiprows=2)
print(wide.shape)   # jag väntar mig (290, 32)

long = wide.melt(id_vars=["region", "ålder"], var_name="kolumn", value_name="antal")
d = long["kolumn"].str.extract(
    r"^Inrikes (inflyttningar|utflyttningar|flyttningsöverskott) (\d{4})$")
long["matt"], long["ar"] = d[0], d[1].astype(int)
r = long["region"].str.extract(r"^(\d{4}) (.+)$")
long["kommun_kod"], long["kommun_namn"] = r[0], r[1]

tabell = (long.pivot_table(index=["kommun_kod", "kommun_namn", "ar"],
                           columns="matt", values="antal", aggfunc="first")
              .reset_index())
tabell.columns.name = None
print(tabell.head())
print("Kommuner:", tabell["kommun_kod"].nunique())
print("in - ut = överskott:",
      (tabell["inflyttningar"] - tabell["utflyttningar"] == tabell["flyttningsöverskott"]).all())