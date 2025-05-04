# Projeto Especial - Parte 1 - Extração de Dados com Firecrawl e Análise de Dados com DuckDB

# Importa o módulo os para interagir com o sistema operacional, usado aqui para acessar variáveis de ambiente
import os

# Importa o módulo json para trabalhar com dados no formato JSON, usado para formatar parâmetros de log
import json

# Importa o módulo duckdb para interagir com o banco de dados DuckDB
import duckdb

# Importa o módulo logging para registrar mensagens de log durante a execução do script
import logging

# Importa o módulo datetime para obter a data e hora atuais
import datetime

# Importa a classe FirecrawlApp da biblioteca firecrawl para realizar o web scraping
from firecrawl import FirecrawlApp

# Importa a função load_dotenv da biblioteca python-dotenv para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv

# Importa a classe BeautifulSoup da biblioteca bs4 para fazer o parsing de HTML
from bs4 import BeautifulSoup

# Obtém a data e hora atuais e formata como string
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Configura o sistema de logging para registrar informações com nível INFO
logging.basicConfig(
    
    # Define o nível mínimo de log como INFO
    level = logging.INFO,
    
    # Define o formato das mensagens de log, incluindo timestamp, hora atual, nível do log e a mensagem
    format = f'%(asctime)s - {current_time} - %(levelname)s - %(message)s',
    
    # Define o formato do timestamp nas mensagens de log
    datefmt = '%Y-%m-%d %H:%M:%S'
)

# Carrega as variáveis de ambiente do arquivo .env para o ambiente atual
load_dotenv()

# Obtém o valor da variável de ambiente FIRECRAWL_API_KEY
API_KEY = os.getenv("FIRECRAWL_API_KEY")

# Verifica se a chave da API foi carregada corretamente
if not API_KEY:
    
    # Registra um erro se a chave da API não estiver definida
    logging.error("DSA Log - Erro: A variável de ambiente FIRECRAWL_API_KEY não foi definida.")
    
    # Encerra o script com código de erro 1 se a chave da API não for encontrada
    exit(1)

# Define a URL do site a ser raspado
URL_TO_SCRAPE = "https://books.toscrape.com/"

# Define o nome do arquivo do banco de dados DuckDB
DUCKDB_FILE = "dsa_dados.duckdb"

# Define opções para o processamento da página durante o scraping (atualmente, extrai todo o conteúdo)
PAGE_PROCESSING_OPTIONS = {

    # Define se deve extrair apenas o conteúdo principal da página (False = extrair tudo)
    'onlyMainContent': False,
}

# Define opções para o extrator de dados (não utilizado nesta versão do script)
EXTRACTOR_OPTIONS = {}

# Define os formatos de saída desejados do scraping (neste caso, apenas HTML)
OUTPUT_FORMATS = ['html']

# Define a função principal que orquestra o processo de scraping, armazenamento e análise
def dsa_scrape_store_analyze():

    # Registra o início do processo
    logging.info("DSA Log - Iniciando o processo de scraping, armazenamento e análise...")

    # Registra a inicialização do aplicativo Firecrawl
    logging.info("DSA Log - Inicializando FirecrawlApp...")

    # Inicia um bloco try para capturar possíveis erros durante a inicialização do FirecrawlApp
    try:
        
        # Cria uma instância do FirecrawlApp usando a chave da API
        app = FirecrawlApp(api_key = API_KEY)
    
    # Captura qualquer exceção que ocorra durante a inicialização
    except Exception as e:
        
        # Registra uma mensagem de erro se a inicialização falhar
        logging.error(f"DSA Log - Falha ao inicializar FirecrawlApp: {e}")
        
        # Retorna da função se a inicialização falhar
        return

    # Define os parâmetros para a operação de scraping, começando com os formatos de saída
    scrape_params = {
        
        # Especifica que o formato de saída desejado é HTML
        'formats': OUTPUT_FORMATS
    }

    # Verifica se existem opções de processamento de página definidas
    if PAGE_PROCESSING_OPTIONS:
        
        # Adiciona as opções de processamento de página aos parâmetros de scraping
        scrape_params.update(PAGE_PROCESSING_OPTIONS)

    # Verifica se existem opções de extrator definidas
    if EXTRACTOR_OPTIONS:

        # Registra um aviso informando que as opções do extrator estão definidas, mas não são usadas
        logging.warning("DSA Log - Opções de Extractor definidas, mas não usadas nesta versão do script.")

    # Registra a URL que será raspada
    logging.info(f"DSA Log - Preparando para raspar URL: {URL_TO_SCRAPE}")

    # Registra os parâmetros que serão usados para o scraping, formatados como JSON para legibilidade
    logging.info(f"DSA Log - Usando parâmetros: {json.dumps(scrape_params, indent = 2)}")

    # Inicializa a variável para armazenar os dados raspados como None
    scraped_data = None

    # Inicializa a variável para armazenar o conteúdo HTML como None
    html_content = None

    # Inicia um bloco try para capturar possíveis erros durante o processo de scraping
    try:
        
        # Registra o início do scraping da URL especificada
        logging.info(f"DSA Log - Raspando URL: {URL_TO_SCRAPE}...")
        
        # Chama o método scrape_url do FirecrawlApp para raspar a URL com os parâmetros definidos
        scraped_data = app.scrape_url(URL_TO_SCRAPE, params = scrape_params)

        # Verifica se os dados raspados foram recebidos, se contêm a chave 'html' e se o valor não está vazio
        if scraped_data and 'html' in scraped_data and scraped_data['html']:

            # Atribui o conteúdo HTML à variável html_content
            html_content = scraped_data['html']

            # Registra que o HTML foi obtido com sucesso
            logging.info("DSA Log - HTML obtido com sucesso.")

        # Caso contrário (se o HTML não for obtido).
        else:

            # Registra um erro indicando falha na obtenção do HTML
            logging.error("DSA Log - Falha ao obter HTML nos dados raspados.")

            # Retorna da função se o HTML não for obtido
            return

    # Captura qualquer exceção que ocorra durante o scraping
    except Exception as e:

        # Registra uma mensagem de erro detalhada sobre o erro de scraping, sem incluir o traceback completo no log principal
        logging.error(f"DSA Log - Ocorreu um erro durante o scraping: {e}", exc_info = False)

        # Retorna da função se ocorrer um erro durante o scraping
        return

    # Verifica se o conteúdo HTML foi obtido com sucesso
    if html_content:

        # Registra o início do parsing do HTML e armazenamento no DuckDB
        logging.info("DSA Log - Iniciando parsing do HTML e armazenamento no DuckDB...")

        # Inicia um bloco try para capturar erros durante o parsing do HTML e interação com o banco de dados
        try:

            # Cria um objeto BeautifulSoup para analisar o conteúdo HTML usando o parser 'lxml'
            soup = BeautifulSoup(html_content, 'lxml')

            # Seleciona todos os elementos <article> com a classe 'product_pod', que representam os livros
            product_pods = soup.select('article.product_pod')

            # Inicializa uma lista vazia para armazenar os dados extraídos dos livros
            extracted_books = []

            # Registra quantos 'product_pods' (livros) foram encontrados na página
            logging.info(f"DSA Log - Encontrados {len(product_pods)} 'product_pods' para processar.")

            # Itera sobre cada 'product_pod' encontrado
            for pod in product_pods:

                # Seleciona a tag <a> dentro de <h3>, que contém o título do livro
                title_tag = pod.select_one('h3 a')

                # Extrai o texto do atributo 'title' da tag <a>, remove espaços extras, ou define como None se a tag ou atributo não existirem
                title = title_tag['title'].strip() if title_tag and title_tag.has_attr('title') else None

                # Seleciona a tag <p> com a classe 'price_color' dentro de <div> com a classe 'product_price', que contém o preço
                price_tag = pod.select_one('div.product_price p.price_color')

                # Inicializa a variável de preço como None
                price = None

                # Verifica se a tag de preço foi encontrada
                if price_tag:

                    # Obtém o texto da tag de preço
                    price_text = price_tag.get_text()

                    # Inicia um bloco try para tratar possíveis erros na conversão do preço para número
                    try:

                        # Remove o símbolo '£' e espaços extras do texto do preço
                        price_cleaned = price_text.replace('£', '').strip()

                        # Converte o preço limpo para um número float
                        price = float(price_cleaned)

                    # Captura um erro se a conversão para float falhar
                    except ValueError:

                        # Registra um aviso se a conversão do preço falhar para um livro específico
                        logging.warning(f"DSA Log - Não foi possível converter o preço '{price_text}' para número para o livro '{title}'.")

                # Verifica se tanto o título quanto o preço foram extraídos com sucesso (não são None)
                if title and price is not None:

                    # Adiciona um dicionário com o título e preço do livro à lista 'extracted_books'
                    extracted_books.append({'title': title, 'price': price})

                # Caso contrário (se título ou preço estiverem faltando)
                else:

                    # Registra um aviso sobre dados incompletos para um livro
                    logging.warning(f"DSA Log - Dados incompletos para um livro. Título: {title}, Preço: {price}")

            # Após o loop, verifica se algum dado de livro válido foi extraído
            if not extracted_books:

                # Registra um aviso se nenhum livro válido foi extraído
                logging.warning("DSA Log - Nenhum dado de livro válido extraído do HTML.")
    
                # Retorna da função se não houver livros extraídos
                return

            # Registra quantos livros com título e preço válidos foram extraídos
            logging.info(f"DSA Log - Extraídos {len(extracted_books)} livros com título e preço válidos.")

            # Estabelece uma conexão com o banco de dados DuckDB (cria o arquivo se não existir)
            with duckdb.connect(database = DUCKDB_FILE, read_only = False) as con:

                # Registra que a conexão com o DuckDB foi estabelecida
                logging.info(f"DSA Log - Conectado ao banco de dados DuckDB: {DUCKDB_FILE}")

                # Executa um comando SQL para criar a tabela 'books' se ela ainda não existir
                con.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        title VARCHAR,
                        price DECIMAL(10, 2)
                    );
                """)

                # Registra que a tabela 'books' foi verificada ou criada
                logging.info("DSA Log - Tabela 'books' verificada/criada.")

                # Executa um comando SQL para remover todos os dados existentes da tabela 'books'
                con.execute("DELETE FROM books;")

                # Registra que os dados antigos foram removidos
                logging.info("DSA Log - Dados antigos da tabela 'books' removidos.")

                # Executa um comando SQL para inserir múltiplos registros na tabela 'books'
                con.executemany("INSERT INTO books (title, price) VALUES (?, ?)",
                                [(book['title'], book['price']) for book in extracted_books])

                # Registra quantas linhas foram inseridas na tabela
                logging.info(f"DSA Log - {len(extracted_books)} registros inseridos na tabela 'books'.")

        # Captura qualquer exceção que ocorra durante o parsing ou interação com o DuckDB
        except Exception as db_err:

            # Registra uma mensagem de erro detalhada, incluindo o traceback
            logging.error(f"DSA Log - Erro durante o parsing ou interação com DuckDB: {db_err}", exc_info = True)

            # Retorna da função se ocorrer um erro
            return

        # Registra o início da seção de análise de dados no DuckDB
        logging.info("DSA Log - Iniciando a análise de preço médio via DuckDB.")

        # Inicia um bloco try para capturar erros durante a análise no DuckDB
        try:

            # Estabelece uma conexão somente leitura com o banco de dados DuckDB
            with duckdb.connect(database = DUCKDB_FILE, read_only = True) as con:

                # Executa uma consulta SQL para calcular o preço médio na tabela 'books' e busca o primeiro resultado
                result = con.execute("SELECT AVG(price) FROM books;").fetchone()

                # Verifica se a consulta retornou um resultado e se o valor médio não é None
                if result and result[0] is not None:

                    # Armazena o preço médio calculado
                    average_price = result[0]

                    # Executa uma consulta SQL para contar o número total de livros na tabela e busca o primeiro resultado
                    count_result = con.execute("SELECT COUNT(*) FROM books;").fetchone()

                    # Armazena a contagem de livros, ou 0 se a consulta não retornar resultado
                    book_count = count_result[0] if count_result else 0

                    # Registra que a consulta SQL foi executada
                    logging.info(f"DSA Log - Consulta SQL executada no DuckDB.")

                    # Registra o número de livros usados para o cálculo da média
                    logging.info(f"DSA Log - Número de livros na tabela para cálculo: {book_count}")

                    # Registra o preço médio calculado, formatado com duas casas decimais
                    logging.info(f"DSA Log - PREÇO MÉDIO (calculado pelo DuckDB): £{average_price:.2f}")

                # Caso contrário (se não foi possível calcular a média)
                else:

                    # Registra um aviso indicando que a média não pôde ser calculada
                    logging.warning("DSA Log - Não foi possível calcular a média no DuckDB (tabela vazia ou erro na consulta?).")

        # Captura qualquer exceção que ocorra durante a análise no DuckDB
        except Exception as analysis_err:

            # Registra uma mensagem de erro detalhada sobre o erro de análise, incluindo o traceback
            logging.error(f"DSA Log - Erro durante a análise no DuckDB: {analysis_err}", exc_info = True)

        # Registra o fim da seção de análise
        logging.info("DSA Log - Análise concluída.")

    # Caso o conteúdo HTML não estivesse disponível (bloco 'if html_content:' foi falso)
    else:

        # Registra um erro informando que a análise foi cancelada por falta de conteúdo HTML
        logging.error("DSA Log - Conteúdo HTML não disponível, análise cancelada.")

# Verifica se o script está sendo executado como o programa principal
if __name__ == "__main__":

    # Chama a função principal para executar o processo
    dsa_scrape_store_analyze()

    # Registra a finalização do processo
    logging.info("DSA Log - Processo finalizado.")




    