import pandas as pd

from dto.atleta_dto import atleta_dto
from dto.goleiro_dto import goleiro_dto
from dto.linha_dto import linha_dto
from scraper.parser_utils import (
    cell,
    column_tokens,
    find_row_by_name,
    normalize_team_name,
    sanitize_and_flatten,
    safe_float,
    safe_int,
    texto,
)

SETORES_VALIDOS = {"GK", "DF", "MF", "FW"}

# Colunas de cada tabela
T6_NOME, T6_NACIONALIDADE, T6_SETOR = 1, 2, 3
T6_PARTIDAS, T6_AMARELO, T6_VERMELHO, T6_SEGUNDO_AMARELO = 5, 6, 7, 8
T6_CRUZAMENTOS, T6_DESARMES = 12, 14

T1_GOLS, T1_ASSISTENCIAS = 9, 10
T4_CHUTES, T4_CHUTES_NO_GOL = 7, 8
T3_GOLS_SOFRIDOS, T3_CHUTES_SOFRIDOS, T3_DEFESAS = 9, 11, 12
T3_PORCENTAGEM_DEFESA, T3_JOGOS_SEM_SOFRER = 13, 17

# Tokens que identificam cada tabela pelo cabeçalho (ordem importa: do mais específico ao mais geral)
ASSINATURAS = {
    "disciplina": {"crdy", "fls"},   # Tabela 6
    "goleiros": {"sota", "save%"},   # Tabela 3
    "chutes": {"sh", "sot"},         # Tabela 4
    "geral": {"gls", "ast"},         # Tabela 1
}
# Posição usada só se a detecção por cabeçalho falhar
POSICAO_FALLBACK = {"geral": 0, "goleiros": 2, "chutes": 3, "disciplina": 5}


def _remover_linhas_resumo(df: pd.DataFrame) -> pd.DataFrame:
    # Remove cabeçalhos repetidos e linhas de total (Squad Total / Opponent Total)
    nomes = df.iloc[:, 0].astype(str).str.strip().str.lower()
    invalidas = nomes.isin({"", "nan", "player", "jogador"}) | nomes.str.startswith(
        ("squad total", "opponent")
    )
    return df[~invalidas]


def _localizar_tabelas(tables: list[pd.DataFrame], clube_nome: str) -> dict[str, pd.DataFrame]:
    flat = [sanitize_and_flatten(t) for t in tables]
    encontradas: dict[str, pd.DataFrame] = {}

    for df in flat:
        tokens = column_tokens(df)
        if "player" not in tokens:
            continue
        for papel, assinatura in ASSINATURAS.items():
            if papel not in encontradas and assinatura <= tokens:
                encontradas[papel] = df
                break

    if "disciplina" not in encontradas:
        if len(flat) < 6:
            print(f"[ERRO ATLETA PARSER] Tabela principal de jogadores não encontrada para {clube_nome}.")
            return {}
        print(f"[ALERTA ATLETA PARSER] Detecção por cabeçalho falhou para {clube_nome}; usando posições fixas.")
        encontradas = {papel: flat[i] for papel, i in POSICAO_FALLBACK.items()}

    return {papel: _remover_linhas_resumo(df) for papel, df in encontradas.items()}


def _nacionalidade(valor) -> str:
    # converte nacionalidade, ex: 'br BRA' -> 'BRA'
    s = texto(valor)
    return s[-3:] if len(s) >= 3 else s


def _setor(valor) -> list[str]:
    posicoes = [p.strip().upper() for p in texto(valor).split(",") if p.strip()]
    return [p for p in posicoes if p in SETORES_VALIDOS]


def parse_atletas(tables: list[pd.DataFrame], clube_nome: str) -> list[atleta_dto]:
    # Retorna instâncias de goleiro_dto e linha_dto para o elenco de um clube
    if not tables:
        return []

    clube_nome = normalize_team_name(clube_nome)
    tabs = _localizar_tabelas(tables, clube_nome)
    if not tabs:
        return []

    tab_geral = tabs.get("geral")
    tab_goleiros = tabs.get("goleiros")
    tab_chutes = tabs.get("chutes")

    atletas: list[atleta_dto] = []

    for _, row in tabs["disciplina"].iterrows():
        nome = cell(row, T6_NOME, texto, "")
        if not nome:
            continue

        setor = _setor(row.iloc[T6_SETOR - 1])

        base = dict(
            nome=nome,
            clube_nome=clube_nome,
            nacionalidade=_nacionalidade(row.iloc[T6_NACIONALIDADE - 1]),
            setor=setor,
            partidasJogadas=cell(row, T6_PARTIDAS, safe_float, 0.0),
            cartaoAmarelo=cell(row, T6_AMARELO, safe_int, 0),
            segundoCartaoAmarelo=cell(row, T6_SEGUNDO_AMARELO, safe_int, 0),
            cartaoVermelho=cell(row, T6_VERMELHO, safe_int, 0),
        )

        if "GK" in setor:
            r3 = find_row_by_name(tab_goleiros, nome)
            if r3 is None:
                print(f"[ALERTA ATLETA PARSER] {nome} ({clube_nome}) sem linha na tabela de goleiros; estatísticas zeradas.")
            atletas.append(
                goleiro_dto(
                    **base,
                    defesas=cell(r3, T3_DEFESAS, safe_int, 0),
                    golsSofridos=cell(r3, T3_GOLS_SOFRIDOS, safe_int, 0),
                    porcentagemDefesa=cell(r3, T3_PORCENTAGEM_DEFESA, safe_float, 0.0),
                    jogosSemSofrerGols=cell(r3, T3_JOGOS_SEM_SOFRER, safe_int, 0),
                    chutesSofridos=cell(r3, T3_CHUTES_SOFRIDOS, safe_int, 0),
                )
            )
        else:
            r1 = find_row_by_name(tab_geral, nome)
            r4 = find_row_by_name(tab_chutes, nome)
            atletas.append(
                linha_dto(
                    **base,
                    gols=cell(r1, T1_GOLS, safe_int, 0),
                    assistencias=cell(r1, T1_ASSISTENCIAS, safe_int, 0),
                    chutes=cell(r4, T4_CHUTES, safe_int, 0),
                    chutesNoGol=cell(r4, T4_CHUTES_NO_GOL, safe_int, 0),
                    desarmes=cell(row, T6_DESARMES, safe_int, 0),
                    cruzamentos=cell(row, T6_CRUZAMENTOS, safe_int, 0),
                )
            )

    print(f"[ATLETA PARSER] {len(atletas)} atletas processados para {clube_nome}")
    return atletas