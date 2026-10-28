SQL_UPSERT_CLUBE = """
    INSERT INTO clube (nome, total_partidas, vitorias, empates, derrotas, gols_marcados, gols_sofridos)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    ON CONFLICT (nome) DO UPDATE SET
        total_partidas = EXCLUDED.total_partidas,
        vitorias = EXCLUDED.vitorias,
        empates = EXCLUDED.empates,
        derrotas = EXCLUDED.derrotas,
        gols_marcados = EXCLUDED.gols_marcados,
        gols_sofridos = EXCLUDED.gols_sofridos
"""

SQL_CLUBE_EXISTE = "SELECT 1 FROM clube WHERE nome = $1"

SQL_CLUBE_PLACEHOLDER = """
    INSERT INTO clube (nome) VALUES ($1)
    ON CONFLICT (nome) DO NOTHING
"""

SQL_UPSERT_ATLETA = """
    INSERT INTO atleta (
        nome, clube_nome, nacionalidade, setor, partidas_jogadas,
        cartao_amarelo, segundo_cartao_amarelo, cartao_vermelho
    )
    VALUES ($1, $2, $3, $4, $5::float8, $6, $7, $8)
    ON CONFLICT (nome, clube_nome) DO UPDATE SET
        nacionalidade = EXCLUDED.nacionalidade,
        setor = EXCLUDED.setor,
        partidas_jogadas = EXCLUDED.partidas_jogadas,
        cartao_amarelo = EXCLUDED.cartao_amarelo,
        segundo_cartao_amarelo = EXCLUDED.segundo_cartao_amarelo,
        cartao_vermelho = EXCLUDED.cartao_vermelho
"""

SQL_UPSERT_GOLEIRO = """
    INSERT INTO goleiro (
        atleta_nome, clube_nome, defesas, gols_sofridos,
        porcentagem_defesa, jogos_sem_sofrer_gols, chutes_sofridos
    )
    VALUES ($1, $2, $3, $4, $5::float8, $6, $7)
    ON CONFLICT (atleta_nome, clube_nome) DO UPDATE SET
        defesas = EXCLUDED.defesas,
        gols_sofridos = EXCLUDED.gols_sofridos,
        porcentagem_defesa = EXCLUDED.porcentagem_defesa,
        jogos_sem_sofrer_gols = EXCLUDED.jogos_sem_sofrer_gols,
        chutes_sofridos = EXCLUDED.chutes_sofridos
"""

SQL_UPSERT_LINHA = """
    INSERT INTO linha (
        atleta_nome, clube_nome, gols, assistencias,
        chutes, chutes_no_gol, desarmes, cruzamentos
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    ON CONFLICT (atleta_nome, clube_nome) DO UPDATE SET
        gols = EXCLUDED.gols,
        assistencias = EXCLUDED.assistencias,
        chutes = EXCLUDED.chutes,
        chutes_no_gol = EXCLUDED.chutes_no_gol,
        desarmes = EXCLUDED.desarmes,
        cruzamentos = EXCLUDED.cruzamentos
"""