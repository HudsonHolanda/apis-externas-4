# Open Data Challenges

Suíte de desafios de consulta de api em Python. Cada desafio fica em um subpacote independente dentro de `src/apis_externas_4/challenges/`.

## Requisitos e instalação

- Python 3.11 ou superior
- Poetry 1.8+ (Poetry 2.x também é suportado)

```bash
poetry install
poetry run open-data-challenges --help
```

### Dependências

Dependências de execução:

```bash
poetry add requests pandas plotly folium
```

Dependências de desenvolvimento:

```bash
poetry add --group dev pytest ruff
```

O projeto usa `argparse` da biblioteca padrão para a CLI. Os testes HTTP usam `unittest.mock`, sem exigir uma biblioteca adicional de mocking.

## Módulos

```text
src/apis_externas_4/
├── shared/                         # recursos genéricos da suíte
└── challenges/
    ├── legislative_activity/       # Câmara dos Deputados
    ├── flight_tracking/             # OpenSky Network
    └── space_exploration/           # NASA e NASA Exoplanet Archive
```

Cada módulo segue a separação `application/`, `domain/`, `infrastructure/` e `presentation/`. Os testes ficam em `tests/unit/challenges/<nome_do_desafio>/`.

## 1. Atividade legislativa

```bash
# Listar temas oficiais
poetry run open-data-challenges legislative themes

# Ranking de deputados por tema/ano
poetry run open-data-challenges legislative ranking \
  --theme saude --year 2025 --limit 10

# Heatmap mensal de votos registrados por partido
poetry run open-data-challenges legislative voting-heatmap \
  --year 2025 --metric volume

# Cobertura mensal de membros com pelo menos um voto registrado
poetry run open-data-challenges legislative voting-heatmap \
  --year 2025 --metric rate
```

Métricas e limitações:

- O ranking conta cada proposição uma vez para cada deputado que aparece como autor. Coautorias são contabilizadas para todos os signatários identificados como deputados.
- `volume` soma registros individuais de votos retornados pela API.
- `rate` é uma **cobertura mensal de membros**: percentual dos membros do partido no intervalo mensal que registraram ao menos um voto naquele mês. Não é uma taxa de presença em cada votação.
- Votações simbólicas podem não apresentar votos individuais. A API não lista ausentes como registros individuais de voto.

## 2. Rastreador de voos — OpenSky Network

A bounding box configurada cobre aproximadamente o Brasil continental. Por ser um retângulo, também pode incluir áreas marítimas e pequenas áreas de países vizinhos. O mapa exclui vetores explicitamente marcados como em solo (`on_ground=true`); estados sem esse campo permanecem por não provarem que a aeronave esteja em solo.

```bash
# Mapa de todas as aeronaves retornadas pela OpenSky
poetry run open-data-challenges flights brazil-map

# Filtrar helicópteros
poetry run open-data-challenges flights brazil-map --category rotorcraft

# Aproximação de aeronaves grandes/pesadas (não identifica operador comercial)
poetry run open-data-challenges flights brazil-map --category commercial

# Trajetória completa do voo ao vivo, exigindo atividade nas últimas 6 horas
poetry run open-data-challenges flights track --icao24 abc123 --hours 6

# Consultar o voo associado a um instante Unix dentro de uma trajetória conhecida
poetry run open-data-challenges flights track \
  --icao24 abc123 --timestamp 1793650000 --output artifacts/flight-track.html

# Chegadas e partidas registradas para um aeroporto ICAO
poetry run open-data-challenges flights airport-flights \
  --airport SBGR --direction arrivals --hours 24

poetry run open-data-challenges flights airport-flights \
  --airport SBGR --direction departures --hours 24
```

Configuração opcional de autenticação OAuth2:

```bash
export OPENSKY_CLIENT_ID="seu-client-id"
export OPENSKY_CLIENT_SECRET="seu-client-secret"
```

Sem essas variáveis, o cliente usa o acesso anônimo por IP disponibilizado pela API. Com ambas, obtém e renova automaticamente um token OAuth2. Não coloque credenciais no código nem as versione no Git.

Limitações importantes:

- O acesso autenticado da OpenSky usa exclusivamente OAuth2 client credentials; Basic Auth não é mais aceito. Chamadas anônimas continuam disponíveis para vetores atuais, mas têm resolução temporal e cotas menores.
- `category` é uma categoria de emissor ADS-B, não uma classificação de linha aérea. O filtro `commercial` usa categorias de porte 4, 5 e 6 (large/high-vortex-large/heavy) como aproximação e pode incluir aeronaves não comerciais.
- O endpoint de trajetórias é experimental. `time=0` solicita o track ao vivo; o programa valida a recência pela última posição, mas mantém todos os waypoints para desenhar o voo completo. Para uma trajetória de voo conhecido, informe um Unix timestamp pertencente ao voo. Tracks com mais de 30 dias não são acessíveis pela API REST.
- Os endpoints de chegadas e partidas são atualizados em lote durante a noite; não devem ser tratados como fonte de informação operacional em tempo real.
- A cobertura ADS-B sobre o Brasil depende dos receptores da comunidade OpenSky. Um mapa vazio não prova ausência de aeronaves: pode refletir cobertura limitada, indisponibilidade ou cota esgotada.
- O OpenSky não fornece horários programados, cancelamentos, atrasos ou números comerciais de voo.

Os mapas são arquivos HTML Folium gravados em `artifacts/`.

## 3. Exploração espacial — NASA

Configure uma chave NASA em `NASA_API_KEY`. Sem a variável, o projeto usa `DEMO_KEY`, adequada apenas para exploração inicial e sujeita a limites mais baixos.

```bash
export NASA_API_KEY="sua-chave-nasa"
```

### Asteroides próximos da Terra (NeoWs)

```bash
poetry run open-data-challenges space asteroids \
  --start-date 2025-01-01 --end-date 2025-01-14
```

O programa divide automaticamente intervalos maiores em consultas NeoWs de até sete dias, achata o JSON aninhado e cria um gráfico de dispersão com:

- Distância mínima da Terra em milhões de quilômetros.
- Velocidade relativa em quilômetros por segundo.
- Diâmetro estimado no tamanho do marcador e indicador de potencial periculosidade na cor/hover.
- Eixo de distância em escala logarítmica para acomodar aproximações em ordens de grandeza diferentes.

### APOD

```bash
poetry run open-data-challenges space apod --date 2026-11-02
```

### Dashboard com abas

```bash
poetry run open-data-challenges space dashboard

# Escolher a data da imagem astronômica
poetry run open-data-challenges space dashboard \
  --apod-date 2026-11-02 --output artifacts/space-dashboard.html
```

O dashboard HTML possui três abas: APOD, distribuição dos métodos de descoberta de exoplanetas e mapa EONET dos eventos com geometrias registradas nas últimas 48 horas. O mapa usa as coordenadas representativas de cada geometria como marcadores; para polígonos/linhas, a posição é um centro aproximado.

Fontes e ressalvas:

- NeoWs: `https://api.nasa.gov/neo/rest/v1/feed` — aceita janelas de até sete dias por requisição.
- APOD: o adaptador usa o endpoint WordPress atual `https://science.nasa.gov/wp-json/wp/v2/apod-basic`. O endpoint APOD legado será arquivado em 1º de dezembro de 2026; o código não depende dele.
- EONET: utiliza a API v3 em `https://eonet.gsfc.nasa.gov/api/v3/events`. A consulta busca dois dias e filtra geometrias para a janela exata de 48 horas.
- Exoplanetas: consulta a tabela `pscomppars` via TAP do NASA Exoplanet Archive. Essa tabela fornece uma linha composta por planeta, adequada a uma distribuição estatística por método de descoberta.
- A NASA informa limite padrão de 1.000 requisições por hora por chave; `DEMO_KEY` possui limite significativamente menor (30/h e 50/dia). Os limites podem variar por serviço.

O dashboard é um relatório HTML estático com abas navegáveis, não um servidor web nem uma GUI Python. Gráficos Plotly e mapa Folium carregam bibliotecas/tiles externos no navegador.

## Testes e qualidade

```bash
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
```

Os testes unitários usam respostas simuladas com `unittest.mock`; não dependem de internet nem de chaves de API.

## Fontes oficiais

- Câmara dos Deputados: https://dadosabertos.camara.leg.br/swagger/api.html
- OpenSky REST API: https://openskynetwork.github.io/opensky-api/rest.html
- OpenSky FAQ: https://dev.opensky-network.org/about/faq
- NASA APIs: https://api.nasa.gov/
- NASA APOD: https://science.nasa.gov/wp-json/wp/v2/apod-basic
- NASA EONET v3: https://eonet.gsfc.nasa.gov/docs/v3
- NASA Exoplanet Archive TAP: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html
