import pandas as pd
from src.transform import gor_lang


def exempel_rader():
    kolumner = ["region", "ålder"]
    for kod, namn in [("BE0101A2", "Inrikes inflyttningar"),
                      ("BE0101A3", "Inrikes utflyttningar"),
                      ("BE0101A4", "Inrikes flyttningsöverskott")]:
        for ar in (2015, 2016):
            kolumner.append(f"{kod} - {namn} {ar} - {ar}")
    rader = [
        ["0114 - 0114 Upplands Väsby", "tot - totalt ålder", 10, 11, 6, 5, 4, 6],
        ["0180 - 0180 Stockholm", "tot - totalt ålder", 50, 60, 70, 80, -20, -20],
    ]
    return pd.DataFrame(rader, columns=kolumner)


def test_en_rad_per_kommun_och_ar():
    ut = gor_lang(exempel_rader())
    assert len(ut) == 4  # 2 kommuner x 2 år


def test_kolumnerna_ar_ratt():
    ut = gor_lang(exempel_rader())
    assert list(ut.columns) == ["kommun_kod", "kommun", "ar",
                                "inflyttningar", "utflyttningar", "flyttnetto"]


def test_kod_och_namn_delas_upp():
    ut = gor_lang(exempel_rader())
    assert set(ut["kommun_kod"]) == {"0114", "0180"}
    assert "Upplands Väsby" in set(ut["kommun"])


def test_varden_hamnar_pa_ratt_ar():
    ut = gor_lang(exempel_rader())
    rad = ut[(ut["kommun"] == "Stockholm") & (ut["ar"] == 2016)].iloc[0]
    assert rad["inflyttningar"] == 60
    assert rad["utflyttningar"] == 80
    assert rad["flyttnetto"] == -20