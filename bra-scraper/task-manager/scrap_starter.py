import asyncio
import sys


from pathlib import Path

# Configuração para que os imports de arquivos funcionem
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import nodriver as nd

from task_consumer import task_consumer
from database.database import database
from task_producer import task_producer

URL_TIMES = "https://fbref.com/en/comps/24/Serie-A-Stats"

ATLETAS_LINKS = [
    ["https://fbref.com/en/squads/639950ae/Flamengo-Stats", "Flamengo"],
    ["https://fbref.com/en/squads/abdce579/Palmeiras-Stats", "Palmeiras"],
    ["https://fbref.com/en/squads/2091c619/Athletico-Paranaense-Stats", "Athletico–PR"],
    ["https://fbref.com/en/squads/84d9701c/Fluminense-Stats", "Fluminense"],
    ["https://fbref.com/en/squads/157b7fee/Bahia-Stats", "Bahia"],
    ["https://fbref.com/en/squads/03ff5eeb/Cruzeiro-Stats", "Cruzeiro"],
    ["https://fbref.com/en/squads/422bb734/Atletico-Mineiro-Stats", "Atlético Mineiro"],
    ["https://fbref.com/en/squads/712c528f/Santos-Stats", "Santos"],
    ["https://fbref.com/en/squads/d680d257/Coritiba-Stats", "Coritiba"],
    ["https://fbref.com/en/squads/f98930d1/Red-Bull-Bragantino-Stats", "RB Bragantino"],
    ["https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats", "São Paulo"],
    ["https://fbref.com/en/squads/d9fdd9d9/Botafogo-RJ-Stats", "Botafogo–RJ"],
    ["https://fbref.com/en/squads/33f95fe0/Vitoria-Stats", "Vitória"],
    ["https://fbref.com/en/squads/bf4acd28/Corinthians-Stats", "Corinthians"],
    ["https://fbref.com/en/squads/289e8847/Mirassol-Stats", "Mirassol"],
    ["https://fbref.com/en/squads/83f55dbe/Vasco-da-Gama-Stats", "Vasco da Gama"],
    ["https://fbref.com/en/squads/d5ae3703/Gremio-Stats", "Grêmio"],
    ["https://fbref.com/en/squads/6f7e1f03/Internacional-Stats", "Internacional"],
    ["https://fbref.com/en/squads/2d4d7b6a/Remo-Stats", "Remo"],
    ["https://fbref.com/en/squads/baa296ad/Chapecoense-Stats", "Chapecoense"],
]


async def main():
    db = database()
    browser = None
    consumer_worker = None
    consumer = None

    try:
        await db.connect()
        browser = await nd.start()
        queue: asyncio.Queue = asyncio.Queue()

        producer = task_producer(queue)
        consumer = task_consumer(queue, db, browser)
        consumer_worker = asyncio.create_task(consumer.start())

        print("\n Enfileirando tabela da Série A...")
        await producer.produce_team_task(URL_TIMES)
        await queue.join()

        print("\n Enfileirando raspagem dos atletas...")
        await producer.produce_player_tasks(ATLETAS_LINKS)
        await queue.join()

        await queue.put(None)
        await consumer_worker

        if consumer.falhas:
            print(f"\n[ALERTA] {len(consumer.falhas)} tarefa(s) com falha:")
            for f in consumer.falhas:
                print(f"  - {f.get('time_nome') or f.get('url')}")
        else:
            print("\n[SUCESSO] Extração completa finalizada!")

    finally:
        if consumer_worker and not consumer_worker.done():
            consumer_worker.cancel()
        if browser:
            browser.stop()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())