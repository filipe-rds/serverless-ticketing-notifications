# Casos de uso

Especificação funcional de cada caso de uso: o que recebe, o que valida, **em que ordem**, o que devolve e como falha.
As operações de domínio e as invariantes (`INV-*`) estão em [`domain.md`](domain.md). As decisões (`DEC-*`) estão em
[`requirements.md`](requirements.md). O formato exato de HTTP e SQS está em [`contracts.md`](contracts.md).

## Índice

| ID | Caso de uso | Gatilho | Contexto | Classe | Etapa (`AGENTS.md` §11) |
|---|---|---|---|---|---|
| [UC-01](#uc-01--listevents) | `ListEventsUseCase` | `GET /events` | `ticketing` | Obrigatório | 3 |
| [UC-02](#uc-02--listeventtickets) | `ListEventTicketsUseCase` | `GET /events/{event_id}/tickets` | `ticketing` | Obrigatório | 2 |
| [UC-03](#uc-03--createreservation) | `CreateReservationUseCase` | `POST /events/{event_id}/reservations` | `ticketing` | Obrigatório | 4 |
| [UC-04](#uc-04--checkoutreservation) | `CheckoutReservationUseCase` | `POST /reservations/{reservation_id}/checkout` | `ticketing` | Obrigatório | 5 |
| [UC-05](#uc-05--expirependingreservations) | `ExpirePendingReservationsUseCase` | EventBridge Scheduler | `ticketing` | Derivado | 6 |
| [UC-06](#uc-06--processnotification) | `ProcessNotificationUseCase` | SQS `SendNotification` | `notifications` | Obrigatório | 7 |
| [UC-07](#uc-07--cancelreservation-extensão) | `CancelReservationUseCase` | `POST /reservations/{reservation_id}/cancel` | `ticketing` | Extensão (EXT-01) | backlog |
| [UC-08](#uc-08--registeruser-etapa-9) | `RegisterUserUseCase` | `POST /auth/register` | `identity` | Segurança | 9 |
| [UC-09](#uc-09--authenticateuser-etapa-9) | `AuthenticateUserUseCase` | `POST /auth/login` | `identity` | Segurança | 9 |
| [UC-10](#uc-10--confirmregistration-etapa-9) | `ConfirmRegistrationUseCase` | `POST /auth/confirm` | `identity` | Segurança | 9 |
| [UC-11](#uc-11--syncnotificationprofile) | `SyncNotificationProfileUseCase` | SQS `UserRegistered` | `notifications` | Segurança | 9 |

---

## Famílias de erro

Todo erro pertence a uma família. A família define quem o produz e para onde ele vai (`AGENTS.md` §3.1,
[DEC-10](requirements.md#dec-10--falha-técnica-não-é-err)).

| Família | Produzido por | Forma | Destino HTTP | Destino SQS |
|---|---|---|---|---|
| **Borda** | API Gateway (WAF, API key, authorizer, throttling) ou handler (schema) | Resposta direta | `400`, `401`, `403`, `429` ([contracts §2.3](contracts.md#23-envelope-de-erro)) | Mensagem vai para a DLQ |
| **Negócio** | Use case | `Err(...)` | Conforme `AGENTS.md` §8.2 | Mensagem consumida |
| **Invariante** | Entidade | Exceção de domínio (`DomainException`) | `500` (é bug) | Retry → DLQ |
| **Inconsistência** | Use case, ao encontrar um estado que as regras tornam impossível (ex.: reserva que aponta para evento inexistente) | Exceção de aplicação (`ApplicationException`) | `500` | Retry → DLQ |
| **Técnica** | Adapter | Exceção de infraestrutura (`InfrastructureException`) | `500` | Retry → DLQ |

- As tabelas de erro abaixo listam **só erros de negócio**. As outras famílias valem para todos os casos de uso e não
  são repetidas.
- Os erros de negócio são `dataclass(frozen=True, slots=True)` em `application/errors/`, com os campos indicados entre
  parênteses. Os campos viram o `details` do envelope HTTP.
- **Inconsistência não é fluxo de negócio.** O use case levanta a exceção sem `try/except`; nunca a captura.

## Modelo de caso de uso

Todo caso de uso segue esta estrutura:

1. **Ficha**: objetivo, gatilho, pacote, dependências (ports) e etapa.
2. **Request / Response**: campos com tipo. São `dataclass(frozen=True, slots=True)` (`AGENTS.md` §6.3).
3. **Regras**: numeradas, com referência a `INV`/`DEC`.
4. **Fluxo**: passos em ordem. **A ordem define qual erro vence** quando mais de uma regra falha. `now` é lido uma
   única vez, no primeiro passo.
5. **Erros de negócio**: nome (campos), condição e HTTP (ou destino SQS).
6. **Efeitos**: o que muda no domínio e o que é publicado.

---

## Catálogo de ports

Contratos que os casos de uso exigem da infraestrutura (`AGENTS.md` D3, §6.5). Vivem em `application/ports/` do
contexto que os usa, como `Protocol`. Os tipos auxiliares (outcomes, comandos) ficam no mesmo pacote e são
`dataclass`/`Enum` simples. **Nenhum port levanta erro de negócio**: resultados previstos voltam como valor, e falhas
técnicas são exceções de infraestrutura.

### `ticketing`

| Port | Método | Retorno | Observação |
|---|---|---|---|
| `ClockPort` | `now()` | `datetime` (UTC, com fuso) | O caso de uso lê uma vez por execução |
| `IdGeneratorPort` | `new_id()` | `UUID` | Nos testes, um fake devolve IDs previsíveis |
| `EventRepositoryPort` | `find_by_id(event_id)` | `Event \| None` | AP-02 |
| | `find_all()` | `list[Event]` | AP-01. O adapter lê todas as páginas do Scan. |
| `ReservationRepositoryPort` | `find_by_id(reservation_id)` | `Reservation \| None` | AP-03 |
| | `get_held_quantity(event_id, user_id)` | `int` | AP-04. `0` se não houver registro. |
| | `find_pending_expired(reference_time, limit)` | `list[Reservation]` | AP-05 |
| | `save_new(reservation, max_tickets_per_user)` | `WriteOutcome` | AP-06, transação de [persistence §4.1](persistence.md#41-criar-reserva--uc-03) |
| | `save_confirmation(reservation)` | `WriteOutcome` | AP-07. Usa `reservation.updated_at` como `:now` da condição. |
| | `save_release(reservation)` | `WriteOutcome` | AP-08, para expiração e cancelamento |
| `PaymentGatewayPort` | `charge(reservation_id, amount)` | `PaymentOutcome` | [DEC-08](requirements.md#dec-08--pagamento-simulado-atrás-de-um-port) |
| `NotificationPublisherPort` | `publish(command)` | `bool` | `True` se a mensagem foi aceita pela fila ([DEC-07](requirements.md#dec-07--falha-ao-publicar-a-notificação-não-desfaz-a-compra)) |

Tipos auxiliares: `WriteOutcome = Enum{APPLIED, CONFLICT}`; `PaymentOutcome = Enum{APPROVED, DECLINED}`;
`PurchaseNotificationCommand(notification_id, user_id, subject, message_body, correlation_id, occurred_at)`.

### `notifications`

| Port | Método | Retorno | Observação |
|---|---|---|---|
| `ClockPort` | `now()` | `datetime` (UTC, com fuso) | Um por contexto: os contextos não se importam |
| `NotificationRepositoryPort` | `find(user_id, notification_id)` | `Notification \| None` | AP-09 |
| | `save_pending(notification)` | `WriteOutcome` | AP-10. `CONFLICT` se já existe em estado final. |
| | `save_final(notification)` | `WriteOutcome` | AP-10. Grava `SENT` ou `FAILED` a partir de `PENDING`, ou cria já `FAILED`. |
| `NotificationProfilePort` | `find(user_id)` | `NotificationProfile \| None` | AP-11. Devolve entidade já validada. |
| | `save_if_newer(profile)` | `bool` | AP-12. `False` se o perfil gravado é igual ou mais novo. |
| `NotificationStrategyPort` | `send(destination, subject, message_body)` | `SendOutcome` | Uma implementação por canal ([domain §3.4](domain.md#34-strategy-de-envio)). Falha transitória do provedor é exceção. |

Tipo auxiliar: `SendOutcome = SENT | REJECTED(reason: str)`. `REJECTED` é recusa **permanente** do provedor (ex.: SES
`MessageRejected`, número inválido no SNS).

### `identity` *(Etapa 9, esboço)*

| Port | Métodos |
|---|---|
| `IdentityProviderPort` | `sign_up(email, password, phone_number)`, `confirm_sign_up(email, code)`, `authenticate(email, password)` — cada um devolve um outcome simples, nunca exceção de negócio |
| `UserRegisteredPublisherPort` | `publish(event) -> bool` |

---

## UC-01 — ListEvents

| | |
|---|---|
| Objetivo | Listar os eventos disponíveis e quantos ingressos ainda podem ser reservados em cada um (REQ-01) |
| Gatilho | `GET /events` |
| Pacote | `ticketing/application/use_cases/list_events/` |
| Dependências | `EventRepositoryPort`, `ClockPort` |
| Etapa | 3 |

**Request** — `ListEventsRequest`: sem campos.

**Response** — `ListEventsResponse`

| Campo | Tipo | Regra |
|---|---|---|
| `events` | `tuple[EventSummary, ...]` | Um item por evento disponível, na ordem da regra 4 |
| `total` | `int` | `len(events)` |

`EventSummary`: `event_id`, `name`, `description`, `location`, `start_at`, `end_at` e
`reservable_quantity: int`, que é a soma de `reservable` das categorias do evento.

**Regras**

1. É uma consulta: não altera estado.
2. Só entram eventos com `Event.is_listed(now)` (`now < end_at`). Evento em andamento continua listado
   ([DEC-14](requirements.md#dec-14--evento-disponível-é-evento-que-ainda-não-terminou)).
3. Evento sem categorias aparece com `reservable_quantity = 0`.
4. Ordem: `start_at` crescente e, no empate, `event_id` ([DEC-31](requirements.md#dec-31--regras-de-apresentação-e-limites-operacionais)).

**Fluxo:** ler `now` → buscar os eventos → manter os listados → ordenar → montar os resumos → `Ok`.

**Erros de negócio:** nenhum.

**Efeitos:** nenhum.

---

## UC-02 — ListEventTickets

| | |
|---|---|
| Objetivo | Listar as categorias de ingresso e os preços de um evento (REQ-02) |
| Gatilho | `GET /events/{event_id}/tickets` |
| Pacote | `ticketing/application/use_cases/list_event_tickets/` |
| Dependências | `EventRepositoryPort` |
| Etapa | 2 |

**Request** — `ListEventTicketsRequest`

| Campo | Tipo | Origem |
|---|---|---|
| `event_id` | `UUID` | Path |

**Response** — `ListEventTicketsResponse`

| Campo | Tipo |
|---|---|
| `event_id` | `UUID` |
| `categories` | `tuple[TicketCategorySummary, ...]` |

`TicketCategorySummary`: `ticket_category_id: UUID`, `name: str`, `base_price: Decimal`.

**Regras**

1. As categorias são devolvidas na ordem em que estão no evento.
2. Evento sem categorias → `Ok` com `categories = ()`. Não é erro.
3. O preço exibido é `base_price`. A taxa de conveniência aparece no total da reserva (UC-03).
4. **Não depende do tempo:** um evento encerrado continua consultável. Quem filtra por disponibilidade é o UC-01.

**Fluxo:** buscar o evento por `event_id` → se não existir, `EventNotFound` → montar os resumos → `Ok`.

**Erros de negócio**

| Erro | Condição | HTTP |
|---|---|---|
| `EventNotFound(event_id)` | Não existe evento com o `event_id` | 404 |

**Efeitos:** nenhum.

---

## UC-03 — CreateReservation

| | |
|---|---|
| Objetivo | Bloquear ingressos de uma categoria por tempo limitado (REQ-03, REQ-06, REQ-09) |
| Gatilho | `POST /events/{event_id}/reservations` |
| Pacote | `ticketing/application/use_cases/create_reservation/` |
| Dependências | `EventRepositoryPort`, `ReservationRepositoryPort`, `ClockPort`, `IdGeneratorPort` e `reservation_ttl: timedelta` (configuração) |
| Etapa | 4 |

`reservation_ttl` é recebido no `__init__` e precisa ser `> 0`. Caso contrário, o construtor levanta `ValueError`: é
erro de configuração no composition root, não de negócio.

**Request** — `CreateReservationRequest`

| Campo | Tipo | Origem |
|---|---|---|
| `event_id` | `UUID` | Path |
| `user_id` | `UUID` | Body até a Etapa 9; depois, token ([DEC-23](requirements.md#dec-23--segurança-por-último)) |
| `ticket_category_id` | `UUID` | Body |
| `quantity` | `int` | Body. A borda exige inteiro estrito; a regra `≥ 1` é do use case. |

**Response** — `CreateReservationResponse`

| Campo | Tipo |
|---|---|
| `reservation_id` | `UUID` |
| `status` | `ReservationStatus` (sempre `PENDING`) |
| `event_id` | `UUID` |
| `ticket_category_id` | `UUID` |
| `user_id` | `UUID` |
| `quantity` | `int` |
| `total_price` | `Decimal` |
| `created_at` | `datetime` |
| `expires_at` | `datetime` |

**Regras**

1. Só é possível reservar **antes** do início do evento: `Event.accepts_reservations(now)`
   ([DEC-15](requirements.md#dec-15--reserva-só-antes-do-início-do-evento)).
2. Uma reserva contém vários ingressos de **uma** categoria.
3. `quantity ≥ 1`.
4. A soma das quantidades do usuário no evento, em `PENDING` e `CONFIRMED`, mais `quantity`, não passa de
   `max_tickets_per_user` ([DEC-11](requirements.md#dec-11--limite-por-usuário-soma-quantidades)).
5. `quantity ≤ reservable` da categoria. Igual é aceito: a reserva esgota a categoria.
6. `total_price = calculate_total_price(...)` ([domain §2.4](domain.md#24-preço)).
7. A reserva nasce por `Reservation.create(..., now, ttl)`: `PENDING`, `expires_at = now + ttl`
   ([DEC-09](requirements.md#dec-09--tempo-de-vida-da-reserva-e-expiração)).
8. Validar em memória **não basta**: estoque, limite do usuário e reserva são gravados numa escrita atômica condicional
   ([persistence §4](persistence.md#4-escritas-atômicas)). Sob concorrência, a primeira escrita válida vence, e as
   demais recebem `ConcurrencyConflict`. O motivo real (estoque ou limite) não é detalhado: ao tentar de novo, o
   cliente recebe o erro específico das regras 4 e 5.
9. **Reenvio do mesmo POST cria outra reserva.** Risco aceito no MVP, limitado pela regra 4 e pelo TTL (EXT-12).

**Fluxo**

1. Ler `now`.
2. Buscar o evento → `EventNotFound`.
3. `accepts_reservations(now)` → senão `EventAlreadyStarted`.
4. `find_category(ticket_category_id)` → senão `TicketCategoryNotFound`.
5. `quantity ≥ 1` → senão `InvalidReservationQuantity`.
6. `held = get_held_quantity(event_id, user_id)`; `held + quantity ≤ max_tickets_per_user` → senão
   `UserReservationLimitExceeded`.
7. `quantity ≤ reservable` → senão `InsufficientReservableQuantity`.
8. Calcular `total_price`, criar a `Reservation` com `new_id()` e aplicar `Event.reserve`.
9. `save_new(reservation, max_tickets_per_user)` → `CONFLICT` → `ConcurrencyConflict`.
10. `Ok`.

**Erros de negócio**

| Erro | Condição | HTTP |
|---|---|---|
| `EventNotFound(event_id)` | Evento inexistente | 404 |
| `EventAlreadyStarted(event_id, start_at)` | `now ≥ start_at` | 409 |
| `TicketCategoryNotFound(ticket_category_id)` | Categoria não pertence ao evento | 404 |
| `InvalidReservationQuantity(quantity)` | `quantity < 1` | 400 |
| `UserReservationLimitExceeded(limit, held, requested)` | Regra 4 violada | 422 |
| `InsufficientReservableQuantity(requested, reservable)` | Regra 5 violada | 409 |
| `ConcurrencyConflict(resource_id)` | A escrita atômica perdeu a condição (`resource_id` = `ticket_category_id`) | 409 |

**Efeitos:** nasce uma reserva `PENDING`. A categoria bloqueia `quantity` ingressos, e o total ativo do usuário no
evento cresce. Nada é publicado ([DEC-06](requirements.md#dec-06--notificação-obrigatória-apenas-no-checkout)).

---

## UC-04 — CheckoutReservation

| | |
|---|---|
| Objetivo | Pagar e confirmar uma reserva pendente e disparar a notificação de compra (REQ-04) |
| Gatilho | `POST /reservations/{reservation_id}/checkout` |
| Pacote | `ticketing/application/use_cases/checkout_reservation/` |
| Dependências | `ReservationRepositoryPort`, `EventRepositoryPort`, `PaymentGatewayPort`, `NotificationPublisherPort`, `ClockPort`, `IdGeneratorPort` |
| Etapa | 5 |

**Request** — `CheckoutReservationRequest`

| Campo | Tipo | Origem |
|---|---|---|
| `reservation_id` | `UUID` | Path |
| `user_id` | `UUID` | Token. **Entra na Etapa 9** ([DEC-23](requirements.md#dec-23--segurança-por-último)) |

**Response** — `CheckoutReservationResponse`

| Campo | Tipo | Regra |
|---|---|---|
| `reservation_id` | `UUID` | |
| `status` | `ReservationStatus` | Sempre `CONFIRMED` |
| `total_price` | `Decimal` | Valor cobrado |
| `confirmed_at` | `datetime` | `updated_at` da confirmação |
| `notification_published` | `bool \| None` | `True`/`False` na confirmação ([DEC-07](requirements.md#dec-07--falha-ao-publicar-a-notificação-não-desfaz-a-compra)); `None` quando a chamada é repetição (regra 1) |

**Regras**

1. **Checkout idempotente** ([DEC-29](requirements.md#dec-29--checkout-idempotente)): se a reserva já está
   `CONFIRMED`, devolve `Ok` com os dados gravados, **sem cobrar nem publicar de novo**.
2. Só uma reserva `PENDING` e não vencida pode ser confirmada. O início do evento **não** bloqueia o checkout
   ([DEC-16](requirements.md#dec-16--o-checkout-tolera-o-início-do-evento)).
3. O evento e a categoria da reserva são carregados **antes** do pagamento. Se não existirem, é inconsistência de
   dados (500), nunca uma cobrança sem confirmação possível.
4. O pagamento é simulado e cobra exatamente `total_price`
   ([DEC-08](requirements.md#dec-08--pagamento-simulado-atrás-de-um-port)). Com pagamento recusado, a reserva continua
   `PENDING`.
5. A confirmação aplica `Reservation.confirm(now)` e `Event.confirm(...)` e é gravada atomicamente, com a condição de a
   reserva ainda estar `PENDING` e não vencida em `now`.
6. Depois de gravar, publica `PurchaseNotificationCommand` **sem canal**: o `notifications` usa a preferência do
   usuário ([DEC-06](requirements.md#dec-06--notificação-obrigatória-apenas-no-checkout)). Falha na publicação não
   desfaz a compra.
7. **Mensagem de compra** (texto fixo em pt-BR, montado por função pura em `ticketing/application/`):
   - assunto: `Compra confirmada — {event.name}`;
   - corpo: `Sua compra de {quantity} ingresso(s) {category.name} para {event.name} foi confirmada. Total: R$ {total}.`,
     com o total formatado em reais (`1.234,56`) por `format_brl(Decimal)`;
   - `notification_id = new_id()`, `correlation_id = reservation_id`, `occurred_at = now`.
8. **A partir da Etapa 9:** só o dono da reserva pode confirmá-la. Reserva de outro usuário responde como inexistente
   ([DEC-19](requirements.md#dec-19--autenticação-com-cognito-no-contexto-identity)).

**Fluxo**

1. Ler `now`.
2. Buscar a reserva → `ReservationNotFound`. A partir da Etapa 9, `reservation.user_id ≠ user_id` → também
   `ReservationNotFound`.
3. `CONFIRMED` → **devolver `Ok` com os dados gravados** (regra 1).
4. `CANCELLED` → `ReservationCancelled`; `EXPIRED` ou `is_expired(now)` → `ReservationExpired`.
5. Carregar o evento e a categoria. Ausentes → exceção de inconsistência (regra 3).
6. Cobrar `total_price` → `DECLINED` → `PaymentFailed`.
7. Aplicar `Reservation.confirm(now)` e `Event.confirm`. `save_confirmation(reservation)` → `CONFLICT` →
   `ConcurrencyConflict`.
8. Montar e publicar a mensagem (regra 7). Guardar o retorno em `notification_published`.
9. `Ok`.

**Erros de negócio**

| Erro | Condição | HTTP |
|---|---|---|
| `ReservationNotFound(reservation_id)` | Reserva inexistente ou de outro usuário | 404 |
| `ReservationCancelled(reservation_id)` | `status = CANCELLED` | 409 |
| `ReservationExpired(reservation_id, expires_at)` | `status = EXPIRED` ou prazo vencido | 409 |
| `PaymentFailed(reservation_id)` | Pagamento recusado | 402 |
| `ConcurrencyConflict(resource_id)` | Outra operação (expiração ou checkout concorrente) venceu a escrita (`resource_id` = `reservation_id`) | 409 |

**Efeitos:** a reserva passa a `CONFIRMED`, e os ingressos passam de reservados a vendidos. Uma mensagem de compra é
publicada.

**Riscos conhecidos** (pagamento simulado, impacto nulo no MVP; estorno na EXT-08):
- o pagamento é aprovado e a escrita perde a corrida para a expiração;
- dois checkouts **simultâneos** da mesma reserva passam do passo 4 e cobram os dois; um confirma e o outro recebe
  `ConcurrencyConflict`. Um checkout **repetido depois** da confirmação não cobra (regra 1).

---

## UC-05 — ExpirePendingReservations

| | |
|---|---|
| Objetivo | Expirar reservas pendentes vencidas e devolver o estoque bloqueado (REQ-08) |
| Gatilho | EventBridge Scheduler, a cada 1 minuto ([DEC-09](requirements.md#dec-09--tempo-de-vida-da-reserva-e-expiração)) |
| Pacote | `ticketing/application/use_cases/expire_pending_reservations/` |
| Dependências | `ReservationRepositoryPort`, `EventRepositoryPort`, `ClockPort` e `batch_limit: int` (configuração, padrão 100) |
| Etapa | 6 |

**Request** — `ExpirePendingReservationsRequest`

| Campo | Tipo | Regra |
|---|---|---|
| `reference_time` | `datetime \| None` | Se ausente, vale o `ClockPort`. Se presente, precisa ter fuso (INV-GL-01). Só vem de testes ou do payload do Scheduler. |

**Response** — `ExpirePendingReservationsResponse`

| Campo | Tipo |
|---|---|
| `expired_count` | `int` |
| `expired_reservation_ids` | `tuple[UUID, ...]` |

**Regras**

1. Só entram reservas `PENDING` com `expires_at ≤ reference_time`, no máximo `batch_limit` por execução. O restante
   fica para a execução seguinte ([DEC-31](requirements.md#dec-31--regras-de-apresentação-e-limites-operacionais)).
2. Cada reserva é expirada numa escrita atômica própria: `Reservation.expire(reference_time)` e `Event.release(...)`.
3. Se a escrita de uma reserva perder a condição (um checkout venceu), a reserva é **ignorada**: não conta em
   `expired_count` e não é erro.
4. Nenhuma reserva vencida → `Ok(expired_count=0)`. Não é erro.
5. **Idempotente:** rodar duas vezes sobre o mesmo estado produz o mesmo resultado final. Uma falha técnica no meio do
   lote sobe como exceção; o que já foi expirado fica, e a próxima execução continua.

**Fluxo:** fixar `reference_time` → `find_pending_expired(reference_time, batch_limit)` → para cada reserva, carregar
o evento (uma vez por evento na execução; ausente → exceção de inconsistência), aplicar as operações e
`save_release` → devolver `Ok` com as que foram expiradas.

**Erros de negócio:** nenhum.

**Efeitos:** reservas passam a `EXPIRED`, e o estoque volta a ser reservável.

---

## UC-06 — ProcessNotification

| | |
|---|---|
| Objetivo | Enviar pelo canal correto a notificação pedida num comando SQS (REQ-05, REQ-20) |
| Gatilho | Mensagem `SendNotification` v1 na fila de notificações ([contracts §3](contracts.md#3-mensagem-sqs-sendnotification)) |
| Pacote | `notifications/application/use_cases/process_notification/` |
| Dependências | `NotificationRepositoryPort`, `NotificationProfilePort`, `ClockPort`, mapeamento `NotificationType → NotificationStrategyPort` |
| Etapa | 7 |

**Request** — `ProcessNotificationRequest`

| Campo | Tipo | Regra |
|---|---|---|
| `notification_id` | `UUID` | |
| `user_id` | `UUID` | |
| `channel` | `NotificationType \| None` | Opcional. Força um canal. Sem ele, vale a preferência do perfil. |
| `subject` | `str \| None` | |
| `message_body` | `str` | |

O handler converte a mensagem SQS neste request. Mensagem malformada não chega ao use case (família **Borda**).

**Response** — `ProcessNotificationResponse`

| Campo | Tipo |
|---|---|
| `notification_id` | `UUID` |
| `status` | `NotificationStatus`: `SENT`, ou `FAILED` quando a chamada é duplicata de uma falha já registrada |

**Regras**

1. **Idempotência:** se já existe notificação `SENT` ou `FAILED` com o mesmo `notification_id`, devolve `Ok` com o
   status gravado e não reenvia. Um registro `PENDING` indica tentativa anterior interrompida, e o envio é repetido.
2. **`Ok` e `Err`:** envio bem-sucedido e duplicata devolvem `Ok`. Falha permanente **nova** grava `FAILED` e devolve
   `Err`. Em ambos os casos o handler consome a mensagem. Falha transitória do provedor é exceção: o registro fica
   `PENDING`, e a SQS repete ([DEC-03](requirements.md#dec-03--falha-permanente--falha-transitória-na-notificação)).
3. O perfil vem do `NotificationProfilePort` **já validado** (INV-NP-01..04). Destino em formato inválido não chega
   até aqui: é barrado na gravação do perfil (UC-11).
4. **Canal:** `channel` do request, se vier; senão, `preferred_channel`. **Destino:**
   `profile.destination_for(canal)` ([domain §3.2](domain.md#32-notificationprofile)).
5. A strategy é escolhida pelo mapeamento `canal → strategy`, sem `if/else`. PUSH não tem strategy no MVP
   ([domain §3.4](domain.md#34-strategy-de-envio)).
6. Entrega **ao menos uma vez**: duas entregas simultâneas do mesmo comando podem enviar duas vezes. Se a gravação de
   `SENT` perder a condição, a outra entrega já concluiu, e o use case devolve `Ok` com o status gravado.
7. O registro guarda `type`, `status` e `message_body`, como pede o enunciado.

**Fluxo**

1. Ler `now`. Buscar a notificação: `SENT`/`FAILED` → `Ok` com o status gravado (regra 1).
2. Carregar o perfil → senão `NotificationProfileNotFound`.
3. Resolver o canal. Obter a strategy → senão `UnsupportedNotificationChannel`.
4. Obter o destino → `None` → `NotificationDestinationUnavailable`.
5. Criar `Notification.pending(...)` e `save_pending` (se já não estava `PENDING`).
6. `send(destination, subject, message_body)`: `REJECTED(reason)` → `mark_failed` → `NotificationRejectedByProvider`.
7. `mark_sent(now)`, `save_final` e `Ok`.

Nos erros dos passos 2 a 4, a notificação é criada direto por `Notification.failed(...)`, com `type` e `destination`
até onde foram resolvidos, e gravada por `save_final` antes de devolver o `Err`.

**Erros de negócio**

| Erro | Condição | Destino SQS |
|---|---|---|
| `NotificationProfileNotFound(user_id)` | Usuário sem perfil (inclusive na janela de consistência eventual, [DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)) | Consumida, `FAILED` |
| `UnsupportedNotificationChannel(channel)` | Nenhuma strategy registrada para o canal (ex.: `PUSH` no MVP) | Consumida, `FAILED` |
| `NotificationDestinationUnavailable(user_id, channel)` | O canal escolhido não tem destino no perfil (ex.: `SMS` forçado sem telefone) | Consumida, `FAILED` |
| `NotificationRejectedByProvider(channel, reason)` | O provedor recusou de forma permanente | Consumida, `FAILED` |

**Efeitos:** o registro de notificação é gravado, e a mensagem é enviada pelo provedor.

---

## UC-07 — CancelReservation (extensão)

> **Fora do escopo obrigatório** ([EXT-01](requirements.md#5-backlog-de-extensões)). A especificação fica pronta para
> quando a fatia for aberta.

| | |
|---|---|
| Objetivo | Cancelar uma reserva pendente e devolver o estoque bloqueado |
| Gatilho | `POST /reservations/{reservation_id}/cancel` |
| Pacote | `ticketing/application/use_cases/cancel_reservation/` |
| Dependências | `ReservationRepositoryPort`, `EventRepositoryPort`, `ClockPort` |
| Etapa | backlog |

**Request:** `reservation_id: UUID` (path) e, a partir da Etapa 9, `user_id: UUID` (token).

**Response:** `reservation_id: UUID`, `status: ReservationStatus` (`CANCELLED`) e `cancelled_at: datetime`.

**Regras**

1. Só uma reserva `PENDING` e não vencida pode ser cancelada. Vencida e ainda não expirada pelo job →
   `ReservationExpired`, como no checkout.
2. Aplica `Reservation.cancel(now)` e `Event.release(...)`: o estoque volta como na expiração.
3. A escrita é atômica, com condição `status = PENDING` **e** `expires_at > now`.
4. A partir da Etapa 9, só o dono da reserva pode cancelá-la
   ([DEC-19](requirements.md#dec-19--autenticação-com-cognito-no-contexto-identity)).

**Fluxo:** ler `now` → buscar a reserva do usuário → verificar o estado → verificar o prazo → carregar o evento →
aplicar as operações → `save_release` → `Ok`.

**Erros de negócio**

| Erro | Condição | HTTP |
|---|---|---|
| `ReservationNotFound(reservation_id)` | Reserva inexistente ou de outro usuário | 404 |
| `ReservationAlreadyConfirmed(reservation_id)` | `status = CONFIRMED` | 409 |
| `ReservationCancelled(reservation_id)` | `status = CANCELLED` | 409 |
| `ReservationExpired(reservation_id, expires_at)` | `status = EXPIRED` ou prazo vencido | 409 |
| `ConcurrencyConflict(resource_id)` | A escrita perdeu a condição | 409 |

---

## UC-08 — RegisterUser *(Etapa 9)*

> Especificação completa na Etapa 9, com `feature-spec-brainstorm`. O que já está decidido
> ([DEC-19](requirements.md#dec-19--autenticação-com-cognito-no-contexto-identity),
> [DEC-26](requirements.md#dec-26--um-canal-preferido-definido-no-cadastro)):

- Pacote `identity/application/use_cases/register_user/`. Dependência: `IdentityProviderPort`.
- Entrada: `email`, `password`, `phone_number` (opcional) e `preferred_channel` (`EMAIL` ou `SMS`, padrão `EMAIL`).
- Aplica INV-NP-03 **já no cadastro** (SMS exige telefone), para não aceitar um perfil que o `notifications`
  rejeitaria. `phone_number` e `preferred_channel` ficam no Cognito como atributos do usuário, para o UC-10 publicar.
- Erros: `EmailAlreadyRegistered` (409), `PasswordPolicyViolation` (400), `InvalidNotificationPreference` (400).

## UC-09 — AuthenticateUser *(Etapa 9)*

- Pacote `identity/application/use_cases/authenticate_user/`. Dependência: `IdentityProviderPort`.
- Entrada: `email`, `password`. Saída: `id_token`, `access_token`, `expires_in`.
- Erros: `InvalidCredentials` (401), `UserNotConfirmed` (403).

## UC-10 — ConfirmRegistration *(Etapa 9)*

- Pacote `identity/application/use_cases/confirm_registration/`. Dependências: `IdentityProviderPort`,
  `UserRegisteredPublisherPort`, `ClockPort`.
- Entrada: `email` e `code` (o código que o Cognito enviou por e-mail,
  [DEC-28](requirements.md#dec-28--confirmação-de-cadastro-por-código)).
- Depois de o Cognito confirmar, publica `UserRegistered` ([contracts §4](contracts.md#4-mensagem-sqs-userregistered))
  com `user_id`, e-mail, telefone, canal preferido e `occurred_at = now`.
- Erros: `InvalidConfirmationCode` (400), `ConfirmationCodeExpired` (400), `UserAlreadyConfirmed` (409).

---

## UC-11 — SyncNotificationProfile

| | |
|---|---|
| Objetivo | Manter o perfil de notificação atualizado a partir dos fatos publicados pelo `identity` ([DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)) |
| Gatilho | Mensagem `UserRegistered` v1 na fila `notification-profiles` ([contracts §4](contracts.md#4-mensagem-sqs-userregistered)) |
| Pacote | `notifications/application/use_cases/sync_notification_profile/` |
| Dependências | `NotificationProfilePort` |
| Etapa | 9, junto com o publicador (UC-10). Até lá, os perfis vêm por seed. |

**Request** — `SyncNotificationProfileRequest`: `user_id: UUID`, `email: str`, `phone_number: str | None`,
`preferred_channel: NotificationType` e `occurred_at: datetime`.

**Response** — `SyncNotificationProfileResponse`: `user_id: UUID` e `applied: bool` (`False` quando o evento era
antigo e foi ignorado).

**Regras**

1. **Validação antes de construir:** o use case chama `profile_violations(...)`
   ([domain §3.3](domain.md#33-validação-de-destino)). Lista não vazia → `Err`. Assim a entidade só é construída com
   dados válidos, e nenhuma exceção de domínio é usada como fluxo (`AGENTS.md` §3.1).
2. **Idempotente e resistente a desordem:** o perfil só é gravado se não existir ou se `occurred_at` for mais recente
   que o `updated_at` gravado. Repetir o mesmo evento ou recebê-lo fora de ordem não regride o perfil.
3. Perder a condição da gravação ([persistence §4.5](persistence.md#45-perfil-de-notificação--uc-11)) significa evento
   antigo: `Ok(applied=False)`, sem erro.
4. `preferred_channel = PUSH` nem chega ao use case: o contrato da mensagem só aceita `EMAIL | SMS`, e a borda a
   trata como malformada.

**Fluxo:** validar (regra 1) → construir o `NotificationProfile` com `updated_at = occurred_at` → `save_if_newer` →
`Ok`.

**Erros de negócio**

| Erro | Condição | Destino SQS |
|---|---|---|
| `NotificationProfileRejected(user_id, violations)` | Os dados violam INV-NP-01..04 | Consumida. O perfil não é gravado. A falha é registrada em log e métrica, sem dados pessoais. |

**Efeitos:** o perfil de notificação do usuário é criado ou atualizado.
