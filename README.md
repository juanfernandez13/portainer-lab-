# Portainer Lab — Flask + Redis + Nginx

Projeto didático para aprender a **subir uma stack no Portainer a partir de um repositório Git**, incluindo build de imagem própria via Dockerfile.

## Arquitetura

```
   Browser ──► Nginx (porta 8080) ──► Flask/Gunicorn ──► Redis
                                                          │
                                                      volume: redis-data
```

- **app** — Flask que incrementa um contador no Redis a cada visita. **Imagem é buildada** a partir de `app/Dockerfile`.
- **redis** — armazenamento persistente (AOF habilitado) com healthcheck.
- **nginx** — reverse proxy publicando a porta 80 do container em `${HTTP_PORT}` no host.

## Estrutura

```
portainer-lab/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── templates/index.html
└── nginx/
    └── nginx.conf
```

## Rodando localmente (smoke test antes de ir pro Portainer)

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8080
```

Abra `http://localhost:8080` no navegador. Cada refresh incrementa o contador.

Para derrubar:

```bash
docker compose down          # mantém o volume redis-data
docker compose down -v       # apaga também o volume (zera o contador)
```

## Subindo no Portainer (objetivo do laboratório)

### 1. Coloque o projeto no GitHub

```bash
cd portainer-lab
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<seu-user>/portainer-lab.git
git push -u origin main
```

### 2. Criar a Stack no Portainer

1. No menu lateral, vá em **Stacks → + Add stack**.
2. Dê um nome (ex: `portainer-lab`). O nome vira prefixo dos containers (`portainer-lab_app_1`, etc).
3. Em **Build method**, escolha **Repository**.
4. Preencha:
   - **Repository URL**: `https://github.com/<seu-user>/portainer-lab`
   - **Repository reference**: `refs/heads/main`
   - **Compose path**: `docker-compose.yml`
   - (Repositórios privados → marque *Authentication* e informe usuário + Personal Access Token)
5. Em **Environment variables** adicione:
   - `APP_NAME=Meu Lab`
   - `HTTP_PORT=8080`
6. (Opcional) **Enable automatic updates** → Polling a cada X minutos. Toda vez que você der `git push`, o Portainer rebuilda e relança.
7. Clique **Deploy the stack**.

O Portainer vai:
- Clonar o repo.
- Executar o equivalente a `docker compose up -d --build`.
- Mostrar o serviço `app` sendo **buildado** (você vê o Dockerfile sendo executado nos logs).
- Subir os 3 containers.

### 3. Explore a UI do Portainer

Depois que a stack subir, percorra as seções para fixar os conceitos:

- **Containers** → clique em cada um:
  - *Logs* → veja `gunicorn` servindo requisições e `nginx` logando acessos.
  - *Stats* → CPU/memória em tempo real.
  - *Console* → execute `redis-cli` dentro do container `redis` e rode `GET visits`.
  - *Inspect* → JSON cru, ótimo pra entender como o Docker enxerga o container.
- **Images** → repare na imagem `portainer-lab-app:latest` que foi **buildada** localmente (não veio de registry).
- **Volumes** → o volume `portainer-lab_redis-data` aparece aqui. Tente derrubar o container do Redis e subir de novo — o contador persiste.
- **Networks** → veja a rede `portainer-lab_lab-net` ligando os 3 containers.
- **Stacks → portainer-lab → Editor** → edite o `docker-compose.yml` direto pela UI e clique *Update the stack*.
- **Stacks → portainer-lab → Pull and redeploy** → força refresh do Git.

### 4. Cenários para praticar

| Exercício | Como fazer | O que aprende |
|-----------|------------|---------------|
| Mudar a porta exposta | Edite `HTTP_PORT` nas env vars da stack → *Update the stack* | Variáveis de ambiente |
| Quebrar e diagnosticar | Pare o container `redis` pela UI | Healthcheck do `app` vai pra unhealthy + logs de erro |
| Persistência | `down` e `up` mantendo o volume; depois apague o volume | Diferença entre container e volume |
| Build vs Pull | Mude o `image:` do app pra `python:3.12-slim` (e remova `build`) | Diferenciar pull de registry e build local |
| GitOps | Faça push de uma mudança no `index.html` com *automatic updates* ligado | Webhook/poll do Portainer |
| Webhook manual | Em *Stacks → editor* gere um webhook e chame com `curl -X POST <url>` | Trigger de redeploy via HTTP |

## Endpoints

| Rota         | Método | Descrição                                  |
|--------------|--------|--------------------------------------------|
| `/`          | GET    | HTML com contador, incrementa em cada hit  |
| `/health`    | GET    | JSON `{status: ok}` se Redis responde      |
| `/reset`     | POST   | Zera o contador (`curl -X POST .../reset`) |

## Requisitos

- Docker Engine 20.10+
- Docker Compose v2 (`docker compose`, sem hífen)
- Portainer CE 2.19+ (qualquer ambiente: Docker standalone, Swarm ou K8s — esse compose é standalone)
