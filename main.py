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

# Separator
ch = '_'

url_list = ['https://lista.mercadolivre.com.br/esportes-fitness/',
            'https://lista.mercadolivre.com.br/calcados-roupas-bolsas/',
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
            # 'https://lista.mercadolivre.com.br/ingressos/',
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
    'calcados-roupas-bolsas',
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
    # 'ingressos',
    # 'joias-relogios',
    # 'eletrodomesticos',
    # 'festas-lembrancinhas',
    # 'informatica',
    # 'instrumentos-musicais',
    # 'livros-revistas-comics',
    # 'mais-categorias'
]

# Formating Date
today = date.today()
d1 = today.strftime("%d-%m-%Y")

# Mkdir
if not os.path.exists('XLSX'):
    os.makedirs('XLSX')

# Engine Excel
writer = pd.ExcelWriter('XLSX/' + 'Tendencias' + '-' + d1 + '.xlsx', engine='xlsxwriter')

#############################################################################################
#############################################################################################
#############################################################################################


for link_index in range(len(url_list)):
    print(str(link_index + 1) + '/' + str(len(url_list)) + '  --->  ' + categorias_list[link_index])

    page = requests.get(url_list[link_index])
    site = BeautifulSoup(page.content, "html.parser")

    # Criando lista para armazenar produtos dos 3 Carroseis
    posicao_list = []
    nome_list = []
    link_list = []
    normal_quantity_list = []
    full_quantity_list = []
    porcentagem_no_full_list = []
    links_3_anuncios = []
    vendas_3_anuncios = []
    vendas_anuncio_1 = []
    vendas_anuncio_2 = []
    vendas_anuncio_3 = []

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

    # Acessando a página de cada categoria tendência
    for link in link_list:
        page = requests.get(link)
        site = BeautifulSoup(page.content, "html.parser")
        normal_string_quantity = site.find('span', class_="ui-search-search-result__quantity-results").getText()
        normal_total_quantity = int(re.sub('[^0-9]', '', normal_string_quantity))

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

        # Subtraindo a quantidade do full na quantidade de anúncio total
        normal_int_quantity = normal_total_quantity - full_int_quantity
        normal_quantity_list.append(normal_int_quantity)

        # Conta que pega a porcentagem da quantidade de anúncios no full em relação com os anúncios normais
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
        for links_anuncios in links_3_anuncios:
            page = requests.get(links_anuncios)
            site = BeautifulSoup(page.content, "html.parser")

            vendas = site.find('span', class_='ui-pdp-subtitle').getText()

            # Conferindo se teve venda
            try:
                vendas = int(re.sub('[^0-9]', '', vendas))
            except:
                vendas = 0

            # print(len(vendas_anuncio_1) + 1)
            # print(len(vendas_anuncio_2) + 1)
            # print(len(vendas_anuncio_3) + 1)
            # print('-----')

            if len(vendas_anuncio_1) == 0:
                vendas_anuncio_1.append(vendas)
            elif len(vendas_anuncio_2) < len(vendas_anuncio_1):
                vendas_anuncio_2.append(vendas)
            elif len(vendas_anuncio_3) < len(vendas_anuncio_2):
                vendas_anuncio_3.append(vendas)
            elif len(vendas_anuncio_1) == len(vendas_anuncio_2) and len(vendas_anuncio_2) == len(vendas_anuncio_3):
                vendas_anuncio_1.append(vendas)

        # Limpa armazenamento dos três anúncios.
        links_3_anuncios.clear()

    # Google Trends
    url_google_trends = "https://trends.google.com.br/trends/explore?geo=BR&q="
    link_trends_list = []
    for name in posicao_list:
        link_trends_list.append(url_google_trends + name)

    # Salvando em um DataFrame
    dicionario = {'Posicao': posicao_list, 'Nome': nome_list, 'Link_ML': link_list, 'Qnt_Normal': normal_quantity_list,
                  'Qnt_Full': full_quantity_list, '%_no_Full': porcentagem_no_full_list, 'Trends': link_trends_list,
                  'V_Anuncio_1': vendas_anuncio_1,
                  'V_Anuncio_2': vendas_anuncio_2, 'V_Anuncio_3': vendas_anuncio_3}
    data = pd.DataFrame(dicionario)

    # Ultima atualização
    data['UltimaAtualizacao'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Salvando no Excel
    data = data[
        ['Posicao', 'Nome', 'Qnt_Normal', 'Qnt_Full', '%_no_Full', 'V_Anuncio_1', 'V_Anuncio_2', 'V_Anuncio_3',
         'Link_ML',
         'Trends', 'UltimaAtualizacao']]
    data.to_excel(writer, sheet_name=categorias_list[link_index], index=False)

    # for column in data:
    #     column_length = max(data[column].astype(str).map(len).max(), len(column))
    #     col_idx = data.columns.get_loc(column)
    #     writer.sheets['esportes-fitness'].set_column(col_idx, col_idx, column_length)

writer.save()
