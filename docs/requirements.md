# Requisitos, decisões e backlog

Este documento liga o enunciado ([`project_base.md`](project_base.md)) ao que será construído. Cada pedido vira um
`REQ`, cada interpretação vira um `DEC` e o que fica para depois vira `EXT`. Em cada `REQ`, **Onde** aponta o documento
e o item que o atende.

---

## 1. Escopo

Dois bounded contexts, sem dependência de código entre eles:

- **`ticketing`**: consulta de eventos, reserva temporária de ingressos e checkout.
- **`notifications`**: serviço genérico que recebe um comando de envio e o roteia para o canal (e-mail, SMS, push).
  Não tem endpoint público: é acionado apenas pela fila SQS.

A comunicação entre os dois é **exclusivamente assíncrona**, por mensagem SQS com contrato versionado
([`contracts.md` §3](contracts.md#3-mensagem-sqs-sendnotification)).

Um terceiro contexto, **`identity`** (cadastro e login sobre o Amazon Cognito), entra na etapa de segurança
([DEC-19](#dec-19--autenticação-com-cognito-no-contexto-identity)).

**Ordem de construção:**

1. **Infraestrutura local pronta primeiro**, no MiniStack ([DEC-24](#dec-24--infraestrutura-local-primeiro-com-ministack)).
2. **Cada caso de uso de ponta a ponta**, em TDD ([DEC-25](#dec-25--ciclo-de-uma-fatia-e-pirâmide-de-testes)), até todo o
   enunciado funcionar.
3. **Por último, a camada de segurança** (Cognito, API key e WAF), que fica fora do enunciado
   ([DEC-23](#dec-23--segurança-por-último)).

---

## 2. Requisitos do enunciado

Classificação: **Obrigatório** foi pedido explicitamente. **Derivado** não foi pedido, mas é necessário para atender um
requisito obrigatório. **Refinamento** foi adicionado por modelagem de domínio e adotado.

### 2.1 Funcionais

| ID | Requisito | Classe | Onde |
|---|---|---|---|
| REQ-01 | `GET /events` lista os eventos disponíveis e a quantidade de ingressos restantes | Obrigatório | [UC-01](use_cases.md#uc-01--listevents) |
| REQ-02 | `GET /events/{event_id}/tickets` lista as categorias de ingresso e os preços de um evento | Obrigatório | [UC-02](use_cases.md#uc-02--listeventtickets) |
| REQ-03 | `POST /events/{event_id}/reservations` bloqueia ingressos temporariamente | Obrigatório | [UC-03](use_cases.md#uc-03--createreservation) |
| REQ-04 | `POST /reservations/{reservation_id}/checkout` efetiva a compra, simula o pagamento e dispara a notificação de sucesso | Obrigatório | [UC-04](use_cases.md#uc-04--checkoutreservation) |
| REQ-05 | O motor de notificação roteia o comando para o canal correto (e-mail, SMS, push) | Obrigatório | [UC-06](use_cases.md#uc-06--processnotification) |
| REQ-06 | Duas pessoas não podem comprar o mesmo estoque ao mesmo tempo (anti-overbooking) | Obrigatório | [UC-03](use_cases.md#uc-03--createreservation), [persistence §4](persistence.md#4-escritas-atômicas) |
| REQ-07 | O valor total pode aplicar taxa de conveniência pela fórmula do enunciado | Obrigatório ([DEC-02](#dec-02--taxa-de-conveniência-pela-fórmula-literal)) | [domain §2.4](domain.md#24-preço) |
| REQ-08 | A reserva é temporária: um lock não confirmado expira e devolve o estoque | Derivado de REQ-03 | [UC-05](use_cases.md#uc-05--expirependingreservations) |
| REQ-09 | Cada usuário tem um limite de ingressos por evento | Refinamento | [UC-03](use_cases.md#uc-03--createreservation), [DEC-11](#dec-11--limite-por-usuário-soma-quantidades) |

### 2.2 Arquiteturais e de infraestrutura

| ID | Requisito | Onde |
|---|---|---|
| REQ-10 | API Gateway com rate limiting | [architecture §3](architecture.md#3-componentes) |
| REQ-11 | Lambda usando recursos de concorrência | [architecture §3](architecture.md#3-componentes) |
| REQ-12 | DynamoDB com escrita condicional (*Conditional Puts*) | [persistence §4](persistence.md#4-escritas-atômicas) |
| REQ-13 | SQS como buffer: o ticketing publica e o notifications consome de forma controlada | [contracts §3](contracts.md#3-mensagem-sqs-sendnotification), [architecture §4](architecture.md#4-fluxos) |
| REQ-14 | SES para e-mail e SNS para SMS/push | [architecture §3](architecture.md#3-componentes) |
| REQ-15 | Uma tabela por domínio: `Ticket` e `Notification`, com as chaves do enunciado | [persistence](persistence.md) |
| REQ-16 | DLQ: depois de X tentativas, a mensagem vai para uma fila de análise manual | [architecture §5](architecture.md#5-resiliência) |
| REQ-17 | Infraestrutura como código com AWS SAM (`template.yaml`) | [architecture §7](architecture.md#7-infraestrutura-como-código) |

### 2.3 Conceitos a praticar

| ID | Requisito | Onde |
|---|---|---|
| REQ-18 | Camadas puras: entities e use cases sem `boto3` nem biblioteca web; adapters na borda | `AGENTS.md` §5 |
| REQ-19 | Inversão de dependência: o use case recebe contratos no `__init__` | `AGENTS.md` D3, D12 |
| REQ-20 | Strategy para o canal de envio, sem cadeia de `if/else` | [UC-06](use_cases.md#uc-06--processnotification) |
| REQ-21 | Adapter para os provedores de e-mail e SMS | [architecture §3](architecture.md#3-componentes) |
| REQ-22 | Decorator para logs | [architecture §6](architecture.md#6-observabilidade) |
| REQ-23 | Result Pattern para interromper fluxos de negócio; tradução para HTTP apenas na borda | `AGENTS.md` D1, §3.1, §8.2 · [contracts §2](contracts.md#2-api-http) |
| REQ-24 | Testes unitários do núcleo puro e testes de integração com `moto` | `AGENTS.md` §7 |
| REQ-25 | Bounded contexts isolados, reutilizáveis por outras equipes | `AGENTS.md` §5.2 · [contracts §3](contracts.md#3-mensagem-sqs-sendnotification) |

---

## 3. Decisões

Cada decisão traz o que foi decidido, o motivo e, quando houver, a divergência em relação ao enunciado.

### DEC-01 — UUID em todos os identificadores

`event_id`, `ticket_category_id`, `reservation_id`, `user_id` e `notification_id` são UUID, tanto no domínio quanto nos
contratos.

- O body da reserva usa `ticket_category_id` (UUID) no lugar de `ticket_category` (nome).
- Origem do `user_id`, em duas fases ([DEC-23](#dec-23--segurança-por-último)):
  - **até a Etapa 9**, vem no body da reserva, como no enunciado;
  - **a partir da Etapa 9**, vem do token do Cognito (claim `sub`, que é UUID) e sai do body
    ([DEC-19](#dec-19--autenticação-com-cognito-no-contexto-identity)).
- **Divergência:** o body do enunciado (`{"user_id": "123", "ticket_category": "camarote", "quantity": 1}`) é tratado
  como ilustrativo. O body efetivo é `{"user_id": "<uuid>", "ticket_category_id": "<uuid>", "quantity": 1}` e, a
  partir da Etapa 9, `{"ticket_category_id": "<uuid>", "quantity": 1}`.

### DEC-02 — Taxa de conveniência pela fórmula literal

```text
V_total = (V_base × Q) + (V_base × T / 100)
```

- `T` é o atributo `convenience_fee_percentage` do evento, com `0 ≤ T ≤ 100`. Com `T = 0`, não há taxa.
- O arredondamento é feito em 2 casas, `ROUND_HALF_UP`, só no resultado final.
- O total é calculado **na criação da reserva** e gravado em `total_price`. O checkout cobra exatamente esse valor, e o
  preço que o usuário viu não muda até o pagamento.
- **Observação:** pela fórmula do enunciado, a taxa incide **uma vez sobre o preço unitário**, não sobre `V_base × Q`.
  A fórmula é seguida como está. Trocar por uma taxa por ingresso é uma extensão (EXT-09).

### DEC-03 — Falha permanente ≠ falha transitória na notificação

| Falha | Exemplo | Tratamento |
|---|---|---|
| Permanente | Perfil ausente, canal sem strategy, canal sem destino no perfil, recusa permanente do provedor (`SendOutcome.REJECTED`) | O use case grava `FAILED` e devolve `Err`. A mensagem é consumida, sem retry. Destino em formato inválido é barrado antes, na gravação do perfil (UC-11). |
| Transitória | SES/SNS indisponível, throttling do provedor | Exceção de infraestrutura. A SQS repete e, depois de X tentativas, a mensagem vai para a DLQ. |
| Mensagem malformada | JSON inválido, campo obrigatório ausente, versão desconhecida | O handler rejeita antes do use case. A mensagem esgota as tentativas e vai para a DLQ. |

**Divergência:** o enunciado cita "formato de e-mail inválido" como exemplo de mensagem que chega à DLQ. Aqui, destino
inválido é falha permanente: repetir não muda o resultado. A DLQ fica com o que precisa de análise humana, ou seja,
mensagens malformadas e provedor persistentemente fora.

### DEC-04 — O destino da notificação é resolvido pelo `notifications`

O comando SQS carrega `user_id` e o conteúdo, não o destino. O `notifications` resolve **canal e destino** a partir
do **perfil de notificação** do usuário (`NotificationProfile`, [domain §3.2](domain.md#32-notificationprofile)),
obtido pelo `NotificationProfilePort` e guardado na tabela `Notification`
([persistence §3.2](persistence.md#32-tabela-notification)).

- **Canal:** o `channel` do comando, se vier; senão, o `preferred_channel` do perfil
  ([DEC-26](#dec-26--um-canal-preferido-definido-no-cadastro)).
- **Destino:** o campo do perfil correspondente ao canal (`email` ou `phone_number`).
- **Origem do perfil:** seed até a Etapa 9. Depois, o evento `UserRegistered`
  ([DEC-27](#dec-27--dados-de-usuário-divididos-por-contexto)).
- **Motivo:** a API pública fica igual à do enunciado, e o motor de notificação continua genérico. Quem publica só
  precisa saber *para quem*, não *para onde* nem *por onde*.

### DEC-05 — Estoque em três contadores no domínio e um contador materializado no banco

- O domínio usa `capacity`, `reserved` e `sold`, com `reservable = capacity - sold - reserved`
  ([domain §2.2](domain.md#22-ticketcategory)).
- O DynamoDB **não aceita aritmética em `ConditionExpression`**. Por isso a persistência mantém `available_quantity`
  (o mesmo campo do enunciado) como cópia materializada de `reservable`, atualizada na mesma escrita atômica. A condição
  anti-overbooking é `available_quantity >= :quantity`.

### DEC-06 — Notificação obrigatória apenas no checkout

- O checkout publica `SendNotification` confirmando a compra, **sem escolher o canal**. O canal é a preferência do
  usuário (DEC-04, DEC-26). O `ticketing` não sabe se o aviso sai por e-mail ou por SMS.
- Notificação na criação ou na expiração da reserva fica para extensão (EXT-02).
- **Motivo:** o enunciado exige "disparando a notificação de sucesso" no checkout. Na reserva, o texto diz apenas
  "confirmado (ou reservado)".

### DEC-07 — Falha ao publicar a notificação não desfaz a compra

- Se a confirmação foi gravada e a publicação na SQS falhar, o checkout devolve `Ok` com `notification_published = false`.
  A falha é registrada em log e métrica.
- O port de publicação devolve o resultado como dado simples. O use case não usa `try/except`.
- **Motivo:** a compra é o fato de negócio, e a notificação é consequência. Devolver erro depois de cobrar e confirmar
  levaria o cliente a repetir o checkout.
- **Risco aceito:** a notificação pode se perder. A garantia de entrega pelo padrão transactional outbox fica para
  extensão (EXT-03).

### DEC-08 — Pagamento simulado atrás de um port

- `PaymentGatewayPort.charge(reservation_id, amount)` devolve `PaymentOutcome.APPROVED` ou `DECLINED`
  ([use_cases §Catálogo de ports](use_cases.md#catálogo-de-ports)).
- O adapter de produção é um simulador que aprova sempre. Nos testes, um fake permite forçar a recusa.
- Com pagamento recusado, a reserva continua `PENDING` e pode ser paga de novo até expirar.

### DEC-09 — Tempo de vida da reserva e expiração

- O TTL padrão é **10 minutos**, configurável. O handler lê a configuração e a entrega ao use case. O núcleo não lê
  variável de ambiente.
- Um agendamento no EventBridge Scheduler executa UC-05 **a cada 1 minuto** e devolve o estoque.
- O checkout recusa uma reserva com `expires_at` vencido **mesmo que o job ainda não tenha rodado**. A validade não
  depende do agendamento.

### DEC-10 — Falha técnica não é `Err`

`Err(...)` é reservado a erro de negócio previsto (`AGENTS.md` §3.1). Banco fora, timeout ou exceção inesperada são
exceções de infraestrutura:

- na API HTTP, viram `500` com envelope genérico ([contracts §2.3](contracts.md#23-envelope-de-erro));
- na SQS, provocam retry e, no limite, a DLQ.

Por isso, `UnexpectedError`, `PersistenceError` e `MaxRetriesExceeded` **não** aparecem como erro de caso de uso.

### DEC-11 — Limite por usuário soma quantidades

- O limite `max_tickets_per_user` vale para a **soma das quantidades** das reservas do usuário no evento em `PENDING` e
  em `CONFIRMED`.
- `EXPIRED` e `CANCELLED` não contam.

### DEC-12 — O tempo é uma dependência injetada

- Os use cases que dependem do instante atual (UC-01, UC-03, UC-04, UC-05, UC-06, UC-07, UC-10) recebem um
  `ClockPort`, e o domínio recebe o instante como argumento.
- O use case lê o relógio **uma única vez**, no início do `execute`, e usa esse `now` em todas as regras e condições
  da execução.
- **IDs seguem a mesma regra:** quem cria identificadores (UC-03, UC-04) recebe um `IdGeneratorPort`. O núcleo não
  chama `uuid4()`.
- Nenhum código do núcleo chama `datetime.now()`.
- Todas as datas são timezone-aware em UTC (INV-GL-01).
- **Motivo:** testes determinísticos, sem `freezegun` nem mocks: fakes com relógio fixo e IDs previsíveis.

### DEC-13 — Uma função Lambda por handler

- Cada endpoint, o consumer da SQS e o job de expiração têm função própria no SAM.
- **Motivo:** concorrência reservada, timeout e permissões IAM ficam configuráveis por função. O handler segue sendo o
  composition root (`AGENTS.md` D12).

### DEC-14 — Evento disponível é evento que ainda não terminou

- `GET /events` lista apenas eventos com `end_at > agora`.
- Evento em andamento (`start_at ≤ agora < end_at`) continua listado, mas não aceita reserva (DEC-15).
- Origem: resolve a antiga QA-01.

### DEC-15 — Reserva só antes do início do evento

- Uma reserva só pode ser criada se `agora < start_at`. Caso contrário, o use case devolve `Err(EventAlreadyStarted)`,
  que vira HTTP 409.
- A checagem em memória basta: `start_at` não muda, então não há corrida a proteger no banco.
- Origem: resolve a antiga QA-02.

### DEC-16 — O checkout tolera o início do evento

- A regra de DEC-15 vale **só na criação** da reserva.
- Uma reserva `PENDING` pode ser paga até `expires_at`, mesmo que o evento já tenha começado. O TTL é a tolerância
  máxima para confirmar uma reserva feita a tempo.
- `expires_at` não é limitado por `start_at`.
- Origem: resolve a antiga QA-05.

### DEC-17 — Três tentativas antes da DLQ

- A fila `notifications` usa `maxReceiveCount = 3`: é o "X tentativas" do enunciado
  ([REQ-16](#22-arquiteturais-e-de-infraestrutura)).
- A contagem inclui a primeira entrega. Uma mensagem com falha transitória é processada no máximo 3 vezes e depois vai
  para a `notifications-dlq`.
- Falhas permanentes não consomem tentativas: a mensagem é consumida com `FAILED` já na primeira
  ([DEC-03](#dec-03--falha-permanente--falha-transitória-na-notificação)).
- Origem: resolve a antiga QA-04.

### DEC-18 — Borda HTTP: REST API em camadas

- O tipo é **REST API**, não HTTP API. Só o REST oferece usage plans, integração com WAF, Lambda authorizer com cache e
  throttling por método.
- A **validação de formato** fica só no schema `pydantic` do handler, como fonte única e testável. O API Gateway não
  valida o body.
- **Sem cache** no API Gateway: `reservable_quantity` precisa estar sempre atual, e o cache tem custo fixo por hora.
- Camadas da requisição, com a etapa em que cada uma entra:

```text
Cliente → WAF, por IP (Etapa 9) → API key + usage plan, por aplicação (Etapa 9)
        → Lambda authorizer, por usuário, só nas escritas (Etapa 9)
        → throttling por rota, global (Etapa 8) → Lambda
```

### DEC-19 — Autenticação com Cognito, no contexto `identity`

> **Etapa 9** ([DEC-23](#dec-23--segurança-por-último)). Os detalhes restantes (QA-09 e QA-10) serão fechados com
> `feature-spec-brainstorm` no início da etapa.

**Provedor de identidade**
- O **Amazon Cognito User Pool** guarda os usuários e as senhas, emite os tokens (JWT assinado pelo Cognito, com
  chaves públicas no JWKS do User Pool) e bloqueia tentativas repetidas de login.
- **Não há tabela de usuários no DynamoDB.**
- O `user_id` é a claim `sub` do token, que é UUID e combina com DEC-01.

**Cadastro e login dentro da API: novo bounded context `identity`**
- `identity` é independente de `ticketing` e de `notifications`, com os mesmos anéis e contratos próprios no
  `import-linter`. Autenticação não é regra de venda.
- Os endpoints `POST /auth/register`, `POST /auth/confirm` e `POST /auth/login` chamam o Cognito **do lado do
  servidor**, por trás de um `IdentityProviderPort` em `identity/application/ports/`. O adapter do Cognito fica em
  `identity/infrastructure/`. O login usa `AdminInitiateAuth` (fluxo `ADMIN_USER_PASSWORD_AUTH`) com permissão IAM
  restrita à função.
- Casos de uso: UC-08 `RegisterUser`, UC-09 `AuthenticateUser` e UC-10 `ConfirmRegistration`
  ([DEC-28](#dec-28--confirmação-de-cadastro-por-código)).
- Telefone e canal preferido ficam no Cognito como atributos do usuário, para o UC-10 publicá-los em `UserRegistered`.
- Erros de negócio previstos:

  | Erro | Caso de uso | HTTP |
  |---|---|---|
  | `EmailAlreadyRegistered` | UC-08 | 409 |
  | `PasswordPolicyViolation` | UC-08 | 400 |
  | `InvalidNotificationPreference` | UC-08 (SMS sem telefone) | 400 |
  | `InvalidCredentials` | UC-09 | 401 |
  | `UserNotConfirmed` | UC-09 | 403 |
  | `InvalidConfirmationCode` | UC-10 | 400 |
  | `ConfirmationCodeExpired` | UC-10 | 400 |
  | `UserAlreadyConfirmed` | UC-10 | 409 |

- **Motivo de ter os endpoints na API:** o cliente tem um contrato único, e o fluxo inteiro (cadastro, login e uso do
  token) é validável localmente no MiniStack (DEC-24).
- **Contrapartida:** a senha passa pela Lambda. Mitigações obrigatórias:
  - o corpo das rotas `/auth/*` nunca vai para log;
  - `/auth/login` tem throttling próprio, mais baixo que o das demais rotas;
  - o Cognito já bloqueia tentativas repetidas por conta própria;
  - na Etapa 9, o WAF ganha limite por IP em `/auth/login` (QA-10).

**Proteção das rotas**
- Um **Lambda authorizer** (tipo TOKEN) valida o JWT pelo **JWKS do Cognito** (assinatura, expiração, emissor e
  audiência), com biblioteca consolidada e cache de resultado curto no API Gateway. Ele repassa o `sub` no contexto do
  authorizer.
- **Por que não o Cognito authorizer nativo:** o MiniStack emula Lambda authorizers, mas não há evidência de que aplique
  o authorizer nativo do Cognito. Com o Lambda authorizer, a proteção das rotas se comporta igual no ambiente local e na
  AWS.
- **Rotas públicas:** `GET /events`, `GET /events/{event_id}/tickets` e as rotas `/auth/*`.
  **Rotas autenticadas:** reserva, checkout e cancelamento (EXT-01).
- O handler lê o `user_id` do contexto do authorizer e o entrega ao use case. O núcleo de `ticketing` não sabe que
  existe autenticação: identidade é detalhe da borda.
- **Propriedade da reserva:** checkout e cancelamento só agem sobre reserva do próprio usuário. Reserva de outro
  usuário é tratada como inexistente (`ReservationNotFound`, 404), para não revelar que ela existe.

- Origem: absorve a antiga EXT-05. Resolve QA-06 (contexto `identity`), QA-07 (assinatura e chaves pelo Cognito) e
  QA-08 (senha guardada pelo Cognito).

### DEC-20 — API key e usage plan por aplicação cliente

> **Etapa 9** ([DEC-23](#dec-23--segurança-por-último)).

- **Todas as rotas** exigem o header `x-api-key`. Cada aplicação cliente (front-end, parceiro, teste de carga) tem a
  própria chave, associada a um usage plan com rate, burst e cota mensal.
- **A API key identifica a aplicação, não autentica o usuário.** Em cliente público (web, mobile), a chave não é
  segredo. Quem prova a identidade é o token (DEC-19).

### DEC-21 — WAF no template, com liga/desliga

> **Etapa 9** ([DEC-23](#dec-23--segurança-por-último)).

- Uma Web ACL do AWS WAF associada ao stage traz as regras gerenciadas `AWSManagedRulesCommonRuleSet` e
  `AWSManagedRulesKnownBadInputsRuleSet`, mais uma **regra de limite por IP**.
- O WAF fica atrás do parâmetro SAM `EnableWaf`: `false` em dev, `true` em prod.
- **Motivo:** a proteção fica pronta e versionada sem custo fixo mensal nos ambientes de desenvolvimento.

### DEC-22 — Capacidade: cada camada deixa passar menos que a seguinte aguenta

> **Etapa 8.** Rate limiting é requisito do enunciado (REQ-10, REQ-11) e **não** é adiado para a Etapa 9.

Princípio: `limite do API Gateway ≤ capacidade da Lambda ≤ capacidade do DynamoDB`. O excesso é recusado cedo com um
`429` limpo, e não com timeout ou erro no banco. A correção (não vender além do estoque) é garantida pelas escritas
condicionais, com qualquer volume. Os limites protegem a **vazão**.

**Valores iniciais**, a calibrar no teste de carga da Etapa 8 ([architecture §9](architecture.md#9-capacidade-e-limites)):

| Alvo | rate (req/s) | burst | Lambda |
|---|---|---|---|
| Padrão do stage | 100 | 200 | — |
| `GET /events`, `GET /events/{event_id}/tickets` | 100 | 200 | Sem concorrência reservada |
| `POST /events/{event_id}/reservations` | 50 | 100 | Concorrência reservada 10 |
| `POST /reservations/{reservation_id}/checkout` | 20 | 40 | Concorrência reservada 5 |
| `process_notification` (SQS) | — | — | `MaximumConcurrency = 2` no gatilho SQS, **sem** concorrência reservada |

- A concorrência necessária é estimada por `rps × duração`. Por exemplo, 50 req/s × 0,2 s ≈ 10.
- O consumer da SQS **não** usa concorrência reservada. Com ela, a mensagem recusada por falta de capacidade volta para
  a fila e conta como tentativa: com `maxReceiveCount = 3` (DEC-17), iria para a DLQ sem nunca ser processada.
- Origem: resolve a antiga QA-03.

### DEC-23 — Segurança por último

- DEC-19 (autenticação), DEC-20 (API key) e DEC-21 (WAF) formam a **Etapa 9**. Ela só começa quando todos os
  requisitos do enunciado (REQ-01 a REQ-25) estiverem funcionando, com a Etapa 8 concluída.
- **Até lá**, todas as rotas são públicas, o `user_id` vem no body e não há verificação de propriedade da reserva.
- **Risco aceito temporariamente:** IDOR. Qualquer cliente age em nome de qualquer `user_id`. Não implantar em
  ambiente exposto antes da Etapa 9.
- **O que já deve nascer pronto para a troca:** o `CreateReservationRequest` (UC-03) já tem `user_id`, e só o handler
  decide de onde ele vem. Na Etapa 9, a troca de "body" para "token" mexe apenas na borda, e o use case não muda.
- **O que entra na Etapa 9:** UC-04 e UC-07 ganham o campo `user_id` no `Request` e a regra de propriedade, cada um
  com teste vermelho próprio.
- **Motivo:** o valor do projeto está no que o enunciado pede. Segurança é camada adicional, e construí-la antes
  atrasaria as fatias centrais sem mudar o núcleo.

### DEC-24 — Infraestrutura local primeiro, com MiniStack

> **Etapa 1B**, antes do restante da Etapa 2 (`AGENTS.md` §11).

- O [MiniStack](https://github.com/ministackorg/ministack) (emulador AWS local, licença MIT, porta 4566) roda via
  `docker-compose.yml`, com a imagem **`full`**, a única que aceita templates SAM.
- A infraestrutura fica pronta **antes** dos casos de uso:
  - um `template.yaml` SAM **esqueleto** com tabelas, fila e DLQ, API e Scheduler;
  - script de deploy local e seed.
  - O template cresce **uma função por fatia**.
- **Primeiro item da Etapa 1B: teste de viabilidade.** Confirmar no MiniStack:
  - runtime **Python 3.14** (o `pyproject.toml` exige `>=3.14`);
  - deploy do template SAM;
  - transação condicional do DynamoDB;
  - gatilho SQS → Lambda com redrive para a DLQ;
  - agendamento no EventBridge Scheduler;
  - Cognito (`SignUp`, `ConfirmSignUp`, `AdminInitiateAuth`, JWKS) e Lambda authorizer TOKEN. São da Etapa 9, mas
    confirmar cedo evita surpresa no fim do projeto.
- **Plano B:** se o 3.14 não rodar, baixar `requires-python` para o maior runtime comum ao MiniStack e ao Lambda. O
  código atual exige no mínimo 3.12, por causa de `class Ok[T]` e `type Result`.

**O que cada ambiente valida**

| Validado no MiniStack | Validado só na AWS real (Etapa 8 / 9) |
|---|---|
| DynamoDB e transações, SQS e DLQ, gatilho SQS → Lambda, EventBridge Scheduler, SES, SNS, API Gateway REST → Lambda, Lambda authorizer, Cognito (cadastro, login, JWKS), CloudFormation/SAM | Throttling e usage plans aplicados ao tráfego, bloqueio pelo WAF, cotas reais (concorrência da conta, SES sandbox) |

- **Motivo:** com a infraestrutura pronta, cada fatia é entregue funcionando de ponta a ponta, e os problemas de
  montagem (permissão, variável de ambiente, contrato de evento) aparecem na fatia que os causou, não todos juntos no
  fim.

### DEC-25 — Ciclo de uma fatia e pirâmide de testes

Toda fatia segue o mesmo ciclo, de dentro para fora (`AGENTS.md` §8):

| # | Passo | Ferramenta | Prova que |
|---|---|---|---|
| 1 | Teste unitário **vermelho** do domínio e do caso de uso | pytest + fakes em `tests/fakes/` | A regra está especificada |
| 2 | Implementação até ficar verde | — | A regra existe **sem nenhuma infraestrutura** |
| 3 | Teste de integração do adapter | pytest + `moto` | O adapter fala com o serviço AWS corretamente |
| 4 | Função no `template.yaml` + teste E2E | MiniStack | As peças montadas funcionam juntas |

- `make check` continua **sem Docker** (formato, lint, tipos, imports, unitários e integração). O E2E roda em
  `make test-e2e`, que exige o MiniStack no ar (`make local-up`).
- `moto` e MiniStack não competem. O `moto` testa **um adapter** dentro do pytest, rápido e isolado. O MiniStack testa
  o **sistema implantado**, por HTTP, SQS ou Scheduler.
- **Motivo:** o passo 2 é a prova da Clean Architecture. Se a regra de negócio passa nos testes sem banco, fila nem
  framework, trocar qualquer um deles não a toca.

### DEC-26 — Um canal preferido, definido no cadastro

- Cada usuário tem **um** canal preferido: `EMAIL` ou `SMS`. O padrão é `EMAIL`. Toda notificação vai por esse canal,
  salvo se o comando forçar outro (DEC-04).
- `SMS` como preferência **exige** telefone cadastrado.
- `PUSH` continua no `NotificationType`, mas **não é selecionável no MVP** e **não tem strategy registrada**, porque
  não há token de dispositivo (EXT-10). Um comando que force `PUSH` termina em `UnsupportedNotificationChannel`.
- A preferência é definida **no cadastro** (`POST /auth/register`, UC-08). Alterá-la depois é a EXT-06.
- **Motivo:** uma regra só, fácil de testar. Uma lista de canais ativos multiplicaria os envios por comando e tornaria a
  idempotência por canal. Essa evolução fica prevista na EXT-06.

### DEC-27 — Dados de usuário divididos por contexto

Não há tabela de usuários (DEC-19). Cada contexto guarda **só o que precisa**:

| Contexto | Guarda | Origem |
|---|---|---|
| `identity` (Cognito) | Credenciais, e-mail, confirmação do cadastro | Cadastro (UC-08, UC-10) |
| `ticketing` | **Só o `user_id`**, como referência por identidade: nunca lê nome, e-mail ou telefone, e não faz junção com usuário | Body até a Etapa 9, token depois (DEC-23) |
| `notifications` | `NotificationProfile`: `email`, `phone_number`, `preferred_channel` | Seed até a Etapa 9, evento `UserRegistered` depois |

**Sincronização do perfil**
- Depois que o Cognito confirma o cadastro, o caso de uso `ConfirmRegistration` (UC-10, `identity`) publica
  **`UserRegistered`** por um port de publicação. O gatilho do Cognito não é usado: o caso de uso fica testável em TDD
  e no MiniStack.
- O transporte é **SQS, como no enunciado**: uma fila dedicada `notification-profiles`, com DLQ própria
  ([contracts §4](contracts.md#4-mensagem-sqs-userregistered)). O consumidor é o UC-11 `SyncNotificationProfile`, no
  `notifications`.
- **Por que uma fila separada da `notifications`:** a fila de envio carrega **comandos** e tem concorrência e tentativas
  ajustadas aos limites do SES (DEC-17, DEC-22). A sincronização de perfil é um **fato** com outro ritmo e outro modo
  de falhar. Separadas, uma não disputa vaga com a outra, e cada DLQ fala de um só problema.
- O `notifications` continua **sem endpoint público** (REQ-05): o perfil só chega por mensagem.

**Consequências aceitas**
- O e-mail existe em dois lugares (Cognito e perfil), com **consistência eventual**: entre a confirmação e o consumo do
  evento, uma notificação pode não achar o perfil. Esse caso é falha permanente (`NotificationProfileNotFound`, DEC-03).
- Mudança de e-mail, de telefone ou de preferência, e exclusão de conta (LGPD), não têm fluxo no MVP: EXT-06 e EXT-11.

- Origem: resolve a antiga QA-11.

### DEC-28 — Confirmação de cadastro por código

> **Etapa 9.**

- Depois do cadastro (UC-08), o Cognito envia um código ao e-mail informado. `POST /auth/confirm` (UC-10) recebe
  e-mail e código e chama `ConfirmSignUp`.
- Só depois da confirmação o `identity` publica `UserRegistered`: um perfil de notificação só nasce para e-mail
  comprovadamente do usuário.
- **Motivo:** as notificações vão para esse e-mail. Sem confirmação, qualquer pessoa poderia cadastrar o e-mail de
  outra e direcionar avisos a ela.
- Origem: resolve a antiga QA-12.

### DEC-29 — Checkout idempotente

- Repetir o checkout de uma reserva já `CONFIRMED` devolve **`200` com os dados da confirmação**, sem cobrar e sem
  publicar de novo. `notification_published` vem `null` nessa resposta, porque nada foi publicado nessa chamada.
- O erro `ReservationAlreadyConfirmed` deixa de existir no checkout (continua no cancelamento, UC-07).
- **Motivo:** o caso típico é o cliente que perdeu a resposta por timeout e repete. Com `409`, ele nunca receberia o
  corpo da confirmação.
- **Limite:** vale para repetição **depois** da confirmação. Dois checkouts **simultâneos** ainda podem cobrar os dois
  (risco registrado no UC-04, estorno na EXT-08).
- O POST de **reserva** repetido não é idempotente: cria outra reserva. Risco aceito no MVP (EXT-12).

### DEC-30 — Formato canônico de datas e dinheiro

- **Datas:** `YYYY-MM-DDTHH:MM:SSZ`, em UTC, **com precisão de segundos**, na API, nas mensagens SQS e no DynamoDB. O
  núcleo trunca os microssegundos ao ler o relógio (o fake de relógio já devolve segundos inteiros).
- **Motivo:** as condições e o GSI do DynamoDB comparam datas como texto. Precisões diferentes (`...:00Z` e
  `...:00.123456Z`) quebrariam a ordem. O sufixo `Z`, em vez de `+00:00`, é o que o contrato fixa.
- **Dinheiro:** `Decimal` com 2 casas (`quantize(Decimal("0.01"))`) em toda saída, inclusive valores lidos do banco,
  que podem voltar como `250`.

### DEC-31 — Regras de apresentação e limites operacionais

| Tema | Regra | Onde |
|---|---|---|
| Ordem de `GET /events` | `start_at` crescente; empate por `event_id` | UC-01 |
| Lote da expiração | No máximo 100 reservas por execução (`batch_limit`) | UC-05 |
| Assunto do e-mail | Sem assunto no comando → "Aviso do ticketstream" | domain §3.4 |
| Texto do SMS | Sem assunto; corpo cortado em 160 caracteres, terminando em "…" | domain §3.4 |
| Mensagem de compra | Modelo fixo em pt-BR, com total em reais (`R$ 1.234,56`) | UC-04, regra 7 |
| Campos desconhecidos no body | Ignorados (`extra="ignore"`) | contracts §2 |

### DEC-32 — Divergências de modelagem em relação ao enunciado

| Enunciado | Projeto | Motivo |
|---|---|---|
| `available_quantity` como estoque | `capacity`/`reserved`/`sold` no domínio; `available_quantity` materializado no banco | DEC-05 |
| `MessageBody` (JSON) na tabela `Notification` | `message_body` como texto; `subject` separado | O conteúdo é texto para o usuário. Estrutura extra não tem consumidor. |
| `Status` (`SENT`, `FAILED`) | Acrescenta `PENDING` | Marca a tentativa em andamento e permite repetir o envio com segurança (UC-06, regra 1) |
| `Type` (`EMAIL`, `SMS`) | `EMAIL`, `SMS`, `PUSH` (PUSH sem strategy no MVP) | O enunciado cita push no motor de notificação |
| Body `{"user_id": "123", "ticket_category": "camarote"}` | UUIDs e `ticket_category_id` | DEC-01 |

---

## 4. Questões em aberto

IDs resolvidos não são reaproveitados:
QA-01 virou DEC-14, QA-02 virou DEC-15, QA-03 virou DEC-22, QA-04 virou DEC-17, QA-05 virou DEC-16, QA-06, QA-07
e QA-08 foram resolvidas por DEC-19, QA-11 virou DEC-27 e QA-12 virou DEC-28.

As questões abaixo pertencem à Etapa 9 e **não bloqueiam** as etapas anteriores. Serão fechadas com
`feature-spec-brainstorm` no início da etapa.

| ID | Questão | Proposta |
|---|---|---|
| QA-09 | Tempo de vida dos tokens e uso de refresh | Configuração do App Client: ID/access token de 1 h. `POST /auth/refresh` fica fora do MVP. |
| QA-10 | Proteção contra força bruta no login | Bloqueio nativo do Cognito + throttling próprio de `/auth/login` + limite por IP no WAF para essa rota |

---

## 5. Backlog de extensões

Evoluções previstas, fora do escopo obrigatório. Cada uma entra como fatia vertical própria (`AGENTS.md` §8).

| ID | Extensão | Observação |
|---|---|---|
| EXT-01 | Cancelar reserva pendente, `POST /reservations/{reservation_id}/cancel` | Especificação pronta em [UC-07](use_cases.md#uc-07--cancelreservation-extensão) |
| EXT-02 | Notificar na criação e na expiração da reserva | Reusa o contrato `SendNotification` |
| EXT-03 | Transactional outbox via DynamoDB Streams | Remove o risco aceito em DEC-07 |
| EXT-04 | Paginação em `GET /events` e GSI no lugar de `Scan` | Necessário quando o volume de eventos crescer |
| ~~EXT-05~~ | ~~Autenticação: `user_id` extraído do token~~ | **Absorvida** pela DEC-19 (Etapa 9) |
| EXT-06 | Alterar perfil e preferência depois do cadastro; envio por mais de um canal | Endpoint no `identity`, que publica `UserProfileChanged` para o `notifications` (DEC-26, DEC-27) |
| EXT-07 | Cadastro de eventos e categorias (casos de uso administrativos) | Hoje os eventos entram por seed |
| EXT-08 | Estorno do pagamento quando a confirmação perde a corrida ou há checkout simultâneo | Ver os riscos em [UC-04](use_cases.md#uc-04--checkoutreservation) |
| EXT-09 | Taxa de conveniência por ingresso: `V_base × Q × (1 + T/100)` | Alternativa à fórmula literal de DEC-02 |
| EXT-10 | Push como canal selecionável | Exige registrar o token do dispositivo no perfil (DEC-26) |
| EXT-11 | Exclusão de conta com propagação (LGPD) | `identity` publica `UserDeleted`, e o `notifications` apaga o perfil (DEC-27) |
| EXT-12 | Reserva idempotente com header `Idempotency-Key` | A mesma chave devolve a mesma reserva. Exige item de chave na transação do UC-03 (DEC-29). |
