from bs4 import BeautifulSoup
import requests
import pandas as pd

'''
Existe uma caixa de pesquisa para buscar informações sobre Estados Brasileiros, porém não vamos selecionar
a caixa e digitar o estado para conseguir as informações. Entretanto, ao pesquisar pelos estados o url da página muda apenas o /RS
Posso criar uma função que altere o url.
'''
def scraping_uf(uf: str):
    '''Retorna um dataframe com as infos de um estado'''

    uf_url = f'https://www.ibge.gov.br/cidades-e-estados/{uf}.html'
    browsers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    page = requests.get(uf_url, headers=browsers)

    soup = BeautifulSoup(page.content, 'html.parser') # Fazer a reestruturação da página utilizando o html.parser
    indicadores = soup.select('.indicador') # Navegar pelas class .indicador (Identificada pelo F12)

    uf_dict = {
        dado.select('.ind-label')[0].text: dado.select('.ind-value')[0].text
        for dado in indicadores
    }
    
    # Limpar o texto:
    for indicator in uf_dict:
        if ']' in uf_dict[indicator]:
            uf_dict[indicator] = uf_dict[indicator].split(']')[0][:-8]
        else:
                uf_dict[indicator] = uf_dict[indicator]

    # Criar um Dataframe:
    df = pd.DataFrame(uf_dict.values(), index=uf_dict.keys())
    
    return df

# Teste:   
df_rs = scraping_uf('rs')