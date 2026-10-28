import re

import pandas as pd

# Converte para int tratando NaN, vazios e hífens do FBref
def safe_int(val, default: int = 0) -> int:
    try:
        if pd.isna(val) or val == "" or val == "-":
            return default
        return int(float(str(val).replace(",", "")))
    except (ValueError, TypeError):
        return default

# Converte para float tratando NaN, vazios e hífens do FBref
def safe_float(val, default: float = 0.0) -> float:
    try:
        if pd.isna(val) or val == "" or val == "-":
            return default
        return float(str(val).replace(",", ""))
    except (ValueError, TypeError):
        return default

# Converte para string limpa, tratando NaN
def texto(val, default: str = "") -> str:
    try:
        if pd.isna(val):
            return default
    except (ValueError, TypeError):
        pass
    return str(val).strip()

# Achata colunas MultiIndex das tabelas extraídas pelo Pandas
def sanitize_and_flatten(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(str(p) for p in col).strip() for col in df.columns.values]
    return df

# Padroniza nomes de times (travessões viram hífen, espaços duplicados somem)
def normalize_team_name(nome: str) -> str:
    nome = str(nome).replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", nome).strip()

# Conjunto de tokens (minúsculos) dos nomes das colunas, para identificar tabelas
def column_tokens(df: pd.DataFrame) -> set[str]:
    tokens: set[str] = set()
    for c in df.columns:
        tokens.update(t for t in re.split(r"[^a-z0-9%]+", str(c).lower()) if t)
    return tokens

"""Lê a célula da coluna `col` e converte com `cast`.

    Devolve `default` se a linha não existir ou a coluna estiver fora do alcance.
    """
def cell(row: pd.Series | None, col: int, cast=safe_int, default=0):
    if row is None or col < 1 or col > len(row):
        return default
    return cast(row.iloc[col - 1], default)

# Busca o atleta pelo nome: igualdade exata primeiro; contains só se for único
def find_row_by_name(df: pd.DataFrame | None, nome: str) -> pd.Series | None:
    if df is None or df.empty:
        return None

    nomes = df.iloc[:, 0].astype(str).str.strip()

    exato = df[nomes.str.lower() == nome.strip().lower()]
    if not exato.empty:
        return exato.iloc[0]

    parcial = df[nomes.str.contains(nome, regex=False, case=False)]
    if len(parcial) == 1:
        return parcial.iloc[0]

    return None