# URL Shortener

API de encurtamento de URLs com autenticação JWT, expiração de links e estatísticas de cliques. Feita com **FastAPI**, **SQLAlchemy** e **SQLite**, com testes automatizados em **pytest**.

## Funcionalidades

- Cadastro e login de usuários (senha com hash **bcrypt**, autenticação por **JWT**)
- Criação de links curtos, com código aleatório ou personalizado
- Expiração opcional dos links (de 1 a 365 dias)
- Redirecionamento (HTTP 307) com registro de cada clique
- Estatísticas por link: total de cliques e cliques por dia
- Cada usuário só vê e apaga os próprios links
- Testes automatizados da API

## Tecnologias

Python 3.12, FastAPI, SQLAlchemy 2, SQLite, PyJWT, bcrypt, Pydantic, pytest e ruff.

## Como rodar

```bash
git clone https://github.com/reiarthurramos-web/url-shortener.git
cd url-shortener

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Acesse a documentação interativa em **http://127.0.0.1:8000/docs**.

## Endpoints

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| POST | `/auth/register` | Cadastra um usuário | Não |
| POST | `/auth/login` | Retorna o token JWT | Não |
| POST | `/links` | Cria um link curto | Sim |
| GET | `/links` | Lista os links do usuário | Sim |
| GET | `/links/{code}/stats` | Total de cliques e cliques por dia | Sim |
| DELETE | `/links/{code}` | Apaga um link | Sim |
| GET | `/{code}` | Redireciona para a URL original | Não |

## Exemplo de uso

```bash
# cadastrar
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"voce@exemplo.com","password":"senha12345"}'

# login (guarda o token)
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=voce@exemplo.com&password=senha12345" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# criar um link
curl -X POST http://127.0.0.1:8000/links \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.python.org/about/"}'
```

## Testes

```bash
pytest -v
```

Os testes usam um banco SQLite em memória e cobrem: autenticação obrigatória, criação e redirecionamento, conflito de código personalizado, contagem de cliques, link expirado (410) e isolamento entre usuários.

## Decisões técnicas

- **307 em vez de 301** no redirecionamento: o 301 é guardado em cache pelo navegador e os cliques seguintes não chegariam ao servidor, quebrando a contagem.
- **410 para link expirado**, para diferenciar de um código que nunca existiu (404).
- **404 em vez de 403** ao acessar link de outro usuário, para não revelar quais códigos existem.
- **Chave do JWT por variável de ambiente** (`SECRET_KEY`): o valor padrão serve só para desenvolvimento.

## Próximos passos

- Painel visual de estatísticas
- Docker e PostgreSQL
- Rate limiting
- Deploy
