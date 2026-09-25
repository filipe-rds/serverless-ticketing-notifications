---
name: docker-advisor
description: Revisa, cria ou aconselha sobre Dockerfile, docker-compose.yml e configuração Docker de projetos. Use esta skill SEMPRE que o usuário pedir para criar, revisar, melhorar ou tirar dúvidas sobre Docker, Dockerfile, docker-compose, containerização, imagens, healthcheck, volumes, variáveis de ambiente em containers, ou deploy com Docker. Também dispare com expressões como "dockerizar", "como faço o Docker desse projeto", "meu container não sobe", "quero containerizar", "revise meu Dockerfile". Aplica boas práticas de segurança, performance e separação dev/prod. Pode ser acionada por scaffolding-brainstorm, scaffolding-blueprint ou scaffolding-development quando o projeto mencionar Docker, containerização ou deploy em container.
---

# Docker Advisor

O usuário precisa de ajuda com Docker. Pode ser criar do zero, revisar o que existe, ou resolver um problema específico. Identifique o contexto antes de agir.

## Fase 0 — Identificar o Modo de Operação

Antes de qualquer coisa, entenda o que o usuário quer:

- **Criar do zero**: não há Dockerfile/compose no projeto — você vai gerar
- **Revisar**: há arquivos existentes — leia-os antes de sugerir qualquer coisa
- **Problema específico**: container não sobe, build falha, comportamento inesperado — diagnostique primeiro
- **Tirar dúvida**: explique o conceito ou a decisão de forma clara e contextualizada

Se for criar ou revisar, leia os arquivos relevantes do projeto (linguagem, framework, gerenciador de pacotes, estrutura de pastas) antes de escrever qualquer linha de Docker. Um Dockerfile bom é específico ao projeto — não um template copiado.

Após identificar o modo, apresente ao usuário o que entendeu e o que pretende fazer. Pergunte: "Posso prosseguir?" Não gere nem modifique arquivos Docker sem confirmação.

---

## Dockerfile — Boas Práticas

### Multi-stage builds

Separe build de runtime. O estágio final deve conter apenas o necessário para rodar — sem compiladores, sem ferramentas de build, sem dependências de desenvolvimento.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS production
RUN adduser -D -u 1000 appuser
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist
USER appuser
CMD ["node", "dist/index.js"]
```

Use estágios nomeados (`AS builder`, `AS dev`, `AS production`) — facilita referenciar e permite builds seletivos com `--target`.

### Imagem base

- **Distroless** (preferível para produção): sem shell, sem package manager, sem utilitários — mínimo de superfície de ataque. Ex.: `gcr.io/distroless/nodejs20-debian12`
- **Alpine**: leve (~5MB), boa para dev e builds intermediários; contém shell e busybox
- **Nunca use `:latest`**: pin em versão específica ou digest. `node:20-alpine` é aceitável; `node:latest` não

### Ordenação de layers para cache

A ordem importa para o cache de build. Coloque o que muda menos no topo:

1. Imagem base
2. Instalação de dependências do sistema
3. Cópia dos arquivos de dependências (`package.json`, `requirements.txt`, `go.mod`)
4. Instalação das dependências (`npm ci`, `pip install`, `go mod download`)
5. Cópia do código-fonte
6. Build e configurações

Se o código muda frequentemente mas as dependências não, esse padrão evita reinstalar tudo a cada build.

### Segurança no Dockerfile

**Usuário não-root** — obrigatório em produção:
```dockerfile
RUN adduser -D -u 1000 appuser
USER appuser
```

**Nunca coloque segredos no Dockerfile**. Nem como ARG (fica no histórico da imagem). Para credenciais em tempo de build, use BuildKit secret mounts:
```dockerfile
RUN --mount=type=secret,id=npm_token npm install
```

**COPY, não ADD** — exceto para extrair .tar automaticamente. ADD tem comportamentos implícitos que surpreendem.

**ARG vs ENV**:
- `ARG`: disponível só durante o build, não persiste na imagem — use para parâmetros de build
- `ENV`: persiste na imagem e fica disponível em runtime — use para configuração da aplicação

### .dockerignore

Sempre crie `.dockerignore`. Sem ele, o contexto de build pode incluir gigabytes desnecessários.

Padrões essenciais (adapte à stack):
```
.git/
node_modules/
dist/
build/
.env
.env.*
!.env.example
*.log
coverage/
.vscode/
.idea/
**/*.test.*
**/__tests__/
README.md
docs/
```

---

## Docker Compose — Boas Práticas

### Healthchecks e dependências

Nunca use `depends_on` sem `condition: service_healthy` para serviços que demoram para estar prontos (banco de dados, message brokers). Sem isso, a aplicação tenta conectar antes do serviço estar pronto.

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  app:
    depends_on:
      db:
        condition: service_healthy
```

O `start_period` dá uma janela de tolerância inicial — falhas dentro desse período não contam para o limite de retries.

### Volumes

**Sempre use volumes nomeados** para dados persistentes — nunca volumes anônimos. Volumes anônimos ficam "esquecidos" e acumulam como dangling volumes.

```yaml
volumes:
  db_data:          # declarado aqui
    driver: local

services:
  db:
    volumes:
      - db_data:/var/lib/postgresql/data   # referenciado assim
```

Bind mounts (`.:/app`) são adequados para desenvolvimento com hot reload — nunca em produção.

### Variáveis de ambiente e segredos

**Hierarquia de segurança** (do mais para o menos seguro):
1. Docker Secrets (`secrets:`) — montados em `/run/secrets/`, nunca expostos como env vars
2. Arquivo `.env` externo não commitado
3. `environment:` no compose — visível para todos os processos, pode aparecer em logs

Para senhas, tokens e chaves de API em produção, prefira Docker Secrets:
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  db:
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
```

Nunca commite `.env` com valores reais. Sempre mantenha `.env.example` com as variáveis documentadas mas sem valores sensíveis.

### Dev vs Produção

Use arquivos compostos para separar ambientes:

- `docker-compose.yml` — base comum
- `docker-compose.dev.yml` — sobreposições de dev (bind mounts, portas expostas, ferramentas de debug)
- `docker-compose.prod.yml` — sobreposições de prod (resource limits, restart policies, sem volumes de código)

```bash
# dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

Ou use **profiles** para serviços que só existem em um ambiente:
```yaml
services:
  pgadmin:
    profiles: ["dev"]
```

### Resource limits e restart

Em produção, sempre defina:
```yaml
services:
  app:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

Sem resource limits, um container pode consumir toda a memória do host. Sem restart policy, falhas ficam silenciosas.

---

## Checklist de Revisão

Quando revisar arquivos existentes, verifique:

**Dockerfile**
- [ ] Multi-stage build separando build de runtime
- [ ] Imagem base com versão específica (não `:latest`)
- [ ] Dependências copiadas e instaladas antes do código-fonte
- [ ] Usuário não-root definido com `USER`
- [ ] Nenhum segredo em ARG, ENV ou RUN
- [ ] `.dockerignore` presente e adequado
- [ ] `COPY` usado no lugar de `ADD` onde não é necessário extrair

**Docker Compose**
- [ ] Healthchecks definidos para serviços com tempo de inicialização
- [ ] `depends_on` usa `condition: service_healthy`
- [ ] Volumes nomeados para dados persistentes
- [ ] Segredos não estão hardcoded no arquivo
- [ ] `.env.example` documentando todas as variáveis
- [ ] Restart policy definida para produção
- [ ] Resource limits definidos

**Segurança**
- [ ] Nenhuma senha ou token no código ou nos arquivos Docker
- [ ] Docker socket (`/var/run/docker.sock`) não montado nos containers
- [ ] Imagem base atualizada (não versão com CVEs conhecidos)

---

## Confirmação antes de aplicar

Após gerar ou revisar os arquivos Docker, apresente o resultado completo ao usuário antes de salvar. Pergunte: "Os arquivos estão como esperado? Posso salvar?" Aplique apenas após confirmação.

Em modo de revisão, apresente os findings e pergunte o que o usuário quer corrigir antes de alterar qualquer arquivo.

## Princípios

- **Leia o projeto antes de gerar**: um Dockerfile genérico serve para demonstração, não para uso real
- **Explique as decisões**: o usuário deve entender *por que* cada escolha foi feita, não só copiar e colar
- **Dev e prod têm necessidades diferentes**: não sacrifique a experiência de desenvolvimento em nome da segurança, nem o contrário
- **Segurança não é opcional**: usuário não-root e sem segredos em imagem são requisitos mínimos, não diferenciais
- **Se perceber algo errado além do que foi perguntado**, aponte — mas separe do que foi pedido para não confundir o escopo
