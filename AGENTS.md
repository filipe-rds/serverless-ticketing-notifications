# AGENTS.md — ticketstream

Documento normativo para agentes de IA e para o desenvolvedor. Fixa as decisões arquiteturais do projeto, o critério que as sustenta e o
modo de trabalho.

Em caso de conflito entre este documento e `README.md`, qualquer arquivo em `docs/` (índice em
[`docs/README.md`](docs/README.md)), os artefatos de fatia em `docs/<fatia>/` ou as skills em `.agents/skills/`,
**este documento prevalece** — os demais são material de origem e podem estar desatualizados.

As regras de negócio vivem em `docs/domain.md` e `docs/use_cases.md`; as interpretações do enunciado
(`docs/project_base.md`) vivem em `docs/requirements.md` como `DEC-xx`.
Divergências conhecidas estão listadas em [Dívidas conhecidas](#dívidas-conhecidas).

---

## 1. Propósito

Projeto didático de backend serverless para venda de ingressos, com dois bounded contexts: `ticketing` (eventos, categorias, reservas,
checkout) e `notifications`
(envio multicanal). Um terceiro, `identity` (cadastro, confirmação e login sobre o Cognito), entra na Etapa 9
(`docs/requirements.md` DEC-19) e segue as mesmas regras de independência.

**O objetivo do projeto é formar base técnica em arquitetura de software.**
A API funcionando é consequência. Uma entrega rápida que borre as fronteiras entre camadas destrói exatamente o valor buscado aqui.

### 1.1 Princípio norteador

Este projeto segue **Clean Architecture com disciplina e proporcionalidade**.

A regra inegociável é:

> **As dependências de código-fonte apontam para dentro, em direção às políticas de nível mais alto.**

Também são inegociáveis:

- regras de negócio no núcleo;
- banco, framework, SDK e transporte como detalhes externos;
- dados simples e independentes cruzando limites;
- bounded contexts independentes.

### 1.2 O que vem do livro e o que é convenção do projeto

#### Princípios arquiteturais baseados no livro anexado

- Dependency Rule;
- casos de uso isolados de banco, UI e framework;
- controllers, presenters e views como **papéis** de Interface Adapters;
- dados simples cruzando limites;
- banco de dados como detalhe;
- ports/gateways definidos do lado que precisa da abstração;
- limites completos têm custo alto; limites parciais são legítimos;
- a arquitetura deve gritar o domínio e os casos de uso.

#### Convenções específicas deste projeto

- Result Pattern nos use cases;
- entidades imutáveis com `dataclass(frozen=True, slots=True)`;
- ports em `application/ports/`;
- `Event` como agregado raiz;
- `Decimal` para dinheiro;
- `UUID` no domínio;
- código em inglês e documentação em português;
- `import-linter` no `make check`.

### 1.3 Regra de proporcionalidade

Este projeto **não** trata Clean Architecture como obrigação de maximalismo.

Quando houver tensão entre:

- uma solução mais formal; e
- uma solução mais simples,

escolha:

> **a solução mais simples que preserve as fronteiras corretas.**

Limites completos são aceitáveis. Limites parciais também são, desde que:

- a direção das dependências continue correta;
- dados externos não contaminem os anéis internos;
- a simplificação não esconda regra de negócio no lugar errado.

---

## 2. Como o agente deve trabalhar

### 2.1 Modo socrático — o desenvolvedor escreve o código

O agente **não escreve código de produção por padrão**. O papel dele é:

1. Explicar o conceito arquitetural em jogo.
2. Apontar o arquivo exato e o contrato esperado.
3. Nomear a alternativa descartada e por quê.
4. Revisar o código escrito contra a Dependency Rule e contra este documento.

**Exceções em que o agente pode escrever:**

- **testes que falham (red)**;
- **operações mecânicas**: `git mv`, `Makefile`, `pyproject.toml`,
  `.importlinter`, documentação, `docker-compose.yml`, `template.yaml` (recursos, permissões e ligações, **não** o
  código dos handlers) e scripts do ambiente local em `scripts/`;
- **quando pedido explicitamente**.

### 2.2 Regras de conduta

- Nunca implementar um use case inteiro “para ganhar tempo”.
- Ao revisar, citar a regra violada, não apenas dizer que está errado.
- Ao propor design, sempre apresentar trade-offs.
- Não expandir escopo: uma fatia vertical por vez.
- Não criar abstrações prematuras.
- Não transformar toda recomendação em regra absoluta se houver alternativa válida.

### 2.3 Skills

As skills em `.agents/skills/` estruturam o trabalho de cada fatia (especificação, plano, revisão, testes, segurança). Elas são
**genéricas** — escritas para qualquer stack — e **este documento prevalece sobre elas**.

Regra de conflito: qualquer fase de skill que mande "implementar", "aplicar correções" ou "corrigir" código de produção em `src/`
segue o §2.1. O agente entrega teste vermelho, arquivo, contrato e alternativa descartada; o desenvolvedor escreve o código.

Quais skills usar, quando e com que adaptações: [§13](#13-uso-das-skills). Agentes: [§14](#14-agentes).

#### Onde ficam as skills e os agentes (qualquer harness)

| Caminho | O que é | Quem lê |
|---|---|---|
| `.agents/skills/<nome>/SKILL.md` | **Fonte única** das skills | Codex, GitHub Copilot, Gemini CLI, Cursor, OpenCode (nativamente) |
| `.agents/agents/<nome>.md` | **Fonte única** dos agentes (formato de subagente do Claude Code) | Claude Code, pelo link abaixo; demais harnesses, lendo o arquivo como instrução |
| `.claude/skills` → `../.agents/skills` | Link simbólico | Claude Code, que só descobre skills em `.claude/` |
| `.claude/agents` → `../.agents/agents` | Link simbólico | Claude Code, que só descobre agentes em `.claude/` |

- **Edite só em `.agents/`.** Os caminhos em `.claude/` são links, não cópias: não edite por eles e não os troque por
  cópias.
- Skill ou agente novo nasce em `.agents/` e já fica visível para todos os harnesses.
- **Harness que não descobre skills ou agentes sozinho** (ou clone sem suporte a links simbólicos): quando a tarefa
  corresponder à descrição de uma skill (§13) ou de um agente (§14), abra o arquivo em `.agents/` e siga as instruções
  dele.

---

## 3. Decisões arquiteturais fixadas

| # | Decisão | Tipo | Razão |
|---|---|---|---|
| D1 | **Result Pattern nos use cases de aplicação** | Convenção do projeto | Fluxo de erro explícito no retorno |
| D2 | **Entidades ricas que levantam exceção de invariante** | Baseado no livro + convenção | A regra crítica mora no anel mais interno |
| D3 | **Ports em `application/ports/`** | Baseado no livro | O contrato pertence ao caso de uso que precisa dele |
| D4 | **Os quatro anéis são conceituais antes de serem físicos** | Baseado no livro | O livro trata os círculos como esquemáticos |
| D5 | **`Event` é o agregado raiz** | Decisão de domínio | Fronteira única de consistência para categorias e reservas |
| D6 | **Estoque = `capacity` + `reserved` + `sold`** | Decisão de domínio | Semântica explícita e auditável |
| D7 | **Dados que cruzam limites são simples e independentes** | Baseado no livro | Nada de entidade, row model, schema de framework ou `dict` cru atravessando fronteiras internas |
| D8 | **`pydantic`, `pydynox`, `boto3` e afins ficam fora de `domain/` e `application/`** | Convenção do projeto alinhada ao livro | Não acoplar regras centrais a detalhes externos |
| D9 | **TDD no núcleo, teste depois na infraestrutura** | Convenção do projeto alinhada ao livro | Testabilidade expõe vazamento de dependência |
| D10 | **Fatia vertical por use case** | Baseado no livro + convenção | A arquitetura deve gritar casos de uso |
| D11 | **`import-linter` no `make check`** | Convenção do projeto | Violação de dependência quebra o build |
| D12 | **O handler é o composition root** | Convenção do projeto alinhada ao livro | Concretos são montados na borda mais externa |

### 3.1 Reconciliação entre D1 e D2

D1 e D2 parecem contraditórios. Não são, desde que a regra seja respeitada:

> O use case valida o caminho previsto e devolve `Err(...)`.
> Se, apesar disso, uma entidade for chamada em estado inválido, isso é bug de programação e a exceção estoura como tal.

Consequência prática:

- **erro de negócio previsto** → `Err(...)`
- **violação de invariante** → exceção de domínio

Duas famílias de erro, com destinos diferentes:

| Família | Onde vive | Tipo | Destino |
|---|---|---|---|
| **Erro de negócio** (`EventNotFound`, `InsufficientReservableQuantity`) | `application/errors/` | valor | Vira `Err(...)` |
| **Violação de invariante** (`InvalidReservationTransition`, `InsufficientStock`) | `domain/exceptions/` | exceção (`DomainException`) | Estoura como bug |

Duas outras exceções completam a hierarquia de `shared/exceptions/` (raiz: `AppException`). Nenhuma delas é fluxo de
negócio:

| Exceção | Quando | Destino |
|---|---|---|
| `ApplicationException` | O use case encontra um estado que as regras tornam impossível (ex.: reserva que aponta para evento inexistente) | Estoura: 500 / retry |
| `InfrastructureException` | Falha técnica de adapter (banco, rede, provedor) | Estoura: 500 / retry |

Quadro completo, com a família de borda: `docs/use_cases.md`, "Famílias de erro".

**Não use `try/except` dentro do use case para controlar fluxo de negócio.**
Se sentiu vontade de fazer isso, faltou validação antes.

---

## 4. Estrutura de diretórios

### 4.1 Estrutura conceitual

Conceitualmente, o projeto tem quatro anéis:

1. **Domain**
2. **Application**
3. **Interface Adapters**
4. **Frameworks & Drivers**

### 4.2 Estrutura física preferida hoje

Neste projeto, a estrutura física **não precisa espelhar literalmente os quatro anéis**. O objetivo é preservar a direção das dependências
com a menor cerimônia viável.

```text
src/ticketstream/
├── shared/
│   ├── result.py
│   ├── use_case.py
│   └── exceptions/
│
├── ticketing/
│   ├── domain/
│   │   ├── entities/
│   │   ├── enumerators/
│   │   ├── exceptions/
│   │   └── services/
│   │
│   ├── application/
│   │   ├── ports/                 # Protocols + outcomes (catálogo em docs/use_cases.md)
│   │   ├── errors/                # erros de negócio (dataclasses), compartilhados entre use cases
│   │   └── use_cases/
│   │       ├── list_events/
│   │       └── list_event_tickets/
│   │           ├── request.py
│   │           ├── response.py
│   │           └── use_case.py    # a união de erros (XError) fica aqui ou em errors.py do pacote
│   │
│   └── infrastructure/
│       ├── entrypoints/
│       │   ├── http/
│       │   │   ├── handlers/
│       │   │   ├── controllers/   # opcional
│       │   │   └── presenters/    # opcional
│       │   └── scheduler/
│       ├── persistence/
│       │   ├── models/
│       │   ├── mappers/
│       │   └── repositories/
│       ├── messaging/             # publishers (saída)
│       └── clients/
│
├── notifications/
│   ├── domain/                    # entities, enumerators, exceptions, services
│   ├── application/               # ports, errors, use_cases
│   └── infrastructure/
│       ├── entrypoints/messaging/ # consumers SQS (entrada)
│       ├── persistence/
│       └── clients/               # adapters SES e SNS
│
└── identity/                      # Etapa 9 — mesma divisão em anéis
```

Os erros de negócio vivem em `application/errors/`, um arquivo por erro, porque vários use cases compartilham o
mesmo erro (ex.: `EventNotFound`). O pacote do use case só guarda a **união** dos erros que ele pode devolver.

### 4.3 Como interpretar essa estrutura

#### `domain/`

Contém regras de negócio e invariantes.

#### `application/`

Contém casos de uso, ports e erros de negócio previstos.

#### `infrastructure/entrypoints/`

Contém o código acionado por gatilhos externos.

No contexto deste projeto:

- o `handler` é sempre o adapter mais externo;
- `controller` e `presenter` são **papéis arquiteturais**, não arquivos obrigatórios;
- só extraia `controllers/` e `presenters/` quando isso melhorar clareza, isolamento ou testabilidade.

#### `infrastructure/persistence/`

Contém detalhes de DynamoDB/pydynox e os mapeamentos para o domínio.

### 4.4 Regra sobre `controllers/` e `presenters`

Controllers e presenters **pertencem conceitualmente** à camada de Interface Adapters.

Neste projeto, porém:

- um **handler fino** pode acumular temporariamente o papel de controller e presenter;
- extraia um `controller` dedicado quando a adaptação da entrada deixar de ser trivial;
- extraia um `presenter` dedicado quando o mapeamento de saída/status HTTP deixar de ser trivial.

**Não crie `controller.py` e `presenter.py` por ritual.**

### 4.5 Fakes e repositórios in-memory

Por padrão, **fakes e repositórios in-memory vivem em `tests/fakes/`**, não no código de produção.

Só mantenha um repositório in-memory em `src/` se ele for realmente um adapter de execução válido para desenvolvimento local ou modo
offline.

---

## 5. A Dependency Rule

Dependências apontam **sempre para dentro**.

### 5.1 Regras conceituais

| Papel                             | Pode importar                                  | Proibido                                                                                |
|-----------------------------------|------------------------------------------------|-----------------------------------------------------------------------------------------|
| `shared/`                         | stdlib                                         | tudo o mais                                                                             |
| `domain/`                         | stdlib, `shared.exceptions`                    | `application`, `infrastructure`, outro bounded context, libs externas                   |
| `application/`                    | stdlib, `shared`, `domain` do próprio contexto | `infrastructure`, outro bounded context, libs externas                                  |
| adapters de entrada/saída         | stdlib, `shared`, `application`, `domain`      | detalhes de persistência e SDKs, a menos que o código seja claramente de infraestrutura |
| infrastructure/frameworks/drivers | tudo                                           | outro bounded context                                                                   |

### 5.2 Regras físicas deste projeto

- `ticketing`, `notifications` e `identity` (Etapa 9) **não se importam**. A ligação entre eles é só por contrato de
  mensagem e pelo token (`docs/architecture.md` §1).
- `domain/` e `application/` **não importam** `boto3`, `pydynox`, `aws_lambda_powertools`, `pydantic`.
- `pydantic` é permitido **somente na borda externa**:
    - schemas HTTP;
    - models de persistência;
    - nunca no núcleo (`domain/`, `application/`).
- `pydynox` e `boto3` ficam restritos à infraestrutura.

### 5.3 Critério correto para decidir pasta

O critério principal **não é** “importa lib externa?”.

O critério principal é:

> **qual é a responsabilidade arquitetural e qual é a razão para mudar?**

Exemplos:

- converter evento HTTP em `Request` do use case → papel de **adapter de entrada**
- mapear `Result` para payload/status HTTP → papel de **adapter de saída**
- falar com DynamoDB/pydynox → **framework/driver**
- definir e proteger regras de reserva → **domínio**

### 5.4 Verificação automática

`make check` executa `lint-imports`.

Contratos mínimos:

1. `domain` não importa `application` nem `infrastructure`
2. `application` não importa `infrastructure`
3. os bounded contexts não se importam entre si (`identity` entra no contrato na Etapa 9)
4. `domain` e `application` não importam `boto3`, `pydynox`, `pydantic`, `aws_lambda_powertools`

Se futuramente houver um pacote físico explícito de `interface_adapters/`, ele ganha contrato próprio.

**Limitação conhecida:** o contrato que restringe o `domain` a `shared.exceptions` é uma lista de **proibição**
(`shared.result`, `shared.use_case`). Todo módulo novo em `shared/` precisa ser acrescentado a essa lista, senão o
domínio passa a poder importá-lo sem o build acusar.

Build vermelho por violação de camada é **feature**, não obstáculo.

---

## 6. Padrões de código

### 6.1 Result

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E


type Result[T, E] = Ok[T] | Err[E]
```

O consumo usa `match`, nunca cadeia de `isinstance`.

### 6.2 Contrato de use case

Para use cases públicos da camada de aplicação, a assinatura preferencial é:

```python
def execute(self, request: XRequest) -> Result[XResponse, XError]: ...
```

Regras:

- `XRequest`, `XResponse` e `XError` são **estruturas simples e independentes**;
- `XRequest` e `XResponse` vivem no pacote do use case;
- `XError` é uma união de erros de negócio;
- nada de `dict[str, Any]` cruzando a fronteira;
- nada de schemas HTTP, models Pydantic, row models ou entidades cruzando a fronteira.

**Observação importante:**
O livro permite que dados cruzem limites como DTOs simples **ou até argumentos de função**. Neste projeto, para use cases públicos,
preferimos `Request/Response` por uniformidade didática. Para helpers internos do mesmo componente, argumentos tipados são aceitáveis se
evitarem cerimônia inútil.

### 6.3 Request/Response

- usar `dataclass(frozen=True, slots=True)` por padrão;
- até request vazio é aceitável;
- não derivar de framework;
- não usar `BaseModel` do Pydantic na aplicação.

### 6.4 Entidades

Imutáveis, com comportamento. Toda transição devolve nova instância.

```python
@dataclass(frozen=True, slots=True)
class TicketCategory:
    ticket_category_id: UUID
    name: str
    base_price: Decimal
    capacity: int
    reserved: int
    sold: int

    @property
    def reservable(self) -> int:
        return self.capacity - self.sold - self.reserved
```

Regras:

- invariantes moram na entidade;
- orquestração mora no use case;
- detalhe externo nunca entra aqui.

### 6.5 Ports / gateways

Ports vivem em `application/ports/` e são definidos pela necessidade do use case.

Regras:

- contratos orientados ao caso de uso;
- sem vocabulário de framework;
- sem retornar models de persistência;
- sem levantar erro de negócio previsto.

Exemplo:

- o port pode devolver `Event | None`;
- quem decide que “não encontrado” vira erro é o use case.

### 6.6 Pydantic e pydynox

#### Permitido

- `pydantic` em schemas HTTP da borda
- `pydantic` em models de persistência
- `pydynox` em `infrastructure/persistence/`

#### Proibido

- `pydantic` em `domain/`
- `pydantic` em `application/`
- `pydynox` fora de `infrastructure/`

### 6.7 Agregado e estoque

`Event` é a raiz. `TicketCategory` é acessada através de `Event`.

Semântica oficial de estoque:

| Campo        | Significado                            | Muda quando                          |
|--------------|----------------------------------------|--------------------------------------|
| `capacity`   | lotação da categoria                   | nunca                                |
| `reserved`   | bloqueado por reservas `PENDING`       | reserva cria/confirma/cancela/expira |
| `sold`       | vendido (`CONFIRMED`)                  | checkout                             |
| `reservable` | derivado: `capacity - sold - reserved` | —                                    |

### 6.8 Concorrência e overbooking

O use case valida regra em memória para o caminho previsto. A garantia de atomicidade é do adapter de persistência.

Logo:

- validação em memória → mensagem de erro e fluxo de negócio;
- condição atômica no banco → prevenção real de overbooking.

As duas são necessárias.

### 6.9 Convenções

- `snake_case`
- ports terminam em `Port`
- dependências privadas com `_`
- dinheiro em `Decimal`
- IDs em `UUID` no núcleo
- datas timezone-aware em UTC
- código e identificadores em inglês
- documentação e conversa em português
- commits em Conventional Commits

---

## 7. Testes

| Camada                           | Disciplina   | Ferramenta      |
|----------------------------------|--------------|-----------------|
| `domain/`                        | **TDD**      | pytest          |
| `application/`                   | **TDD**      | pytest + fakes  |
| adapters extraídos, se existirem | teste depois | pytest          |
| `infrastructure/`                | teste depois | pytest + `moto` |
| sistema implantado (E2E)         | teste depois | pytest + MiniStack (`make test-e2e`) |

Regras:

- testes de `domain` e `application` não podem importar `moto`, `boto3` nem ler env vars;
- prefira fakes em `tests/fakes/` a `unittest.mock`;
- o agente pode escrever o teste vermelho;
- o desenvolvedor escreve a implementação que o faz passar;
- `make check` **não depende de Docker**: unitários e integração (`moto`) rodam sem MiniStack. O E2E fica em
  `make test-e2e` (`docs/requirements.md` DEC-25).

---

## 8. Fluxo de uma fatia vertical

Ordem preferida — de dentro para fora:

0. **FRD e Blueprint da fatia** em `docs/<fatia>/` (`feature-spec-brainstorm` → `feature-blueprint`, §13)
1. **Entidade / regra de domínio** — teste vermelho → implementação
2. **Port** em `application/ports/`
3. **Request / Response / Error** do use case
4. **Use case** — teste vermelho dos ramos `Ok` e `Err`
5. **Fake** em `tests/fakes/`
6. **Schema externo / handler fino**
7. **Extrair controller/presenter se houver ganho real**
8. **Repositório concreto** em infraestrutura + teste de integração
9. **Função no `template.yaml`** + deploy no MiniStack + **teste E2E** (`make local-deploy`, `make test-e2e`)
10. `make check`
11. **Revisão da fatia** (`feature-review`, §13)

A fatia só está pronta quando os três níveis estão verdes: unitário, integração e E2E (`docs/requirements.md` DEC-25).

### 8.1 Controller e presenter são obrigatórios?

**Não.**

Eles são **papéis arquiteturais**, não arquivos obrigatórios.

Crie `controller` dedicado quando:

- parsing/adaptação da entrada crescer;
- a mesma adaptação aparecer em mais de um handler;
- você quiser testá-lo isoladamente.

Crie `presenter` dedicado quando:

- o mapeamento para HTTP ficar não trivial;
- houver formatação relevante;
- múltiplos gatilhos precisarem da mesma saída.

Se o handler ainda for curto e só:

- validar entrada,
- chamar use case,
- devolver resposta,

então **não extraia por ritual**.

### 8.2 Mapeamento de erro → HTTP

Esse mapeamento pertence ao adapter de saída:

- presenter, se existir;
- handler, enquanto ele ainda cumprir esse papel de forma simples.

| Erro de negócio | HTTP |
|---|---|
| `EventNotFound`, `TicketCategoryNotFound`, `ReservationNotFound` | 404 |
| `InvalidReservationQuantity` | 400 |
| `EventAlreadyStarted`, `InsufficientReservableQuantity`, `ConcurrencyConflict`, `ReservationAlreadyConfirmed` (só no cancelamento), `ReservationCancelled`, `ReservationExpired` | 409 |
| `UserReservationLimitExceeded` | 422 |
| `PaymentFailed` | 402 |
| entrada inválida no schema da borda (`InvalidRequest`) | 400 |
| exceção não tratada (`InternalError`) | 500 |

O checkout repetido de reserva já confirmada **não é erro**: devolve 200 (`docs/requirements.md` DEC-29).

**Erros consumidos na SQS (sem HTTP):**
- UC-06: `NotificationProfileNotFound`, `UnsupportedNotificationChannel`, `NotificationDestinationUnavailable` e
  `NotificationRejectedByProvider`. A mensagem é consumida, e a notificação fica `FAILED` (DEC-03).
- UC-11: `NotificationProfileRejected`. A mensagem é consumida, e o perfil **não** é gravado.

Envelope de erro: `docs/contracts.md` §2.3.

**Erros de `identity`** (Etapa 9, DEC-19): `PasswordPolicyViolation`, `InvalidNotificationPreference`,
`InvalidConfirmationCode` e `ConfirmationCodeExpired` → 400; `InvalidCredentials` → 401; `UserNotConfirmed` → 403;
`EmailAlreadyRegistered` e `UserAlreadyConfirmed` → 409.

---

## 9. Comandos

```bash
make setup             # uv sync + instalacao editavel
make format            # ruff format (escreve)
make format-check      # ruff format --check (nao escreve)
make lint              # ruff check
make typecheck         # ty check
make imports           # lint-imports
make test              # pytest tests — a partir da Etapa 1B, com --ignore=tests/e2e
make test-unit         # pytest tests/unit
make test-integration  # pytest tests/integration
make check             # format-check + lint + typecheck + imports + test (nunca exige Docker)

# ambiente local (Etapa 1B em diante; exige Docker e AWS SAM CLI)
make local-up          # sobe o MiniStack (docker compose)
make local-deploy      # implanta o template.yaml no MiniStack
make local-seed        # popula eventos, categorias e perfis de notificação
make test-e2e          # pytest tests/e2e contra o MiniStack
make local-down        # derruba o ambiente
```

`make check` usa `format-check`, nunca `format`: um alvo de verificacao nao muta o
working tree. A configuracao de `ruff`, `ty` e `pytest` vive em `pyproject.toml`.

A regra `ARG` do `ruff` esta desligada de proposito: a unica violacao hoje e o
parâmetro `request` ignorado de `ListEventsUseCase.execute`. **Ligar `ARG` e o gatilho natural
da Etapa 3.** A regra `TC` (flake8-type-checking) tambem esta fora: ela empurraria os
imports de `UUID`, `datetime` e `Event` para blocos `if TYPE_CHECKING:`, escondendo as
dependencias entre aneis justamente onde elas precisam estar visiveis.

---

## 10. Estado atual

**Build vermelho de propósito.** `make check` falha hoje, e isso é esperado: o teste vermelho da Etapa 2
(`tests/unit/ticketing/test_list_event_tickets.py`) importa `list_event_tickets.request` e `.use_case`, que o
desenvolvedor ainda vai escrever. Falham a coleta do pytest e o `ty` (que também verifica `tests/`). O build volta a
ficar verde quando a Etapa 2 for implementada. Nenhum outro vermelho é aceitável.

**Implementado:** estrutura base dos bounded contexts, entidades de `ticketing`
(ainda sem comportamento completo), `ReservationStatus` com máquina de transição,
`EventRepositoryPort` e `ReservationRepositoryPort`, `ListEventsUseCase` (fora do gabarito, dívida 3),
`InMemoryEventRepository`, `shared/result.py`, hierarquia de exceções em `shared/`,
`import-linter` no `make check` com 6 contratos. Testes existentes: `test_reservation_status.py`,
`test_ticket_category.py` e o vermelho `test_list_event_tickets.py`.

**Base de ferramental (fechada):** `[build-system]` explícito com `hatchling`,
configuração de `ruff`, `ty` e `pytest` em `pyproject.toml`, `make format-check`
separado de `make format`.

**Layout de testes.** `tests/` é um **diretório comum, não um pacote**: nenhum
`__init__.py`. A árvore é achatada até o bounded context e tem um arquivo por assunto,
não um por arquivo de produção — o §7 não pede espelhamento. Fakes ficam em
`tests/fakes/` (§7) e construtores de entidade são fixtures-fábrica em
`tests/conftest.py`; a linha `pythonpath = ["."]` no `pyproject.toml` é o que torna
`tests` importável como namespace package. Contrapartida aceita: nomes de arquivo de
teste precisam ser únicos em toda a árvore.

**O que se testa.** Regras de negócio e casos de uso. Não se testa forma de dataclass
(que campos um Response tem, se um `Decimal` continua `Decimal`) nem o comportamento de
um test double — se o fake quebrar, o teste do caso de uso que o usa quebra junto.
Prefira uma função parametrizada que enuncie a regra a várias funções recortando
subcasos dela.

**Resolvido nesta rodada:** o pacote `src/ticketstream/ticketing/adapters/` foi
removido — ele não existia na árvore do §4.2 e hospedava o `InMemoryEventRepository`
contra o §4.5. O fake passou para `tests/fakes/in_memory_event_repository.py` e os
contratos do `import-linter` deixaram de citar `adapters`. Consequência direta: o
handler da Etapa 2 não tem repositório de produção disponível, então o **passo 8 do §8
(repositório DynamoDB + teste de integração com `moto`) deixa de ser opcional na fatia
de referência**.

**Removido por ser placeholder morto:** `infrastructure/clients/dynamodb_client.py`
(instanciava o client no import, com `region=os.getenv("AWS_REGION")` possivelmente
`None` — o composition root é o handler), `persistence/models/event.py` e
`reservation.py` (0 byte) e `DynamoDBEventRepository` (um `pass`). Voltam na fatia que
precisar deles, já no formato correto: o client como factory sem efeito colateral,
recebendo a região como argumento obrigatório.

**Ausente ou ainda não extraído:** handlers, repositório DynamoDB, models/mappers de persistência, parte relevante de `notifications`,
controllers/presenters dedicados.

### Dívidas conhecidas

| #  | Item                                                                               | Quando  |
|----|------------------------------------------------------------------------------------|---------|
| 3  | `ListEventsUseCase` fora da UC-01: recebe `dict[str, Any]` em vez de Request DTO, não devolve `Result`, não tem `ClockPort` nem filtro `end_at > now` (DEC-14), não ordena (DEC-31), usa `EventResponse` em vez de `EventSummary` e não tem teste | Etapa 3 |
| 11 | Entidades sem comportamento: faltam as operações e invariantes de `docs/domain.md` (`Event.reserve/confirm/release`, `Reservation.create/confirm/expire/cancel`, `calculate_total_price`, `Notification.pending/failed/mark_*`) | Etapas 4–7 |
| 13 | `list_events/response.py` usa `@dataclass(frozen=True)` sem `slots=True` em `EventResponse` e `ListEventsResponse`, contra o §6.3 | Etapa 3 |
| 14 | `Event` sem `convenience_fee_percentage` (`docs/domain.md` §2.1, DEC-02) | Etapa 4 |
| 15 | `Reservation` sem `event_id` e `total_price` (`docs/domain.md` §2.3) | Etapa 4 |
| 16 | `Notification` sem `subject`, `failure_reason`, `created_at` e `updated_at`, com `type` e `destination` ainda obrigatórios; `NotificationProfile` inexistente (`docs/domain.md` §3) | Etapa 7 |
| 17 | `ReservationRepositoryPort` com métodos CRUD genéricos (`create`, `update`, `find_by_category_id`, `find_by_user_id`); o catálogo de ports (`docs/use_cases.md`) pede `get_held_quantity`, `find_pending_expired` e `save_new/confirmation/release` → `WriteOutcome` | Etapa 4 |
| 18 | `domain/exceptions/` vazio nos dois contextos: nenhuma exceção de `docs/domain.md` §2.5 e §3.5 existe | Etapa 4 |
| 19 | `ClockPort` e `IdGeneratorPort` inexistentes (DEC-12) | Etapa 3 (clock), Etapa 4 (ids) |
| 20 | Fixture `make_event` (`tests/conftest.py`) usa `start_at = datetime.now(UTC)` sem parâmetro: todo evento já começou (quebra testes de reserva, DEC-15) e o teste depende do relógio. Trocar por um `NOW` fixo, `start_at = NOW + 1 dia` e `start_at`/`end_at`/`convenience_fee_percentage` como parâmetros | Etapa 3 |
| 21 | `make test-integration` roda sobre `tests/integration/` vazio: o pytest sai com código 5 e o alvo falha | Etapa 2 (primeiro teste com `moto`) |
| 22 | `python-dotenv` e `.env` existem mas não são documentados; o §7 proíbe ler env vars no núcleo. Documentar como uso exclusivo de E2E/seed ou remover | Etapa 1B |
| 23 | `make test` roda `pytest tests` e passaria a incluir `tests/e2e/`, exigindo MiniStack no `make check` | Etapa 1B |

### Conflito de regra resolvido

`ReservationStatus.can_transition_to` permitia `CONFIRMED → CANCELLED`, contra a regra de que reserva confirmada
**não pode** ser cancelada. Resolvido no código e em `tests/unit/ticketing/test_reservation_status.py`: `CONFIRMED`,
`CANCELLED` e `EXPIRED` são terminais, e do `PENDING` saem as três transições (`docs/domain.md` §2.3).

---

## 11. Roadmap imediato

- [x] **Etapa 1 — Migração estrutural**
- [ ] **Etapa 1B — Infraestrutura local (MiniStack)** (`docs/requirements.md` DEC-24, `docs/architecture.md` §10) —
      vem **antes** do restante da Etapa 2
    - [ ] teste de viabilidade — **primeiro item**: Python 3.14 no MiniStack, SAM na imagem `full`, transação DynamoDB,
          gatilho SQS → Lambda com DLQ, Scheduler, Cognito e Lambda authorizer. Se o 3.14 falhar, aplicar o plano B da
          DEC-24 — **agente**, com relatório em `docs/local-infrastructure/`
    - [ ] `docker-compose.yml` (skill `docker-advisor`) — **agente**
    - [ ] `template.yaml` esqueleto: tabelas `Ticket` e `Notification`, fila e DLQ, API REST, Scheduler — **agente**
    - [ ] `scripts/local-deploy.sh`, `scripts/seed.py` e alvos `local-*` e `test-e2e` no `Makefile`; `make test` passa a
          ignorar `tests/e2e/` (dívida 23) — **agente**
    - [ ] `tests/e2e/` com um teste de fumaça (MiniStack no ar e tabelas criadas) — **agente**
- [ ] **Etapa 2 — Fatia de referência: `GET /events/{event_id}/tickets`** (UC-02)
    - [ ] FRD enxuto e retroativo — `docs/list-event-tickets/frd-list-event-tickets.md`
          (`feature-spec-brainstorm`) — **agente**
    - [ ] Blueprint — `docs/list-event-tickets/blueprint-list-event-tickets.md`
          (`feature-blueprint`), cobrindo só o que falta — **agente**
    - [x] pacote `application/use_cases/list_event_tickets/` criado
    - [x] teste vermelho do caso de uso escrito em `tests/unit/ticketing/test_list_event_tickets.py`
    - [ ] `request.py`, `response.py`, `use_case.py` (a união de erros no próprio pacote) — **desenvolvedor**
    - [ ] handler fino em `infrastructure/entrypoints/http/handlers/`, acumulando os
          papéis de controller e presenter (§4.4, §8.1) — **desenvolvedor**
    - [ ] repositório DynamoDB + models/mappers + teste com `moto` — **desenvolvedor**
    - [ ] função no `template.yaml` (**agente**) + teste E2E no MiniStack (**agente**, teste vermelho)
    - [ ] revisão da fatia (`feature-review`) + `security-review` leve do handler — **agente**
- [ ] **Etapa 3 — `GET /events` migrado para o gabarito**
- [ ] **Etapa 4 — `POST /events/{event_id}/reservations`**
- [ ] **Etapa 5 — `POST /reservations/{id}/checkout`**
- [ ] **Etapa 6 — `ExpirePendingReservations`**
- [ ] **Etapa 7 — bounded context `notifications`**
- [ ] **Etapa 8 — Deploy na AWS real, rate limiting, calibração de capacidade e observabilidade**
      (`docs/requirements.md` DEC-18, DEC-22). SAM e DLQ já existem desde a Etapa 1B. Aqui entra o que o MiniStack
      não valida (`docs/architecture.md` §10.1).
- [ ] **Etapa 9 — Segurança: contexto `identity` com Cognito (`/auth/register`, `/auth/confirm`, `/auth/login`),
      Lambda authorizer pelo JWKS, propriedade da reserva, API key + usage plan e WAF** (`docs/requirements.md` DEC-19
      a DEC-21, DEC-23, DEC-28; questões QA-09 e QA-10). Inclui os contratos de `identity` no `.importlinter`.
      **Só começa com o enunciado inteiro funcionando.**

### Regra de execução do roadmap

Cada etapa deve:

1. preservar a Dependency Rule;
2. manter domínio e aplicação livres de detalhes externos;
3. adicionar o mínimo de estrutura necessário;
4. extrair controller/presenter apenas quando a fatia justificar;
5. deixar o build verde com `make check`.

---

## 12. Regra final para o agente

Se houver dúvida entre:

- uma solução mais formal; e
- uma solução mais simples,

escolha a mais simples **desde que**:

- o domínio continue puro;
- a aplicação continue isolada;
- os detalhes externos continuem fora;
- os dados cruzem limites como estruturas simples e independentes.

Em resumo:

> **Melhor uma arquitetura simples com dependências corretas do que uma arquitetura cerimonial com camadas inúteis.**

---

## 13. Uso das skills

As skills vivem em `.agents/skills/`. São genéricas por desenho; esta seção fixa **como** elas se aplicam a este projeto. Onde a skill
e este documento divergirem, vale este documento (§2.3).

### 13.1 Pipeline por fatia vertical

```text
feature-spec-brainstorm → feature-blueprint → feature-development → feature-review
                                   │                    │
                                   └── business-logic-hardening (quando houver invariante/máquina de estados)
                                                        └── feature-test-hardening (quando a cobertura pedir reforço)
```

- **Um diretório por fatia:** `docs/<fatia>/`, em kebab-case e inglês, com o mesmo nome do pacote do use case
  (`list_event_tickets` → `docs/list-event-tickets/`). O conteúdo é em português (§6.9).
- Os artefatos seguem os nomes das skills: `frd-<fatia>.md`, `blueprint-<fatia>.md`, `review-<fatia>.md`,
  `hardening-<fatia>.md`, `test-report-<fatia>.md`, `security-report-<fatia>.md`, `e2e-report-<fatia>.md`.

### 13.2 Adaptações obrigatórias por skill

| Skill | Quando | Adaptação a este projeto |
|---|---|---|
| `feature-spec-brainstorm` | Início de cada fatia | Entradas: `docs/use_cases.md`, `docs/domain.md`. **Não reabrir** o que o §3, o §6.7 e o §8.2 já decidiram. Cada RN do FRD é marcada como **invariante** (candidata a `domain/exceptions/`) ou **erro de negócio previsto** (candidata a `Err`), conforme o §3.1. |
| `feature-blueprint` | Após o FRD aprovado | Fases e tarefas seguem **a ordem do §8** (de dentro para fora). Cada T-XXX ganha o campo **Autor: agente \| desenvolvedor** conforme o §2.1 — teste vermelho, fake, `.importlinter`, `Makefile` e docs são do agente; entidade, use case, handler e repositório são do desenvolvedor. Testes planejados seguem o §7 (TDD no núcleo, `moto` na infraestrutura, fakes em vez de `unittest.mock`). O Blueprint declara os contratos do `import-linter` tocados e se controller/presenter serão extraídos, com justificativa pelo §8.1 — o default é **não extrair**. |
| `feature-development` | Por tarefa do Blueprint | A Fase 2 (plano) vale como está. **A Fase 3 muda:** em tarefa de autor "desenvolvedor", o agente escreve o teste vermelho, aponta arquivo e contrato, nomeia a alternativa descartada e **para**. A Fase 4 roda `make check` sobre o código do desenvolvedor e revisa contra a Dependency Rule, citando a regra violada (§2.2). |
| `feature-review` | Fim da fatia | Acrescentar um **Eixo 0 — Arquitetura** antes dos demais: Dependency Rule, D1–D12, §3.1 (sem `try/except` controlando fluxo de negócio), §6.2 (sem `dict`, entidade ou pydantic cruzando a fronteira) e `make check` como evidência. A Fase 5 **só recomenda** — quem aplica é o desenvolvedor. Não apontar ausência de teste de forma de dataclass (§10, "O que se testa"). |
| `business-logic-hardening` | Etapa 4 e dívida 11 | Especificação formal: `docs/use_cases.md` + o "Conflito de regra resolvido" do §10 (estados terminais). Violação de transição/invariante → exceção de domínio; pré-condição prevista → `Err` (§3.1). O agente escreve os testes vermelhos; o desenvolvedor implementa. |
| `feature-test-hardening` | Após `feature-development` ou `feature-review` | Test doubles = **fakes em `tests/fakes/`**; não sugerir `unittest.mock`. "Seeds" = fixtures-fábrica em `tests/conftest.py`. Respeitar o layout de testes do §10 (sem `__init__.py`, um arquivo por assunto, nomes únicos). O agente pode escrever testes; bug revelado por teste é sinalizado e corrigido pelo desenvolvedor. |
| `reverse-engineering` | Ao fechar cada Etapa, ou antes de migrar código legado | Audita `docs/*.md` contra o código. Só reporta; achados alimentam [Dívidas conhecidas](#dívidas-conhecidas). |
| `security-review` | A partir do primeiro handler; completa na Etapa 9 | Foco serverless: validação pydantic na borda, IDOR em reservas por usuário, condição atômica do DynamoDB contra overbooking (§6.8), IAM de menor privilégio no SAM, nada de stack trace no 500. Correções seguem o §2.1. |
| `e2e-flow-test` | Fluxos de várias etapas, a partir da Etapa 5 | E2E aqui é **o sistema implantado no MiniStack**, chamado por HTTP, SQS ou Scheduler — não há frontend. O E2E de cada fatia é o passo 9 do §8. Esta skill cobre fluxos que atravessam fatias: reservar → checkout (Etapa 5); reservar → expirar (Etapa 6); reservar → checkout → notificação (Etapa 7). Usa `tests/e2e/` e `make test-e2e` (Etapa 1B). |
| `synthetic-data-generation` | Só após o repositório DynamoDB existir | `faker` como dependência de dev; seed idempotente e fora de `src/`. |
| `docker-advisor` | Etapa 1B, e ao mexer no ambiente local | Aplica-se ao `docker-compose.yml` do MiniStack (imagem, porta, persistência de estado, healthcheck). Não se aplica ao runtime: as Lambdas não são containers próprios. |
| `scaffolding-brainstorm`, `scaffolding-blueprint`, `scaffolding-development`, `scaffolding-review` | **Não usar** | A Etapa 1 está concluída e `scaffolding-brainstorm` sobrescreveria este `AGENTS.md`. Mudança de ferramental é operação mecânica (§2.1). |

### 13.3 Mapa Etapa → skills

| Etapa | Skills |
|---|---|
| 1B — infraestrutura local | `docker-advisor` para o compose; relatório do teste de viabilidade em `docs/local-infrastructure/` |
| 2 — `GET /events/{event_id}/tickets` | FRD e Blueprint enxutos e retroativos → `feature-development` nas tarefas restantes → `feature-review` → `security-review` leve do handler |
| 3 — `GET /events` | `reverse-engineering` do `ListEventsUseCase` atual (dívidas 3 e 13) → `feature-blueprint` → `feature-development` → `feature-review` |
| 4 — reservas | `feature-spec-brainstorm` → `feature-blueprint` → `business-logic-hardening` (dívida 11, estados terminais) → `feature-development` → `feature-review` → `feature-test-hardening` |
| 5 — checkout | pipeline completo + `e2e-flow-test` (reservar → checkout) |
| 6 — expiração | pipeline completo + `e2e-flow-test` (reservar → expirar) |
| 7 — `notifications` | pipeline completo em `docs/<fatia>/` próprio; nada importa `ticketing` |
| 8 — AWS real, rate limiting, capacidade | `synthetic-data-generation` para a massa do teste de carga |
| 9 — segurança (`identity`, Cognito) | pipeline completo em `docs/<fatia>/` próprio + `security-review` completa |

### 13.4 Regras de uso

- **Uma skill por vez, uma fatia por vez** (§2.2). O agente não emenda uma skill na seguinte sem pedido.
- Os artefatos das skills (FRD, Blueprint, relatórios) são documentação: o agente os escreve.
- As fases de aprovação das skills ("Posso implementar?") continuam valendo — elas combinam com o §2.1.
- Se um FRD ou Blueprint contradisser este documento, vale este documento, e a divergência entra em
  [Dívidas conhecidas](#dívidas-conhecidas).

---

## 14. Agentes

Os subagentes do projeto vivem em `.agents/agents/`. Cada um cumpre um papel do §8 e aplica as skills do §13. O
catálogo, o fluxo e como carregá-los no Claude Code estão em
[`.agents/agents/README.md`](.agents/agents/README.md).

| Agente | Papel | Pode escrever em |
|---|---|---|
| `slice-planner` | FRD e Blueprint da fatia | `docs/<fatia>/` |
| `test-writer` | Testes vermelhos, fakes, fixtures e E2E | `tests/` |
| `socratic-mentor` | Guia o desenvolvedor na implementação (§2.1) | — |
| `local-infra-engineer` | MiniStack, `template.yaml`, `samconfig`, `scripts/`, `Makefile` | arquivos mecânicos do §2.1 |
| `architecture-reviewer` | Revisão contra a Dependency Rule e as especificações | relatório em `docs/<fatia>/` |
| `security-reviewer` | Revisão de segurança serverless | relatório em `docs/<fatia>/` |
| `docs-auditor` | Coerência código × docs e docs × docs | — (só relatório) |

**Nenhum agente escreve código de produção em `src/`.** As regras deste documento valem para eles como valem para
qualquer agente, e este documento prevalece sobre as instruções de cada um.
