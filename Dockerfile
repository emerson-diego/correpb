FROM mongo:latest

# Expor porta alternativa para o MongoDB
EXPOSE 27018

# Configurar o MongoDB para rodar na porta 27018
CMD ["mongod", "--port", "27018"] 