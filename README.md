
# Estrutura do Projeto

```
correpb/
│
├── app/                      # Código principal da aplicação
│   ├── __init__.py
│   ├── api/                  # Endpoints da API
│   │   ├── __init__.py
│   │   ├── eventos.py        # Endpoints relacionados a eventos
│   │
│   ├── core/                 # Configurações e funcionalidades centrais
│   │   ├── __init__.py
│   │   ├── config.py         # Configurações da aplicação
│   │   ├── database.py       # Configuração e conexão com MongoDB
│   │
│   ├── models/               # Modelos de dados (Pydantic)
│   │   ├── __init__.py
│   │   ├── evento.py         # Modelo para eventos
│   │
│   ├── services/             # Lógica de negócios
│   │   ├── __init__.py
│   │   ├── evento_service.py # Serviços relacionados a eventos
│   │
│   └── utils/                # Utilitários e helpers
│       ├── __init__.py
│       └── json_utils.py     # Utilitários para manipulação de JSON
│
│
├── data_collection/              # Scripts utilitários
│
├── logs/                     # Diretório para arquivos de log
│   ├── api.log
│
├── .env                      # Variáveis de ambiente (não versionado)
├── .env.example              # Exemplo de variáveis de ambiente (versionado)
├── .gitignore                # Arquivos a serem ignorados pelo Git
├── requirements.txt          # Dependências do projeto
├── main.py                   # Ponto de entrada principal da aplicação
└── README.md                 # Documentação do projeto
```
# Endpoint para consumo da api

Lista eventos com filtros, ordenação e paginação.

    GET /api/v1/eventos/

Retorna uma lista de eventos sem paginação. Útil para obter dados para filtros ou seleções.

    GET /api/v1/eventos/sem-paginacao

 Obtém um evento pelo ID.

    GET /api/v1/eventos/{id}

# Eventos Banco de Dados

|Campo|Tipo|Descrição|
|:-:|:-:|:-|
|nome|string|Nome do Evento realizado|
|url|string|Endereço online com informações oficiais do evento|
|imagem|string|Endereço da imagem oficial do evento|
|data|datetime|Data em que o Evento será realizado|
|cidade|string|Cidade em que o Evento será realizado|
|distancias|list(string)|Distâncias oferecidas durante o Evento|
|organizacao|string|Informação da entidade organizadora do Evento|
|fonte|string|Site em que o Evento foi coletado|
|data_importacao|datetime|Data da importação do Evento para o Banco de Dados|