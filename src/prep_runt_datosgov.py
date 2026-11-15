#!/usr/bin/env python3
"""Prepara el conjunto 'Vehículos eléctricos e híbridos matriculados - RUNT 2.0' (datos.gov.co, id ntxy-q9ix).

Columnas del conjunto: COMBUSTIBLE, MODELO, AÑO_REGISTRO, CLASE, CARROCERIA,
MUNICIPIO, DEPARTAMENTO, CANTIDAD (una fila = una combinación de características).

Paso 1 (explorar, no filtra nada):
  python prep_runt_datosgov.py explorar --runt runt_ev.csv --out salida_prep
  -> escribe valores_combustible.csv, valores_clase.csv, anios.csv. Revíselos y
     decida con el equipo qué combustibles son BEV y qué clases entran.

Paso 2 (preparar):
  python prep_runt_datosgov.py preparar --runt runt_ev.csv --dane dane_municipios.csv \
      --combustibles "ELECTRICO" --clases "AUTOMOVIL,CAMIONETA,CAMPERO,MICROBUS,BUS,BUSETA" \
      --out salida_prep
  -> runt_anual.csv (divipola, anio, cantidad) para eda_limpieza_datawizards.py
     y reporte_cruce_municipios.csv con lo que no cruzó (corríjalo con --alias alias.csv).

dane_municipios.csv (arme desde el xlsx de proyecciones del DANE): divipola,
departamento, municipio, poblacion. Los valores de --combustibles y --clases son
EJEMPLOS: use los que aparezcan en valores_combustible.csv y valores_clase.csv.
"""
import argparse
import os
import re
import unicodedata

import pandas as pd
from rapidfuzz import fuzz, process

UMBRAL_MUNICIPIO = 92  # similitud mínima dentro del mismo departamento


def norm(t):
    """Minúsculas, sin tildes ni puntuación, sin 'distrito', 'd.c.' o 'municipio de'."""
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\b(distrito|capital|dc|d c|municipio de)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def leer(path):
    df = pd.read_csv(path, dtype=str)
    df.columns = [norm(c).replace(" ", "_") for c in df.columns]
    return df.rename(columns={"ano_registro": "anio", "a_o_registro": "anio"})


def explorar(a):
    os.makedirs(a.out, exist_ok=True)
    r = leer(a.runt)
    r["cantidad"] = pd.to_numeric(r["cantidad"], errors="coerce")
    for col, f in (("combustible", "valores_combustible.csv"), ("clase", "valores_clase.csv"), ("anio", "anios.csv")):
        (r.groupby(col, dropna=False)["cantidad"].agg(["count", "sum"]).sort_values("sum", ascending=False)
         .to_csv(os.path.join(a.out, f)))
    print(r["cantidad"].describe())
    print("Filas:", len(r), "| vacíos por columna:\n", r.isna().sum())
    print("Revise los CSV de valores antes de preparar.")


def cruzar(r, dane, alias=None):
    d = dane.copy()
    d["k_dep"], d["k_mun"] = d["departamento"].map(norm), d["municipio"].map(norm)
    d["divipola"] = d["divipola"].astype(str).str.zfill(5)
    llave = {(a, b): c for a, b, c in zip(d["k_dep"], d["k_mun"], d["divipola"])}
    por_dep = {k: g for k, g in d.groupby("k_dep")}
    deps = list(por_dep)
    salida = {}
    for dep_raw, mun_raw in r[["departamento", "municipio"]].drop_duplicates().itertuples(index=False):
        kd, km = norm(dep_raw), norm(mun_raw)
        if alias is not None and (kd, km) in alias:
            salida[(dep_raw, mun_raw)] = (alias[(kd, km)], "alias", 100)
            continue
        if (kd, km) in llave:
            salida[(dep_raw, mun_raw)] = (llave[(kd, km)], "exacto", 100)
            continue
        dep_match = kd if kd in por_dep else (process.extractOne(kd, deps, scorer=fuzz.ratio) or (None, 0))[0]
        if dep_match in por_dep:
            g = por_dep[dep_match]
            m = process.extractOne(km, list(g["k_mun"]), scorer=fuzz.ratio)
            if m and m[1] >= UMBRAL_MUNICIPIO:
                salida[(dep_raw, mun_raw)] = (g.iloc[m[2]]["divipola"], "difuso", round(m[1], 1))
                continue
        salida[(dep_raw, mun_raw)] = (None, "sin_cruce", 0)
    return salida


def preparar(a):
    os.makedirs(a.out, exist_ok=True)
    r = leer(a.runt)
    dane = pd.read_csv(a.dane, dtype={"divipola": str})
    r["cantidad"] = pd.to_numeric(r["cantidad"], errors="coerce")
    r["anio"] = pd.to_numeric(r["anio"], errors="coerce")
    comb = [norm(x) for x in a.combustibles.split(",")]
    clases = [norm(x) for x in a.clases.split(",")]
    n0 = len(r)
    r = r[r["combustible"].map(norm).isin(comb) & r["clase"].map(norm).isin(clases)].copy()
    print(f"Filas del conjunto: {n0}; tras filtrar combustible y clase: {len(r)}")
    alias = None
    if a.alias:  # CSV: departamento, municipio (como vienen en el RUNT), divipola
        al = pd.read_csv(a.alias, dtype=str)
        alias = {(norm(x), norm(y)): z.zfill(5) for x, y, z in zip(al["departamento"], al["municipio"], al["divipola"])}
    mapa = cruzar(r, dane, alias)
    r["divipola"] = [mapa[(d, m)][0] for d, m in zip(r["departamento"], r["municipio"])]
    rep = pd.DataFrame([(d, m, *v) for (d, m), v in mapa.items()],
                       columns=["departamento", "municipio", "divipola", "tipo_cruce", "similitud"])
    rep = rep.merge(r.groupby(["departamento", "municipio"])["cantidad"].sum().rename("vehiculos").reset_index(), how="left")
    rep.sort_values(["tipo_cruce", "vehiculos"], ascending=[True, False]).to_csv(os.path.join(a.out, "reporte_cruce_municipios.csv"), index=False)
    sin = r["divipola"].isna()
    print(f"Filas sin cruce con DANE: {int(sin.sum())} ({r.loc[sin, 'cantidad'].sum():,.0f} vehículos). Revise reporte_cruce_municipios.csv")
    print("Cruces difusos para validar a mano:", int((rep["tipo_cruce"] == "difuso").sum()))
    out = (r.dropna(subset=["divipola"]).groupby(["divipola", "anio"], as_index=False)["cantidad"].sum())
    out.to_csv(os.path.join(a.out, "runt_anual.csv"), index=False)
    print("runt_anual.csv:", len(out), "filas")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("explorar")
    e.add_argument("--runt", required=True), e.add_argument("--out", default="salida_prep")
    p = sp.add_parser("preparar")
    p.add_argument("--runt", required=True), p.add_argument("--dane", required=True)
    p.add_argument("--combustibles", required=True), p.add_argument("--clases", required=True)
    p.add_argument("--alias", help="CSV opcional departamento,municipio,divipola para cruces manuales")
    p.add_argument("--out", default="salida_prep")
    a = ap.parse_args()
    explorar(a) if a.cmd == "explorar" else preparar(a)
