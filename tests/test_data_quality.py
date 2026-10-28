from pathlib import Path
import duckdb
import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "db" / "flyttningar.duckdb"


@pytest.fixture(scope="module")
def con():
    if not DB_PATH.exists():
        pytest.skip("Databasen saknas. Kör först load.py och transform.py")
    c = duckdb.connect(str(DB_PATH), read_only=True)
    yield c
    c.close()


def varde(con, sql):
    return con.execute(sql).fetchone()[0]


def test_antal_rader(con):
    # 290 kommuner x 10 år (2015-2024)
    assert varde(con, "SELECT COUNT(*) FROM flyttningar") == 2900


def test_290_kommuner(con):
    assert varde(con, "SELECT COUNT(DISTINCT kommun_kod) FROM flyttningar") == 290


def test_tio_ar(con):
    assert varde(con, "SELECT MIN(ar) FROM flyttningar") == 2015
    assert varde(con, "SELECT MAX(ar) FROM flyttningar") == 2024


def test_inga_tomma_varden(con):
    sql = """SELECT COUNT(*) FROM flyttningar
             WHERE kommun_kod IS NULL OR kommun IS NULL OR ar IS NULL
                OR inflyttningar IS NULL OR utflyttningar IS NULL OR flyttnetto IS NULL"""
    assert varde(con, sql) == 0


def test_inga_dubbletter(con):
    sql = """SELECT COUNT(*) FROM (
               SELECT kommun_kod, ar FROM flyttningar
               GROUP BY kommun_kod, ar HAVING COUNT(*) > 1)"""
    assert varde(con, sql) == 0


def test_inga_negativa_in_eller_utflyttningar(con):
    sql = "SELECT COUNT(*) FROM flyttningar WHERE inflyttningar < 0 OR utflyttningar < 0"
    assert varde(con, sql) == 0


def test_in_minus_ut_ar_netto(con):
    sql = "SELECT COUNT(*) FROM flyttningar WHERE inflyttningar - utflyttningar <> flyttnetto"
    assert varde(con, sql) == 0


def test_stockholm_2021_ar_kant_varde(con):
    sql = "SELECT flyttnetto FROM flyttningar WHERE kommun = 'Stockholm' AND ar = 2021"
    assert varde(con, sql) == -11399