#!/usr/bin/env python3
"""Prepara los datos del RUNT (datos.gov.co) y la población del DANE para el análisis Datawizards.

Archivos reales usados:
  ev.csv     VEHÍCULOS ELÉCTRICOS E HÍBRIDOS MATRICULADOS EN COLOMBIA - RUNT 2.0 (id ntxy-q9ix)
             COMBUSTIBLE, MODELO, AÑO_REGISTRO, CLASE, CARROCERIA, MUNICIPIO, DEPARTAMENTO, CANTIDAD
  parque.csv CRECIMIENTO DEL PARQUE AUTOMOTOR RUNT2.0 (id u3vn-bdcy)
             NOMBRE_DEPARTAMENTO, NOMBRE_MUNICIPIO, NOMBRE_SERVICIO, ESTADO_DEL_VEHICULO,
             NOMBRE_DE_LA_CLASE, FECHA DE REGISTRO (año), CANTIDAD, MES/AÑO DE PUBLICACIÓN
  dane.xlsx  PPED-AreaMun-2018-2042 (hoja PobMunicipalxÁrea: DP, DPNOM, MPIO, DPMP, AÑO, ÁREA GEOGRÁFICA, TOTAL)

Pasos:
  1) python prep_runt_datosgov.py dane     --xlsx dane.xlsx --anio 2026 --out salida_prep
  2) python prep_runt_datosgov.py explorar --runt ev.csv --out salida_prep
  3) python prep_runt_datosgov.py preparar --runt ev.csv --dane salida_prep/dane_municipios.csv \
         --combustibles ELECTRICO --clases "AUTOMOVIL,CAMIONETA,CAMPERO,BUS,BUSETA,MICROBUS" --out salida_prep
  4) python prep_runt_datosgov.py parque   --runt parque.csv --dane salida_prep/dane_municipios.csv \
         --clases "AUTOMOVIL,CAMIONETA,CAMPERO" --out salida_prep

Alerta de formato: en ev.csv algunas CANTIDAD vienen con separador de miles ("1,164"). Convertirlas
con coerción las vuelve vacías y se pierden las filas más grandes (casi la mitad de los vehículos).
Este script las lee correctamente y reporta cuántas encontró.
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


def a_numero(serie):
    """Convierte texto a número aceptando separador de miles ('1,164'). Devuelve (serie, n_con_separador)."""
    t = serie.astype(str).str.strip()
    n_sep = int(t.str.contains(",", regex=False).sum())
    return pd.to_numeric(t.str.replace(",", "", regex=False), errors="coerce"), n_sep


RENOMBRAR = {"ano_registro": "anio", "a_o_registro": "anio", "fecha_de_registro": "anio",
             "nombre_departamento": "departamento", "nombre_municipio": "municipio",
             "nombre_de_la_clase": "clase", "nombre_servicio": "servicio", "estado_del_vehiculo": "estado"}


def leer(path):
    df = pd.read_csv(path, dtype=str)
    df.columns = [norm(c).replace(" ", "_") for c in df.columns]
    return df.rename(columns=RENOMBRAR)


def dane_a_csv(a):
    os.makedirs(a.out, exist_ok=True)
    raw = pd.read_excel(a.xlsx, sheet_name=a.hoja, header=None, dtype=str)
    fila = raw.index[raw.apply(lambda f: f.astype(str).str.strip().eq("MPIO").any(), axis=1)][0]
    d = pd.read_excel(a.xlsx, sheet_name=a.hoja, header=fila, dtype=str).dropna(subset=["MPIO"])
    d = d[(d["ÁREA GEOGRÁFICA"].str.strip() == "Total") & (pd.to_numeric(d["AÑO"], errors="coerce") == a.anio)]
    out = pd.DataFrame({"divipola": d["MPIO"].str.zfill(5), "departamento": d["DPNOM"], "municipio": d["DPMP"],
                        "poblacion": pd.to_numeric(d["TOTAL"], errors="coerce")})
    out.to_csv(os.path.join(a.out, "dane_municipios.csv"), index=False)
    print(f"dane_municipios.csv: {len(out)} municipios, población {a.anio}: {out['poblacion'].sum():,.0f}")


def explorar(a):
    os.makedirs(a.out, exist_ok=True)
    r = leer(a.runt)
    r["cantidad"], n_sep = a_numero(r["cantidad"])
    print(f"Filas: {len(r)} | CANTIDAD con separador de miles: {n_sep} | CANTIDAD no numérica: {int(r['cantidad'].isna().sum())}")
    print("Vacíos por columna:\n", r.isna().sum())
    for col, f in (("combustible", "valores_combustible.csv"), ("clase", "valores_clase.csv"), ("anio", "anios.csv")):
        (r.groupby(col, dropna=False)["cantidad"].agg(["count", "sum"]).sort_values("sum", ascending=False)
         .to_csv(os.path.join(a.out, f)))
    print(r.groupby("combustible")["cantidad"].sum())
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
        dep_match = kd if kd in por_dep else (process.extractOne(kd, deps, scorer=fuzz.token_set_ratio) or (None, 0))[0]
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
    r["cantidad"], n_sep = a_numero(r["cantidad"])
    print(f"CANTIDAD con separador de miles corregidas: {n_sep}")
    r["anio"] = pd.to_numeric(r["anio"], errors="coerce")
    # calidad del archivo crudo (antes de filtrar): vacíos y rangos
    crudo = [(c, int(r[c].isna().sum()), f"{r[c].isna().mean():.2%}") for c in r.columns]
    pd.DataFrame(crudo, columns=["columna", "vacios", "pct"]).to_csv(os.path.join(a.out, "calidad_runt_crudo.csv"), index=False)
    print("Vacíos en el archivo crudo:", {c: v for c, v, _ in crudo if v})
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
    print("Filas filtradas con cantidad vacía (no suman):", int(r["cantidad"].isna().sum()))
    out = (r.dropna(subset=["divipola"]).groupby(["divipola", "anio"], as_index=False)["cantidad"].sum())
    out.to_csv(os.path.join(a.out, "runt_anual.csv"), index=False)
    print("runt_anual.csv:", len(out), "filas")


def parque(a):
    """Parque activo total (conjunto 'Crecimiento del parque automotor RUNT 2.0') por municipio, solo clases livianas."""
    os.makedirs(a.out, exist_ok=True)
    r = leer(a.runt)
    dane = pd.read_csv(a.dane, dtype={"divipola": str})
    r["cantidad"], n_sep = a_numero(r["cantidad"])
    print(f"CANTIDAD con separador de miles: {n_sep}")
    clases = [norm(x) for x in a.clases.split(",")]
    n0 = len(r)
    r = r[(r["estado"].map(norm) == "activo") & r["clase"].map(norm).isin(clases)].copy()
    print(f"Filas: {n0}; activas y de clases elegidas: {len(r)}")
    alias = None
    if a.alias:
        al = pd.read_csv(a.alias, dtype=str)
        alias = {(norm(x), norm(y)): z.zfill(5) for x, y, z in zip(al["departamento"], al["municipio"], al["divipola"])}
    mapa = cruzar(r, dane, alias)
    r["divipola"] = [mapa[(d, m)][0] for d, m in zip(r["departamento"], r["municipio"])]
    rep = pd.DataFrame([(d, m, *v) for (d, m), v in mapa.items()], columns=["departamento", "municipio", "divipola", "tipo_cruce", "similitud"])
    rep.to_csv(os.path.join(a.out, "reporte_cruce_parque.csv"), index=False)
    print("Cruces:", rep["tipo_cruce"].value_counts().to_dict(), "| sin cruce:", int(r["divipola"].isna().sum()), "filas")
    out = r.dropna(subset=["divipola"]).groupby("divipola", as_index=False)["cantidad"].sum().rename(columns={"cantidad": "parque_liviano"})
    out.to_csv(os.path.join(a.out, "parque_liviano.csv"), index=False)
    print("parque_liviano.csv:", len(out), "municipios;", int(out["parque_liviano"].sum()), "vehículos")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    dd = sp.add_parser("dane")
    dd.add_argument("--xlsx", required=True), dd.add_argument("--anio", type=int, default=2026)
    dd.add_argument("--hoja", default="PobMunicipalxÁrea"), dd.add_argument("--out", default="salida_prep")
    e = sp.add_parser("explorar")
    e.add_argument("--runt", required=True), e.add_argument("--out", default="salida_prep")
    p = sp.add_parser("preparar")
    p.add_argument("--runt", required=True), p.add_argument("--dane", required=True)
    p.add_argument("--combustibles", required=True), p.add_argument("--clases", required=True)
    p.add_argument("--alias", help="CSV opcional departamento,municipio,divipola para cruces manuales")
    p.add_argument("--out", default="salida_prep")
    q = sp.add_parser("parque")
    q.add_argument("--runt", required=True), q.add_argument("--dane", required=True)
    q.add_argument("--clases", default="AUTOMOVIL,CAMIONETA,CAMPERO,MICROBUS")
    q.add_argument("--alias"), q.add_argument("--out", default="salida_prep")
    a = ap.parse_args()
    {"dane": dane_a_csv, "explorar": explorar, "preparar": preparar, "parque": parque}[a.cmd](a)
