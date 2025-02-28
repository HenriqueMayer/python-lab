import requests # Faz a conexão com o servidor
from bs4 import BeautifulSoup # Através da conexão faz a extração de informação

'''
Para não ter perigo de ficar realizando várias verificações e o site derrubar a nossa
conexão, vamos criar uma conexão e trabalahr em cima dela. 
-> Criar uma variável com o request
'''
# Setup
url_globo = 'https://www.globo.com/'
page = requests.get(url_globo) # Response 200 -> OK

# Verificar o que tem no page:
print(page.text)

# Analisando o texto através do BeautifulSoup
resposta = page.text
soup = BeautifulSoup(resposta, 'html.parser')

# Analysis
'''
Entrar no site que vai realizar a coleta e através do F12 encontrar um padrão das informações.
No site da Globo.com as notícias tem esse padrão: h2 class="post__title"
'''
noticias = soup.find_all('h2', {'class': 'post__title'})

# Print só nas notícias:
for i in range(len(noticias)):
    print(noticias[i].text)