## Dev Tool

### - Linux

```bash
# antes...
# Se não tiver o Postgres, rode o seguinte:


./run.sh debug #executa em modo local, utilizando seu Java

./run.sh #executa atráves do imagem Docker, pre-requisito para o deploy

docker compose -f docker-compose-llm.yml up -d # com llm do ollama executando

docker compose up -d # sem modelo llm, mais leve em computadores de bonecas
```


