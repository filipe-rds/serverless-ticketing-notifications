# Contratos externos

Formato exato do que entra e sai do sistema: a API HTTP e as mensagens SQS entre os contextos (`SendNotification` e
`UserRegistered`). Estes contratos pertencem à **borda**: são validados por schemas `pydantic` nos handlers e
convertidos em `Request`/`Response` simples antes de chegar ao núcleo (`AGENTS.md` D7, D8).

---

## 1. Convenções de serialização

| Tipo | Formato JSON | Exemplo |
|---|---|---|
| Identificador | string UUID canônica, minúscula na saída. Na entrada, maiúsculas também são aceitas. | `"3f1c9a6e-8b2d-4c1e-9f0a-2d4b6c8e0a11"` |
| Data e hora | `YYYY-MM-DDTHH:MM:SSZ`: UTC, sufixo `Z`, **sem frações de segundo** ([DEC-30](requirements.md#dec-30--formato-canônico-de-datas-e-dinheiro)) | `"2026-10-01T19:00:00Z"` |
| Dinheiro | **string** decimal com exatamente 2 casas (nunca `number`, para não perder precisão) | `"525.00"` |
| Enumeração | string em maiúsculas | `"PENDING"` |
| Nomes de campo | `snake_case` | `ticket_category_id` |

**Regras dos schemas de entrada** (pydantic, na borda):
- campos desconhecidos são **ignorados** (`extra="ignore"`);
- inteiros são **estritos** (`StrictInt`): `"2"`, `2.0` e `true` são rejeitados com `400 InvalidRequest`;
- a regra de negócio (ex.: `quantity ≥ 1`) **não** vai para o schema: fica no use case, que devolve o erro específico.

---

## 2. API HTTP

Base: API Gateway (REST). Todas as respostas usam `Content-Type: application/json`.

### 2.1 Autenticação e headers

O contrato tem **duas fases** ([DEC-23](requirements.md#dec-23--segurança-por-último)).

**Até a Etapa 9:** todas as rotas são públicas, sem header de autenticação, e o `user_id` vai no body da reserva.

**A partir da Etapa 9:**

| Header | Rotas | Conteúdo | Validado por |
|---|---|---|---|
| `x-api-key` | **Todas** | Chave da aplicação cliente ([DEC-20](requirements.md#dec-20--api-key-e-usage-plan-por-aplicação-cliente)) | API Gateway (usage plan) |
| `Authorization` | Reserva, checkout, cancelamento | `Bearer <IdToken>` emitido pelo Cognito e devolvido por `POST /auth/login` ([DEC-19](requirements.md#dec-19--autenticação-com-cognito-no-contexto-identity)) | Lambda authorizer (JWKS do Cognito) |

| Endpoint | Acesso na Etapa 9 |
|---|---|
| `GET /events` | Público (só API key) |
| `GET /events/{event_id}/tickets` | Público (só API key) |
| `POST /auth/register`, `POST /auth/confirm`, `POST /auth/login` | Público (só API key). Esboço em §2.2. |
| `POST /events/{event_id}/reservations` | Autenticado |
| `POST /reservations/{reservation_id}/checkout` | Autenticado |
| `POST /reservations/{reservation_id}/cancel` | Autenticado (extensão) |

Na Etapa 9, o `user_id` **deixa de vir do body**: o handler o lê do contexto do authorizer (claim `sub` do token). Um
`user_id` no body passa a ser campo desconhecido e não tem efeito.

### 2.2 Endpoints

#### `GET /events` — UC-01

Lista só os eventos que ainda não terminaram (`end_at > agora`, DEC-14), ordenados por `start_at` e depois por
`event_id` (DEC-31). `200 OK`:

```json
{
  "events": [
    {
      "event_id": "3f1c9a6e-8b2d-4c1e-9f0a-2d4b6c8e0a11",
      "name": "Tech Conference 2026",
      "description": "Conferência anual de tecnologia",
      "location": "São Paulo",
      "start_at": "2026-10-01T12:00:00Z",
      "end_at": "2026-10-01T20:00:00Z",
      "reservable_quantity": 150
    }
  ],
  "total": 1
}
```

#### `GET /events/{event_id}/tickets` — UC-02

`200 OK`

```json
{
  "event_id": "3f1c9a6e-8b2d-4c1e-9f0a-2d4b6c8e0a11",
  "categories": [
    { "ticket_category_id": "a1b2c3d4-0000-4000-8000-000000000001", "name": "Camarote", "base_price": "250.00" },
    { "ticket_category_id": "a1b2c3d4-0000-4000-8000-000000000002", "name": "Pista", "base_price": "120.00" }
  ]
}
```

Erros: `404 EventNotFound`.

#### `POST /events/{event_id}/reservations` — UC-03

Request:

```json
{
  "user_id": "7d9e1f20-3a4b-4c5d-8e6f-708192a3b4c5",
  "ticket_category_id": "a1b2c3d4-0000-4000-8000-000000000001",
  "quantity": 2
}
```

| Campo | Tipo | Obrigatório | Validação na borda |
|---|---|---|---|
| `user_id` | UUID | sim, **até a Etapa 9** | UUID válido. Na Etapa 9, sai do body e passa a vir do token (§2.1). |
| `ticket_category_id` | UUID | sim | UUID válido |
| `quantity` | inteiro | sim | Inteiro estrito. A regra `≥ 1` é de negócio e fica no use case. |

`201 Created`

```json
{
  "reservation_id": "c0ffee00-1234-4abc-8def-0123456789ab",
  "status": "PENDING",
  "event_id": "3f1c9a6e-8b2d-4c1e-9f0a-2d4b6c8e0a11",
  "ticket_category_id": "a1b2c3d4-0000-4000-8000-000000000001",
  "user_id": "7d9e1f20-3a4b-4c5d-8e6f-708192a3b4c5",
  "quantity": 2,
  "total_price": "525.00",
  "created_at": "2026-09-24T14:00:00Z",
  "expires_at": "2026-09-24T14:10:00Z"
}
```

Erros: `400 InvalidReservationQuantity`, `404 EventNotFound`, `404 TicketCategoryNotFound`,
`409 EventAlreadyStarted`, `409 InsufficientReservableQuantity`, `409 ConcurrencyConflict`, `422 UserReservationLimitExceeded`.

#### `POST /reservations/{reservation_id}/checkout` — UC-04

Sem body. `200 OK`:

```json
{
  "reservation_id": "c0ffee00-1234-4abc-8def-0123456789ab",
  "status": "CONFIRMED",
  "total_price": "525.00",
  "confirmed_at": "2026-09-24T14:05:00Z",
  "notification_published": true
}
```

**Idempotente** ([DEC-29](requirements.md#dec-29--checkout-idempotente)): repetir o checkout de uma reserva já
confirmada devolve `200` com o mesmo `reservation_id`, `total_price` e `confirmed_at`, e `"notification_published":
null`. Nada é cobrado nem publicado de novo.

Erros: `402 PaymentFailed`, `404 ReservationNotFound`, `409 ReservationCancelled`, `409 ReservationExpired`,
`409 ConcurrencyConflict`.

#### `POST /reservations/{reservation_id}/cancel` — UC-07 (extensão)

Sem body. `200 OK`: `{ "reservation_id": "...", "status": "CANCELLED", "cancelled_at": "..." }`.

Erros: `404 ReservationNotFound`, `409 ReservationAlreadyConfirmed`, `409 ReservationCancelled`,
`409 ReservationExpired`, `409 ConcurrencyConflict`.

#### Rotas `/auth/*` — UC-08 a UC-10 (Etapa 9, esboço)

> Esboço para orientar a Etapa 9. O contrato final sai do FRD da etapa (DEC-19). Estas rotas **nunca** registram o body
> em log, porque ele carrega a senha.

| Rota | Body | Sucesso | Erros de negócio |
|---|---|---|---|
| `POST /auth/register` | `{ "email": "...", "password": "...", "phone_number": "+55...", "preferred_channel": "EMAIL" }` (`phone_number` opcional; `preferred_channel` opcional, padrão `EMAIL`) | `201`: `{ "user_id": "<uuid>", "confirmation_required": true }` | `409 EmailAlreadyRegistered`, `400 PasswordPolicyViolation`, `400 InvalidNotificationPreference` (SMS sem telefone) |
| `POST /auth/confirm` | `{ "email": "...", "code": "123456" }` | `204` | `400 InvalidConfirmationCode`, `400 ConfirmationCodeExpired`, `409 UserAlreadyConfirmed` |
| `POST /auth/login` | `{ "email": "...", "password": "..." }` | `200`: `{ "id_token": "...", "access_token": "...", "expires_in": 3600 }` | `401 InvalidCredentials`, `403 UserNotConfirmed` |

O cliente usa o `id_token` no header `Authorization: Bearer <id_token>` das rotas autenticadas (§2.1).

### 2.3 Envelope de erro

Toda resposta de erro tem o mesmo formato:

```json
{
  "error": {
    "code": "InsufficientReservableQuantity",
    "message": "Não há quantidade disponível para atender a reserva solicitada.",
    "details": { "requested": 3, "reservable": 1 }
  }
}
```

| Campo | Regra |
|---|---|
| `code` | Nome do erro de negócio (`AGENTS.md` §8.2) ou um dos códigos de borda abaixo |
| `message` | Texto em português, para humanos. Não é contrato: o cliente decide pelo `code`. |
| `details` | Opcional. São os campos do erro de negócio, serializados. |

Códigos de borda (não vêm de use case):

| Status | `code` | Quando |
|---|---|---|
| 400 | `InvalidRequest` | Body ou path inválido para o schema (JSON malformado, UUID inválido, campo ausente) |
| 401 | — | *(Etapa 9)* Token ausente, inválido ou expirado numa rota autenticada. A resposta é do API Gateway. |
| 403 | — | *(Etapa 9)* API key ausente ou inválida, ou requisição bloqueada pelo WAF. A resposta é do API Gateway. |
| 429 | — | Throttling da rota (Etapa 8). Na Etapa 9, também limite do usage plan ou cota da API key esgotada. A resposta é do API Gateway. |
| 500 | `InternalError` | Exceção não tratada. **Nunca** expõe stack trace nem mensagem interna. |

---

## 3. Mensagem SQS `SendNotification`

Comando publicado pelo `ticketing` e consumido pelo `notifications`. É a **única** ligação entre esses dois contextos
([REQ-25](requirements.md#23-conceitos-a-praticar)). O `identity` fala com o `notifications` pela mensagem da §4.

**Cada lado mantém a própria representação** deste contrato: o publisher em `ticketing/infrastructure/messaging/` e o
parser em `notifications/infrastructure/entrypoints/messaging/`. Não existe módulo compartilhado. O acoplamento é ao
**formato**, não ao código.

### 3.1 Versão 1

Corpo da mensagem (JSON):

```json
{
  "message_type": "SendNotification",
  "schema_version": 1,
  "notification_id": "5b6c7d8e-9f00-4a1b-8c2d-3e4f5a6b7c8d",
  "user_id": "7d9e1f20-3a4b-4c5d-8e6f-708192a3b4c5",
  "subject": "Compra confirmada — Tech Conference 2026",
  "message_body": "Sua compra de 2 ingresso(s) Camarote para Tech Conference 2026 foi confirmada. Total: R$ 525,00.",
  "correlation_id": "c0ffee00-1234-4abc-8def-0123456789ab",
  "occurred_at": "2026-09-24T14:05:00Z"
}
```

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `message_type` | string | sim | Sempre `"SendNotification"` |
| `schema_version` | inteiro | sim | `1` |
| `notification_id` | UUID | sim | Gerado pelo publicador. **Chave de idempotência** do consumidor. |
| `user_id` | UUID | sim | Destinatário. Canal e destino são resolvidos pelo consumidor a partir do perfil ([DEC-04](requirements.md#dec-04--o-destino-da-notificação-é-resolvido-pelo-notifications)). |
| `channel` | `EMAIL` \| `SMS` \| `PUSH` | **não** | Força um canal. Ausente: vale o canal preferido do usuário ([DEC-26](requirements.md#dec-26--um-canal-preferido-definido-no-cadastro)). O checkout **não** envia este campo. `PUSH` é aceito pelo contrato, mas termina em `FAILED` no MVP (sem strategy). |
| `subject` | string \| null | não | Usado só quando o canal resolvido é `EMAIL`. Ausente: "Aviso do ticketstream" (DEC-31). |
| `message_body` | string | sim | Não vazio. Para SMS, a strategy corta em 160 caracteres (DEC-31). |
| `correlation_id` | string | não | Rastreio ponta a ponta. No checkout, é o `reservation_id`. |
| `occurred_at` | data e hora | sim | Momento em que o comando foi emitido |

### 3.2 Regras de evolução

- **Mudança compatível** (campo opcional novo): mantém `schema_version`. O consumidor **ignora campos desconhecidos**.
- **Mudança incompatível** (remover ou renomear campo, mudar tipo ou semântica): incrementa `schema_version`. O
  consumidor passa a aceitar as duas versões durante a transição.
- Mensagem com `message_type` ou `schema_version` desconhecidos é malformada: vai para a DLQ
  ([DEC-03](requirements.md#dec-03--falha-permanente--falha-transitória-na-notificação)).

### 3.3 Semântica de entrega

A SQS entrega **ao menos uma vez**, e o consumidor precisa tolerar duplicatas. O controle de idempotência por
`notification_id` está no UC-06, regra 1.

---

## 4. Mensagem SQS `UserRegistered`

> **Etapa 9** ([DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)).

**Evento** (um fato, não um comando) publicado pelo `identity` quando um cadastro é confirmado (UC-10) e consumido pelo
`notifications` (UC-11). Viaja na fila dedicada **`notification-profiles`**, com DLQ própria, separada da fila de
comandos de envio (§3). Valem as mesmas regras de evolução (§3.2) e de entrega (§3.3). Cada lado mantém a própria
representação: o publicador em `identity/infrastructure/messaging/` e o parser em
`notifications/infrastructure/entrypoints/messaging/`.

### 4.1 Versão 1

```json
{
  "message_type": "UserRegistered",
  "schema_version": 1,
  "user_id": "7d9e1f20-3a4b-4c5d-8e6f-708192a3b4c5",
  "email": "ana@example.com",
  "phone_number": "+5511987654321",
  "preferred_channel": "SMS",
  "occurred_at": "2026-09-24T13:00:00Z"
}
```

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `message_type` | string | sim | Sempre `"UserRegistered"` |
| `schema_version` | inteiro | sim | `1` |
| `user_id` | UUID | sim | `sub` do Cognito. **Chave** do perfil no consumidor. |
| `email` | string | sim | E-mail confirmado no cadastro |
| `phone_number` | string \| null | não | Formato E.164 |
| `preferred_channel` | `EMAIL` \| `SMS` | sim | Padrão `EMAIL` no cadastro. `SMS` exige `phone_number` (DEC-26). |
| `occurred_at` | data e hora | sim | Momento da confirmação. O consumidor descarta evento mais antigo que o perfil gravado (UC-11). |

**Dados pessoais:** esta mensagem carrega e-mail e telefone. O corpo dela nunca vai para log, nem no publicador nem no
consumidor.
