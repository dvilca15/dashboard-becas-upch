import os
import pandas as pd
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_table(table: str, columns: str = "*") -> pd.DataFrame:
    """Fetch all rows from a Supabase table with pagination."""
    client = get_client()
    all_rows = []
    page_size = 1000
    offset = 0

    while True:
        response = (
            client.table(table)
            .select(columns)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        data = response.data
        if not data:
            break
        all_rows.extend(data)
        if len(data) < page_size:
            break
        offset += page_size

    return pd.DataFrame(all_rows)


@st.cache_data(ttl=1800)
def load_becarios() -> pd.DataFrame:
    df = fetch_table("BECARIO")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    if "fecha_registro" in df.columns:
        df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
    return df


@st.cache_data(ttl=1800)
def load_matricula() -> pd.DataFrame:
    df = fetch_table("MATRICULA")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    for col in ["prom_semestral", "prom_acumulado", "cred_ganado", "cred_perdidos", "ord_merito"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data(ttl=1800)
def load_perdidas() -> pd.DataFrame:
    df = fetch_table("PERDIDAS_BECA")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    return df


@st.cache_data(ttl=1800)
def load_egresados() -> pd.DataFrame:
    df = fetch_table("EGRESADOS")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    return df


@st.cache_data(ttl=1800)
def load_notas() -> pd.DataFrame:
    df = fetch_table("NOTAS")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    if "periodo_academico" in df.columns:
        df["periodo_academico"] = pd.to_numeric(df["periodo_academico"], errors="coerce")
    if "promedio_curso" in df.columns:
        df["promedio_curso"] = pd.to_numeric(df["promedio_curso"], errors="coerce")
    return df


@st.cache_data(ttl=1800)
def load_orden_merito() -> pd.DataFrame:
    df = fetch_table("ORDEN_MERITO")
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.upper())
    if "nota_promedio" in df.columns:
        df["nota_promedio"] = pd.to_numeric(df["nota_promedio"], errors="coerce")
    return df
