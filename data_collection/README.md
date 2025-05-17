# 🏃‍♂️ Projeto Corridas PB

Este projeto coleta, organiza e armazena metadados de eventos de corrida do estado da Paraíba, Brasil, em uma instância MongoDB rodando em Docker, facilitando análises e integrações futuras.

---

## 🚀 Sumário

- [Pré-requisitos](#pré-requisitos)
- [Subindo o MongoDB com Docker](#subindo-o-mongodb-com-docker)
- [Instalando as dependências Python](#instalando-as-dependências-python)
- [Executando os scrapers](#executando-os-scrapers)
- [Importando os dados para o MongoDB](#importando-os-dados-para-o-mongodb)
- [Verificando os dados no MongoDB](#verificando-os-dados-no-mongodb)
- [Estrutura dos arquivos](#estrutura-dos-arquivos)
- [Observações](#observações)

---

## 🛠️ Pré-requisitos

- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Google Chrome](https://www.google.com/chrome/) instalado (para Selenium)
- [ChromeDriver](https://sites.google.com/chromium.org/driver/) compatível com sua versão do Chrome (ou use o webdriver-manager)

---

## 🐳 Subindo o MongoDB com Docker

1. **Construa a imagem Docker:**

   ```bash
   docker build -t mongo_bd:latest .
   ```

2. **Rode o container na porta alternativa 27018:**
   ```bash
   docker run -d -p 27018:27018 --name mongo_bd-container mongo_bd:latest
   ```

---

## 📦 Instalando as dependências Python

Recomenda-se o uso de um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

## 🕷️ Executando os scrapers

Execute os dois scrapers para gerar os arquivos CSV com os metadados dos eventos:

```bash
python scraper_brasilcorrida.py
python scraper_brasilquecorre.py
```

Os arquivos `eventos_brasilcorrida.csv` e `eventos_brasilquecorre.csv` serão gerados na raiz do projeto.

---

## 🗃️ Importando os dados para o MongoDB

Após gerar os CSVs, execute o script de importação:

```bash
python import_to_mongodb.py
```

- O script irá:
  - Conectar ao MongoDB na porta 27018
  - Limpar a coleção `eventos` do banco `corridas_db`
  - Importar todos os eventos dos dois arquivos CSV
  - Adicionar metadados de fonte e data de importação

---

## 🔎 Verificando os dados no MongoDB

Você pode acessar o MongoDB via terminal:

```bash
docker exec -it mongo_bd-container mongosh --port 27018
```

No prompt do MongoDB, use:

```mongodb
use corridas_db
db.eventos.find().pretty()
```

---

## 📁 Estrutura dos arquivos

```
.
├── Dockerfile
├── requirements.txt
├── scraper_brasilcorrida.py
├── scraper_brasilquecorre.py
├── import_to_mongodb.py
├── eventos_brasilcorrida.csv
├── eventos_brasilquecorre.csv
└── README.md
```

---

## ⚠️ Observações

- Sempre execute os scrapers antes de importar para garantir dados atualizados.
- O script de importação sempre limpa a coleção antes de inserir novos dados.
- O MongoDB padrão do seu sistema continuará rodando normalmente, pois este projeto usa a porta 27018.
- Se quiser rodar novamente, basta repetir os passos de scraping e importação.

---

**Dúvidas ou sugestões? Abra uma issue!**
