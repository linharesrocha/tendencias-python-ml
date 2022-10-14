# Imports
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from datetime import date
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import time


def posicao_nomes_links(url):
    global data

    page = requests.get(url)
    site = BeautifulSoup(page.content, "html.parser")

    # Criando lista para armazenar produtos dos 3 Carroseis
    posicao_list = []
    nome_list = []
    link_list = []

    # Pegando todos os cards do carrousel de produtos de uma categoria
    content = site.find(class_='ui-category-trends-desktop-content-main')

    posicoes = content.findAll('div', class_='ui-category-trends-entry-description')
    nomes = content.findAll('h3', class_='ui-category-trends-entry-keyword')
    links = content.findAll(class_='ui-category-trends-entry-container', href=True)

    # Coletando posições, nomes e links das categorias tendências
    for posicao in posicoes:
        posicao_list.append(posicao.getText())
    for nome in nomes:
        nome_list.append(nome.getText().title())
    for link in links:
        link_list.append(link.get('href').replace('#trend', '').split(ch, 1)[0])

    dicionario = {'Posicao': posicao_list, 'Nome': nome_list, 'Link_ML': link_list}
    data = pd.DataFrame(dicionario)
    return data


def vendas_anuncios():
    print(str(index) + '/' + str(len(url_list)) + '  --->  ' + categorias_list[index])
    link_list = data['Link_ML'].tolist()

    normal_quantity_list = []
    full_quantity_list = []
    porcentagem_no_full_list = []
    links_3_anuncios = []
    vendas_anuncio_1 = []
    vendas_anuncio_2 = []
    vendas_anuncio_3 = []

    # Acessando a página de cada categoria tendência
    aux1 = 1
    for link in link_list:
        print(str(aux1) + '/' + str(len(link_list)) + ' --> ' + link)
        page = requests.get(link)
        site = BeautifulSoup(page.content, "html.parser")
        try:
            normal_string_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
            normal_total_quantity = int(re.sub('[^0-9]', '', normal_string_quantity))
        except:
            # Removendo caso não ache nenhuma informação na página de anúncios da categoria
            normal_quantity_list.append('ERRO')
            full_quantity_list.append('ERRO')
            porcentagem_no_full_list.append('ERRO')
            vendas_anuncio_1.append('ERRO')
            vendas_anuncio_2.append('ERRO')
            vendas_anuncio_3.append('ERRO')
            continue

        # Coletando quantidade de anúncio do Full
        try:
            full_container = site.find('a', class_='ui-search-filter-icon ui-search-link',
                                       attrs={"aria-label": "Full"})
            full_string_quantity = full_container.find('span', class_="ui-search-filter-results-qty").getText()
            full_int_quantity = int(re.sub('[^0-9]', '', full_string_quantity))
            full_quantity_list.append(full_int_quantity)
        except AttributeError:
            full_int_quantity = 0
            full_quantity_list.append(full_int_quantity)

        # Anuncios Totais do ML (Full, Flex, Normal) - FULL
        normal_int_quantity = normal_total_quantity - full_int_quantity
        normal_quantity_list.append(normal_int_quantity)

        # Porcentagem no FULL
        porcentagem_no_full = round((full_int_quantity / normal_int_quantity) * 100, 1)
        porcentagem_no_full_list.append(str(porcentagem_no_full) + '%')

        # Pega todos os links de produtos da categoria
        todos_anuncios_container = site.find_all('a', class_='ui-search-result__content ui-search-link')
        if len(todos_anuncios_container) != 0:
            aux = 0
            for produto in todos_anuncios_container:
                links_3_anuncios.append(produto.get('href'))
                aux = aux + 1
                if aux == 3:
                    break
        if len(todos_anuncios_container) == 0:
            todos_anuncios_container = site.find_all('div', class_='ui-search-result__image shops__picturesStyles')
            aux = 0
            for produto in todos_anuncios_container:
                filtrando_produto_link = produto.find("a", class_="ui-search-link").get('href')
                links_3_anuncios.append(filtrando_produto_link)
                aux = aux + 1
                if aux == 3:
                    break

        # Acessa cada anúncio coletado, pega as vendas e armazena em uma das três listas
        if len(links_3_anuncios) >= 3:
            for links_anuncios in links_3_anuncios:
                page = requests.get(links_anuncios)
                site = BeautifulSoup(page.content, "html.parser")
                try:
                    vendas = site.find('span', class_='ui-pdp-subtitle').getText()
                except:
                    vendas = 0
                # Conferindo se teve venda
                try:
                    vendas = int(re.sub('[^0-9]', '', vendas))
                except:
                    vendas = 0

                if len(vendas_anuncio_1) == 0:
                    vendas_anuncio_1.append(vendas)
                elif len(vendas_anuncio_2) < len(vendas_anuncio_1):
                    vendas_anuncio_2.append(vendas)
                elif len(vendas_anuncio_3) < len(vendas_anuncio_2):
                    vendas_anuncio_3.append(vendas)
                elif len(vendas_anuncio_1) == len(vendas_anuncio_2) and len(vendas_anuncio_2) == len(
                        vendas_anuncio_3):
                    vendas_anuncio_1.append(vendas)
        else:
            vendas_anuncio_1.append('menos de 3 anuncios')
            vendas_anuncio_2.append('menos de 3 anuncios')
            vendas_anuncio_3.append('menos de 3 anuncios')

        aux1 = aux1 + 1
        # Limpa armazenamento dos três anúncios.
        links_3_anuncios.clear()

    data['Qnt_ML'] = normal_quantity_list
    data['Qnt_Full'] = full_quantity_list
    data['%_no_Full'] = porcentagem_no_full_list
    data['V_Anuncio_1'] = vendas_anuncio_1
    data['V_Anuncio_2'] = vendas_anuncio_2
    data['V_Anuncio_3'] = vendas_anuncio_3
    return data


def google_trends():
    print('GOOGLE TRENDS')
    list_product_names = data['Nome'].tolist()
    link_trends_list = []
    url_google_trends = "https://trends.google.com.br/trends/explore?geo=BR&q="

    for name in list_product_names:
        link_trends_list.append(url_google_trends + name)

    data['Trends'] = link_trends_list
    return data


def qntd_netshoes():
    print('QUANTIDADE NETSHOES')
    nome_list = data['Nome'].tolist()
    qntd_netshoes_list = []
    url = 'https://www.netshoes.com.br/busca?nsCat=Natural&q='

    for name in nome_list:
        page = requests.get(url + name, headers=user_agent)
        site = BeautifulSoup(page.content, "html.parser")

        # Quantidade de anuncios Netshoes
        try:
            container = site.find(class_="items-info")
            product_quantity_string = container.find('span', class_='block').getText()
            list_numbers_string = re.findall(r'\d+', product_quantity_string)
            results = list(map(int, list_numbers_string))
            product_quantity = results[-1]
        except AttributeError:
            product_quantity = 0

        qntd_netshoes_list.append(product_quantity)

    data['Qnt_Netshoes'] = qntd_netshoes_list
    return data


def qntd_magalu():
    print('QUANTIDADE MAGALU')
    nome_list = data['Nome'].tolist()
    qntd_magalu_list = []
    url = 'https://www.magazineluiza.com.br/busca/'
    for name in nome_list:
        page = requests.get(url + name, headers=user_agent)
        site = BeautifulSoup(page.content, "html.parser")
        # Quantidade de anuncios Magalu
        try:
            product_quantity_string = site.find('p', class_='sc-zCoBu jEEPCh').getText()
            list_numbers_string = re.findall(r'\d+', product_quantity_string)
            results = list(map(int, list_numbers_string))
            product_quantity = results[-1]
        except AttributeError:
            product_quantity = 0

        qntd_magalu_list.append(product_quantity)

    data['Qnt_Magalu'] = qntd_magalu_list
    return data


def qntd_dafiti():
    print('QUANTIDADE DAFITI')
    nome_list = data['Nome'].tolist()
    qntd_dafiti_list = []
    url = 'https://www.dafiti.com.br/catalog/?q='
    for name in nome_list:
        page = requests.get(url + name, headers=user_agent)
        site = BeautifulSoup(page.content, "html.parser")
        # Quantidade de anuncios Dafiti
        try:
            product_quantity_string = site.find('span', class_='value').getText()
            list_numbers_string = re.findall(r'\d+', product_quantity_string)
            results = list(map(int, list_numbers_string))
            product_quantity = results[-1]
        except AttributeError:
            product_quantity = 0

        qntd_dafiti_list.append(product_quantity)

    data['Qnt_Dafiti'] = qntd_dafiti_list
    return data


def ultima_atualizacao():
    print('ULTIMA ATUALIZACAO')
    data['UltimaAtualizacao'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    return data


def salvando_aba():
    print('SALVANDO ABA')
    # Salvando no Excel
    data_ordenado = data[
        ['Posicao',
         'Nome',
         'Qnt_Netshoes',
         'Qnt_Dafiti',
         'Qnt_Magalu',
         'Qnt_ML',
         'Qnt_Full',
         '%_no_Full',
         'V_Anuncio_1',
         'V_Anuncio_2',
         'V_Anuncio_3',
         'Link_ML',
         'Trends',
         'UltimaAtualizacao']]

    data_ordenado.to_excel(writer, sheet_name=categorias_list[index], index=False)

    for column in data_ordenado:
        column_length = max(data_ordenado[column].astype(str).map(len).max(), len(column))
        col_idx = data_ordenado.columns.get_loc(column)
        writer.sheets[categorias_list[index]].set_column(col_idx, col_idx, column_length)

    return data


def salvando_excel():
    print('SALVANDO EXCEL')
    writer.save()


def bot_slack():
    print('BOT SLACK')
    # Env
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # Slack Client
    app = slack.WebClient(token=os.environ['SLACK_TOKEN'])

    # Seding
    # app.chat_postMessage(channel='tendencias-2023', text="PRODUTOS TENDÊNCIAS - " + d1)
    # app.files_upload(channels='tendencias-2023', file='XLSX/Tendencias-' + d1 + '.xlsx')

    # Seding Test
    app.chat_postMessage(channel='tendencias-test', text="PRODUTOS TENDÊNCIAS - " + d1)
    app.files_upload(channels='tendencias-test', file='XLSX/Tendencias-' + d1 + '.xlsx')


if __name__ == "__main__":
    # Start time
    st = time.time()

    # Formating Date
    today = date.today()
    d1 = today.strftime("%d-%m-%Y")

    # Separator
    ch = '_'

    # Categorias
    url_list = [
        'https://lista.mercadolivre.com.br/esportes-fitness/',
        # 'https://lista.mercadolivre.com.br/calcados-roupas-bolsas/',
        # 'https://lista.mercadolivre.com.br/saude/',
        # 'https://lista.mercadolivre.com.br/acessorios-veiculos/',
        # 'https://lista.mercadolivre.com.br/alimentos-bebidas/',
        # 'https://lista.mercadolivre.com.br/antiguidades-colecoes/',
        # 'https://lista.mercadolivre.com.br/bebes/',
        # 'https://lista.mercadolivre.com.br/brinquedos-hobbies/',
        # 'https://lista.mercadolivre.com.br/celulares-telefones/',
        # 'https://lista.mercadolivre.com.br/agro/',
        # 'https://lista.mercadolivre.com.br/animais/',
        # 'https://lista.mercadolivre.com.br/arte-papelaria-armarinho/',
        # 'https://lista.mercadolivre.com.br/beleza-cuidado-pessoal/',
        # 'https://lista.mercadolivre.com.br/casa-moveis-decoracao/',
        # 'https://lista.mercadolivre.com.br/construcao/',
        # 'https://lista.mercadolivre.com.br/cameras-acessorios/',
        # 'https://lista.mercadolivre.com.br/eletronicos-audio-video/',
        # 'https://lista.mercadolivre.com.br/ferramentas/',
        # 'https://lista.mercadolivre.com.br/games/',
        # 'https://lista.mercadolivre.com.br/industria-comercio/',
        # 'https://lista.mercadolivre.com.br/joias-relogios/',
        # 'https://lista.mercadolivre.com.br/eletrodomesticos/',
        # 'https://lista.mercadolivre.com.br/festas-lembrancinhas/',
        # 'https://lista.mercadolivre.com.br/informatica/',
        # 'https://lista.mercadolivre.com.br/instrumentos-musicais/',
        # 'https://lista.mercadolivre.com.br/livros-revistas-comics/',
        # 'https://lista.mercadolivre.com.br/mais-categorias/'
    ]
    categorias_list = [
        'esportes-fitness',
        # 'calcados-roupas-bolsas',
        # 'saude',
        # 'acessorios-veiculos',
        # 'alimentos-bebidas',
        # 'antiguidades-colecoes',
        # 'bebes',
        # 'brinquedos-hobbies',
        # 'celulares-telefones',
        # 'agro',
        # 'animais',
        # 'arte-papelaria-armarinho',
        # 'beleza-cuidado-pessoal',
        # 'casa-moveis-decoracao',
        # 'construcao',
        # 'cameras-acessorios',
        # 'eletronicos-audio-video',
        # 'ferramentas',
        # 'games',
        # 'industria-comercio',
        # 'joias-relogios',
        # 'eletrodomesticos',
        # 'festas-lembrancinhas',
        # 'informatica',
        # 'instrumentos-musicais',
        # 'livros-revistas-comics',
        # 'mais-categorias'
    ]

    # Mkdir
    if not os.path.exists('XLSX'):
        os.makedirs('XLSX')

    # Engine Excel
    writer = pd.ExcelWriter('XLSX/' + 'Tendencias' + '-' + d1 + '.xlsx', engine='xlsxwriter')

    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/106.0.0.0 Safari/537.36'}

    # Functions
    index = 0
    for url_item in url_list:
        posicao_nomes_links(url_item)
        vendas_anuncios()
        google_trends()
        qntd_netshoes()
        # qntd_magalu() COLOCAR MAGALU NO DATA ALI EM CIMA QUE FOI TIRADO
        qntd_dafiti()
        ultima_atualizacao()
        salvando_aba()
        index = index + 1
    salvando_excel()
    bot_slack()

    # Tempo decorrido
    elapsed_time = time.time() - st
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
