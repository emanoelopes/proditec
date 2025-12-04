import requests
from bs4 import BeautifulSoup

url = "https://avamecinterativo.mec.gov.br/"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Exemplo: extrair todos os títulos das atividades
for titulo in soup.find_all("MuiTypography-root-118 jss161 MuiTypography-body1-120"):
    print(titulo.get_text(strip=True))
    # Exibir o conteúdo HTML da página para inspeção
    print(soup.prettify())