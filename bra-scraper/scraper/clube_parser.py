import pandas as pd

from dto.clube_dto import clube_dto
from scraper.parser_utils import (
    cell,
    normalize_team_name,
    sanitize_and_flatten,
    safe_int,
    texto,
)

# Colunas da Tabela
COL_NOME = 2
COL_PARTIDAS = 3
COL_VITORIAS = 4
COL_EMPATES = 5
COL_DERROTAS = 6
COL_GOLS_MARCADOS = 7
COL_GOLS_SOFRIDOS = 8

NOMES_INVALIDOS = {"", "nan", "squad", "time", "equipe", "squad total"}

# Processa a tabela com as informações dos clubes
def parse_clubes(tables: list[pd.DataFrame]) -> list[clube_dto]:
    if not tables:
        return []

    df = sanitize_and_flatten(tables[0])
    clubes: list[clube_dto] = []

    for _, row in df.iterrows():
        nome = normalize_team_name(cell(row, COL_NOME, texto, ""))

        if nome.lower() in NOMES_INVALIDOS:
            continue

        clubes.append(
            clube_dto(
                nome=nome,
                totalPartidas=cell(row, COL_PARTIDAS, safe_int, 0),
                vitorias=cell(row, COL_VITORIAS, safe_int, 0),
                empates=cell(row, COL_EMPATES, safe_int, 0),
                derrotas=cell(row, COL_DERROTAS, safe_int, 0),
                golsMarcados=cell(row, COL_GOLS_MARCADOS, safe_int, 0),
                golsSofridos=cell(row, COL_GOLS_SOFRIDOS, safe_int, 0),
            )
        )

    print(f"[CLUBE PARSER] {len(clubes)} clubes processados")
    return clubes