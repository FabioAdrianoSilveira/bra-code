import io
import nodriver as nd
import pandas as pd

""" 
Extrai o HTML renderizado da página ativa do Nodriver,
remove comentários HTML para expor tabelas secundárias do FBref e as converte para DataFrames
via Pandas.
 """
async def fetch_and_parse_tables(page: nd.Tab) -> list[pd.DataFrame]:
    # Aguarda 8 segundos para contornar Cloudflare e garantir carregamento completo das tabelas
    await page.sleep(8)

    html_content = await page.get_content()
    html_limpo = html_content.replace("<!--", "").replace("-->", "")

    try:
        tables = pd.read_html(io.StringIO(html_limpo))
        return tables
    except Exception as e:
        print(f"[ERRO EXTRACTOR] Falha ao processar tabelas HTML: {e}")
        return []