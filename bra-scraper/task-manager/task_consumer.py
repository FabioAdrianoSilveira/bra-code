import asyncio

from dto.goleiro_dto import goleiro_dto
from scraper.atleta_parser import parse_atletas
from scraper.extractor import fetch_and_parse_tables
from scraper.clube_parser import parse_clubes
from sql_operations import (
    SQL_CLUBE_EXISTE,
    SQL_CLUBE_PLACEHOLDER,
    SQL_UPSERT_ATLETA,
    SQL_UPSERT_GOLEIRO,
    SQL_UPSERT_LINHA,
    SQL_UPSERT_CLUBE,
)

# Pausa entre páginas para reduzir o risco de bloqueio pelo FBref
REQUEST_DELAY = 3

class task_consumer:
    def __init__(self, queue: asyncio.Queue, db, browser):
        self.queue = queue
        self.db = db
        self.browser = browser
        self.falhas: list[dict] = []

    async def start(self):
        while True:
            task = await self.queue.get()
            if task is None:
                self.queue.task_done()
                break

            try:
                await self.process_task(task)
            except Exception as e:
                print(f"[ERRO CONSUMER] Falha ao processar {task}: {e}")
                self.falhas.append(task)
            finally:
                self.queue.task_done()

            await asyncio.sleep(REQUEST_DELAY)

    async def process_task(self, task: dict):
        task_type = task.get("type", "CLUBE")
        url = task.get("url")

        print(f"\n[CONSUMER] Processando [{task_type}]: {url}")

        page = await self.browser.get(url)
        tables = await fetch_and_parse_tables(page)

        if not tables:
            print(f"[ALERTA CONSUMER] Nenhuma tabela extraída da URL: {url}")
            self.falhas.append(task)
            return

        if task_type == "CLUBE":
            await self._salvar_clubes(tables)
        elif task_type == "ATLETA":
            await self._salvar_atletas(tables, task["clube_nome"])
        else:
            raise ValueError(f"Tipo de tarefa desconhecido: {task_type}")

        print(f"[CONSUMER SUCESSO] {url} processado e gravado.")

    async def _salvar_clubes(self, tables):
        clubes = parse_clubes(tables)
        print(f"[CONSUMER] Gravando {len(clubes)} clubes...")

        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                for t in clubes:
                    await conn.execute(
                        SQL_UPSERT_CLUBE,
                        t.nome, t.totalPartidas, t.vitorias, t.empates,
                        t.derrotas, t.golsMarcados, t.golsSofridos,
                    )

    async def _salvar_atletas(self, tables, clube_nome: str):
        atletas = parse_atletas(tables, clube_nome)

        if not atletas:
            print(f"[ALERTA CONSUMER] Nenhum atleta extraído para {clube_nome}")
            self.falhas.append({"type": "ATLETA", "clube_nome": clube_nome})
            return

        print(f"[CONSUMER] Gravando {len(atletas)} atletas de {clube_nome}...")

        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                if not await conn.fetchval(SQL_CLUBE_EXISTE, clube_nome):
                    print(
                        f"[ALERTA CONSUMER] '{clube_nome}' não existe na tabela clube "
                        f"(nome diferente do usado na classificação?). Criando registro vazio."
                    )
                    await conn.execute(SQL_CLUBE_PLACEHOLDER, clube_nome)

                for a in atletas:
                    await conn.execute(
                        SQL_UPSERT_ATLETA,
                        a.nome, a.clube_nome, a.nacionalidade, a.setor, a.partidasJogadas,
                        a.cartaoAmarelo, a.segundoCartaoAmarelo, a.cartaoVermelho,
                    )

                    if isinstance(a, goleiro_dto):
                        await conn.execute(
                            SQL_UPSERT_GOLEIRO,
                            a.nome, a.clube_nome, a.defesas, a.golsSofridos,
                            a.porcentagemDefesa, a.jogosSemSofrerGols, a.chutesSofridos,
                        )
                    else:
                        await conn.execute(
                            SQL_UPSERT_LINHA,
                            a.nome, a.clube_nome, a.gols, a.assistencias,
                            a.chutes, a.chutesNoGol, a.desarmes, a.cruzamentos,
                        )