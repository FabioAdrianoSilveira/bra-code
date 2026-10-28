import asyncio

from scraper.parser_utils import normalize_team_name

# Produtor responsável por injetar tarefas padronizadas na fila em memória
class task_producer:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def produce_team_task(self, url: str):
        await self.queue.put({"type": "CLUBE", "url": url})

    async def produce_player_tasks(self, player_links: list):
        for link, clube_nome in player_links:
            await self.queue.put({
                "type": "ATLETA",
                "url": link,
                "clube_nome": normalize_team_name(clube_nome),
            })