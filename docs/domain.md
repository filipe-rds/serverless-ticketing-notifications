# Modelo de domínio

Entidades, invariantes, operações e estados dos bounded contexts `ticketing` e `notifications`. Este documento define
**o que é verdade no domínio** e **o que cada entidade sabe fazer**. Quem orquestra essas operações são os casos de
uso ([`use_cases.md`](use_cases.md)). O contexto `identity` (Etapa 9) não tem regra de domínio própria: delega ao
Cognito.

**Convenções válidas para todo o documento**

- Identificadores `UUID`, dinheiro `Decimal`, quantidades `int`.
- **Toda data é `datetime` timezone-aware em UTC** (INV-GL-01). Data sem fuso é violação de invariante.
- Entidades são imutáveis (`dataclass(frozen=True, slots=True)`), e toda operação devolve uma **nova instância**
  (`AGENTS.md` §6.4).
- **O domínio não lê o relógio.** Toda operação que depende do instante recebe `now` como argumento. Quem lê o
  relógio é o caso de uso, pelo `ClockPort` ([use_cases §Catálogo de ports](use_cases.md#catálogo-de-ports)).
- **O domínio não gera IDs.** Os identificadores chegam prontos, gerados pelo `IdGeneratorPort` no caso de uso.
- Violar uma invariante ou pré-condição levanta uma **exceção de domínio** (§2.5, §3.5). Isso indica bug: o caso de
  uso deveria ter validado antes e devolvido `Err` (`AGENTS.md` §3.1).

| ID | Invariante global |
|---|---|
| INV-GL-01 | Todo atributo `datetime` de qualquer entidade é timezone-aware em UTC |

---

## 1. Linguagem ubíqua

| Termo | Significado |
|---|---|
| **Evento** | Acontecimento com data, local e ingressos à venda. É a raiz do agregado de vendas. |
| **Categoria de ingresso** | Faixa de ingresso de um evento (ex.: Pista, Camarote), com preço e lotação próprios. |
| **Lotação** (`capacity`) | Total de ingressos de uma categoria. Nunca muda. |
| **Reservado** (`reserved`) | Ingressos bloqueados por reservas pendentes. |
| **Vendido** (`sold`) | Ingressos de reservas confirmadas. |
| **Reservável** (`reservable`) | O que ainda pode ser reservado: `capacity - sold - reserved`. |
| **Reserva** | Pré-pedido que bloqueia ingressos por tempo limitado. |
| **Checkout** | Pagamento e confirmação de uma reserva pendente. |
| **Expiração** | Fim do prazo de uma reserva pendente não paga. O estoque bloqueado volta a ser reservável. |
| **Taxa de conveniência** | Percentual cobrado sobre o preço base, definido por evento ([§2.4](#24-preço)). |
| **Notificação** | Registro de uma comunicação enviada (ou tentada) a um usuário por um canal. |
| **Canal** | Meio de envio: `EMAIL`, `SMS` ou `PUSH`. |
| **Destino** | Endereço no canal: e-mail, telefone ou token do dispositivo. |
| **Perfil de notificação** | E-mail, telefone e canal preferido de um usuário, guardados pelo `notifications`. |
| **Canal preferido** | Canal pelo qual o usuário quer receber os avisos: `EMAIL` ou `SMS` no MVP. |

---

## 2. Bounded context `ticketing`

### 2.1 `Event` — raiz do agregado

Evento à venda. `TicketCategory` só é acessada e alterada através de `Event` (`AGENTS.md` D5). Eventos entram no
sistema por seed (EXT-07). Por isso as invariantes INV-EV só são verificadas quando o mapper remonta o agregado: dado
inválido no banco vira exceção de domínio e HTTP 500.

| Atributo | Tipo | Descrição |
|---|---|---|
| `event_id` | `UUID` | Identificador |
| `name` | `str` | Nome |
| `description` | `str` | Descrição |
| `location` | `str` | Local |
| `start_at` | `datetime` | Início |
| `end_at` | `datetime` | Fim |
| `max_tickets_per_user` | `int` | Máximo de ingressos por usuário no evento ([DEC-11](requirements.md#dec-11--limite-por-usuário-soma-quantidades)) |
| `convenience_fee_percentage` | `Decimal` | Percentual da taxa de conveniência ([DEC-02](requirements.md#dec-02--taxa-de-conveniência-pela-fórmula-literal)) |
| `categories` | `tuple[TicketCategory, ...]` | Categorias do evento, na ordem de exibição. Pode ser vazia. |

**Invariantes** (violação → `InvalidEvent`)

| ID | Regra |
|---|---|
| INV-EV-01 | `start_at < end_at` |
| INV-EV-02 | `max_tickets_per_user ≥ 1` |
| INV-EV-03 | `0 ≤ convenience_fee_percentage ≤ 100` |
| INV-EV-04 | `ticket_category_id` é único dentro do evento |

**Janelas de tempo** (consultas puras, recebem `now`)

| Consulta | Condição | Usada por |
|---|---|---|
| `accepts_reservations(now) -> bool` | `now < start_at` | UC-03 ([DEC-15](requirements.md#dec-15--reserva-só-antes-do-início-do-evento)) |
| `is_listed(now) -> bool` | `now < end_at` | UC-01 ([DEC-14](requirements.md#dec-14--evento-disponível-é-evento-que-ainda-não-terminou)) |
| — | O checkout depende só de `expires_at` da reserva, **independente** de `start_at` | UC-04 ([DEC-16](requirements.md#dec-16--o-checkout-tolera-o-início-do-evento)) |

**Operações** (devolvem um novo `Event`)

| Operação | Usada por | Efeito na categoria | Pré-condição → exceção |
|---|---|---|---|
| `find_category(ticket_category_id) -> TicketCategory \| None` | UC-03 | — (consulta) | — |
| `reserve(ticket_category_id, quantity)` | UC-03 | `reserved += q` | categoria existe → `TicketCategoryNotInEvent`; `q ≥ 1` → `InvalidStockOperation`; `q ≤ reservable` → `InsufficientStock` |
| `confirm(ticket_category_id, quantity)` | UC-04 | `reserved -= q` · `sold += q` | categoria existe → `TicketCategoryNotInEvent`; `1 ≤ q ≤ reserved` → `InvalidStockOperation` |
| `release(ticket_category_id, quantity)` | UC-05, UC-07 | `reserved -= q` | categoria existe → `TicketCategoryNotInEvent`; `1 ≤ q ≤ reserved` → `InvalidStockOperation` |

### 2.2 `TicketCategory`

Categoria de ingresso. Faz parte do agregado `Event` e **não tem repositório próprio**.

| Atributo | Tipo | Descrição |
|---|---|---|
| `ticket_category_id` | `UUID` | Identificador, único no evento |
| `name` | `str` | Nome exibido (ex.: "Camarote") |
| `base_price` | `Decimal` | Preço unitário, sem taxa |
| `capacity` | `int` | Lotação. **Imutável** depois de criada. |
| `reserved` | `int` | Bloqueado por reservas `PENDING` |
| `sold` | `int` | Vendido, de reservas `CONFIRMED` |
| `reservable` | `int` (derivado) | `capacity - sold - reserved` |

**Invariantes** (violação → `InvalidTicketCategory`)

| ID | Regra |
|---|---|
| INV-TC-01 | `capacity ≥ 1` |
| INV-TC-02 | `base_price ≥ 0` |
| INV-TC-03 | `reserved ≥ 0`, `sold ≥ 0` e `reserved + sold ≤ capacity` (equivale a `reservable ≥ 0`) |
| INV-TC-04 | `capacity` nunca muda |

**Estoque por transição de reserva**

| Transição da reserva | `reserved` | `sold` | `reservable` |
|---|---|---|---|
| criar (`→ PENDING`) | `+ q` | — | `− q` |
| confirmar (`PENDING → CONFIRMED`) | `− q` | `+ q` | — |
| expirar ou cancelar (`PENDING → EXPIRED / CANCELLED`) | `− q` | — | `+ q` |

`quantity == reservable` é aceito: a reserva esgota a categoria.

### 2.3 `Reservation`

Pré-pedido de ingressos de uma categoria, com prazo de validade.

| Atributo | Tipo | Descrição |
|---|---|---|
| `reservation_id` | `UUID` | Identificador |
| `event_id` | `UUID` | Evento da reserva (necessário para carregar o agregado no checkout) |
| `ticket_category_id` | `UUID` | Categoria reservada |
| `user_id` | `UUID` | Usuário que reservou. É só referência por identidade: o `ticketing` não conhece outros dados do usuário ([DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)). |
| `quantity` | `int` | Quantidade de ingressos |
| `total_price` | `Decimal` | Valor total congelado na criação ([§2.4](#24-preço)) |
| `status` | `ReservationStatus` | Estado atual |
| `created_at` | `datetime` | Criação |
| `expires_at` | `datetime` | Prazo para checkout ([DEC-09](requirements.md#dec-09--tempo-de-vida-da-reserva-e-expiração)) |
| `updated_at` | `datetime` | Última transição. Na criação, igual a `created_at`. Nas respostas, aparece como `confirmed_at` ou `cancelled_at`. |

**Invariantes** (violação → `InvalidReservation`, salvo INV-RS-04)

| ID | Regra |
|---|---|
| INV-RS-01 | `quantity ≥ 1` |
| INV-RS-02 | `created_at < expires_at` |
| INV-RS-03 | `total_price ≥ 0` |
| INV-RS-04 | Só ocorrem as transições da máquina de estados abaixo. Qualquer outra levanta `InvalidReservationTransition`. |
| INV-RS-05 | `created_at ≤ updated_at` |

**Operações**

| Operação | Usada por | Resultado | Pré-condição → exceção |
|---|---|---|---|
| `Reservation.create(reservation_id, event_id, ticket_category_id, user_id, quantity, total_price, now, ttl)` | UC-03 | `status = PENDING`, `created_at = updated_at = now`, `expires_at = now + ttl` | `ttl > 0` e INV-RS-01..03 → `InvalidReservation` |
| `is_expired(now) -> bool` | UC-04, UC-07 | `expires_at ≤ now` (consulta pura) | — |
| `confirm(now)` | UC-04 | `status = CONFIRMED`, `updated_at = now` | `status = PENDING` → `InvalidReservationTransition`; `now < expires_at` → `ReservationPastDeadline` |
| `expire(now)` | UC-05 | `status = EXPIRED`, `updated_at = now` | `status = PENDING` → `InvalidReservationTransition`; `expires_at ≤ now` → `ReservationNotYetDue` |
| `cancel(now)` | UC-07 | `status = CANCELLED`, `updated_at = now` | `status = PENDING` → `InvalidReservationTransition`; `now < expires_at` → `ReservationPastDeadline` |

**Máquina de estados**

```text
            ┌──────────► CONFIRMED   (checkout)
            │
PENDING ────┼──────────► EXPIRED     (prazo vencido)
            │
            └──────────► CANCELLED   (cancelamento — EXT-01)
```

| De \ Para | `CONFIRMED` | `EXPIRED` | `CANCELLED` |
|---|---|---|---|
| `PENDING` | ✅ | ✅ | ✅ |
| `CONFIRMED` | — | ❌ | ❌ |
| `EXPIRED` | ❌ | — | ❌ |
| `CANCELLED` | ❌ | ❌ | — |

- `PENDING` é o único estado não terminal. `CONFIRMED`, `EXPIRED` e `CANCELLED` são terminais.
- Uma reserva confirmada não pode ser cancelada nem expirar.
- A tabela está em `ReservationStatus.can_transition_to`, e as operações acima a usam.

**Estado efetivo e prazo.** Uma reserva `PENDING` com `expires_at ≤ agora` já está vencida, mesmo que o job de
expiração ainda não a tenha marcado como `EXPIRED`. O checkout e o cancelamento a tratam como expirada
([DEC-09](requirements.md#dec-09--tempo-de-vida-da-reserva-e-expiração)).

### 2.4 Preço

Regra de domínio, como função pura em `ticketing/domain/services/`:

```python
def calculate_total_price(
    base_price: Decimal, quantity: int, convenience_fee_percentage: Decimal
) -> Decimal: ...
```

```text
total_price = (base_price × quantity) + (base_price × convenience_fee_percentage / 100)
```

- O arredondamento é em 2 casas decimais, `ROUND_HALF_UP`, **só no resultado final**. Os cálculos intermediários são
  em `Decimal` exato.
- O total é calculado na criação da reserva e gravado em `Reservation.total_price`.
- A taxa incide uma vez sobre o preço unitário, como está no enunciado
  ([DEC-02](requirements.md#dec-02--taxa-de-conveniência-pela-fórmula-literal)).

| Caso | `base_price` | `quantity` | `T` | `total_price` |
|---|---|---|---|---|
| Exemplo | `250.00` | 2 | `10` | `500.00 + 25.00 = 525.00` |
| Sem taxa | `120.00` | 3 | `0` | `360.00` |
| Arredondamento | `0.05` | 1 | `10` | `0.05 + 0.005 = 0.055 → 0.06` |
| Ingresso gratuito | `0.00` | 4 | `10` | `0.00` |

### 2.5 Exceções de domínio

Vivem em `ticketing/domain/exceptions/` e derivam de `DomainException` (`shared/exceptions/`). Indicam bug ou dado
corrompido: estouram como HTTP 500 ou retry na SQS (`AGENTS.md` §3.1).

| Exceção | Quando |
|---|---|
| `InvalidEvent` | INV-EV-01..04 |
| `InvalidTicketCategory` | INV-TC-01..04 |
| `InvalidReservation` | INV-RS-01..03, INV-RS-05, `ttl ≤ 0` |
| `InvalidReservationTransition` | Transição fora da máquina de estados (INV-RS-04) |
| `ReservationPastDeadline` | `confirm` ou `cancel` com `now ≥ expires_at` |
| `ReservationNotYetDue` | `expire` com `now < expires_at` |
| `TicketCategoryNotInEvent` | `reserve`, `confirm` ou `release` com categoria que não pertence ao evento |
| `InsufficientStock` | `reserve` com quantidade acima de `reservable` |
| `InvalidStockOperation` | `confirm` ou `release` acima de `reserved`, ou quantidade `< 1` |
| `NaiveDatetime` | Data sem fuso em qualquer entidade (INV-GL-01) |

---

## 3. Bounded context `notifications`

### 3.1 `Notification`

Registro de uma comunicação processada. O `notification_id` vem do comando recebido e serve de **chave de
idempotência**: o mesmo comando entregue duas vezes não gera dois registros.

| Atributo | Tipo | Descrição |
|---|---|---|
| `notification_id` | `UUID` | Identificador, gerado por quem publica o comando |
| `user_id` | `UUID` | Destinatário |
| `type` | `NotificationType \| None` | Canal resolvido: `EMAIL`, `SMS`, `PUSH`. `None` só se a falha ocorreu antes da resolução. |
| `destination` | `str \| None` | Endereço resolvido no canal. `None` só se a falha ocorreu antes da resolução. |
| `subject` | `str \| None` | Assunto. Usado apenas no e-mail. |
| `message_body` | `str` | Conteúdo |
| `status` | `NotificationStatus` | `PENDING`, `SENT`, `FAILED` |
| `failure_reason` | `str \| None` | Nome do erro que levou a `FAILED` |
| `created_at` | `datetime` | Primeira gravação |
| `updated_at` | `datetime` | Última transição |

**Invariantes** (violação → `InvalidNotification`, salvo INV-NT-04)

| ID | Regra |
|---|---|
| INV-NT-01 | Em `PENDING` e `SENT`, `type` e `destination` estão preenchidos, e `destination` é válido para o `type` ([§3.3](#33-validação-de-destino)) |
| INV-NT-02 | `message_body` não é vazio |
| INV-NT-03 | `failure_reason` é preenchido se, e somente se, `status = FAILED` |
| INV-NT-04 | Só ocorrem as transições `PENDING → SENT` e `PENDING → FAILED`. `SENT` e `FAILED` são terminais. Violação → `InvalidNotificationTransition`. |
| INV-NT-05 | `created_at ≤ updated_at` |

**Operações**

| Operação | Usada por | Resultado |
|---|---|---|
| `Notification.pending(notification_id, user_id, type, destination, subject, message_body, now)` | UC-06 | `status = PENDING`, `created_at = updated_at = now` |
| `Notification.failed(notification_id, user_id, subject, message_body, failure_reason, now, type=None, destination=None)` | UC-06 | Falha permanente **antes** de enviar: nasce `FAILED`, com `type` e `destination` até onde foram resolvidos |
| `mark_sent(now)` | UC-06 | `PENDING → SENT`, `updated_at = now` |
| `mark_failed(failure_reason, now)` | UC-06 | `PENDING → FAILED` (o provedor rejeitou), `updated_at = now` |

### 3.2 `NotificationProfile`

Como e para onde notificar um usuário. É a **cópia local** que o `notifications` guarda dos dados de contato
([DEC-04](requirements.md#dec-04--o-destino-da-notificação-é-resolvido-pelo-notifications),
[DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)). Não é um cadastro de usuários: tem só o
necessário para enviar. É lido pelo `NotificationProfilePort` e atualizado pelo UC-11.

| Atributo | Tipo | Descrição |
|---|---|---|
| `user_id` | `UUID` | Usuário (o `sub` do Cognito a partir da Etapa 9) |
| `email` | `str` | E-mail. Obrigatório. |
| `phone_number` | `str \| None` | Telefone. Opcional. |
| `preferred_channel` | `NotificationType` | Canal preferido. Padrão `EMAIL` ([DEC-26](requirements.md#dec-26--um-canal-preferido-definido-no-cadastro)). |
| `updated_at` | `datetime` | Momento do fato que gerou esta versão do perfil. Serve para descartar eventos antigos (UC-11). |

**Invariantes** (violação → `InvalidNotificationProfile`)

| ID | Regra |
|---|---|
| INV-NP-01 | `email` está no formato de e-mail ([§3.3](#33-validação-de-destino)) |
| INV-NP-02 | `phone_number`, se presente, está em E.164 |
| INV-NP-03 | `preferred_channel = SMS` exige `phone_number` |
| INV-NP-04 | `preferred_channel ≠ PUSH` no MVP (EXT-10) |

**Operação**

| Operação | Usada por | Resultado |
|---|---|---|
| `destination_for(channel) -> str \| None` | UC-06 | `EMAIL` → `email`; `SMS` → `phone_number` (pode ser `None`); `PUSH` → `None` no MVP |

**Resolução de canal** (usada pelo UC-06): o `channel` do comando, se vier; senão, `preferred_channel`.

### 3.3 Validação de destino

Predicados **puros** em `notifications/domain/services/`, usados pela entidade (para garantir as invariantes) **e**
pelos casos de uso (para validar antes de construir, sem `try/except`, `AGENTS.md` §3.1):

| Predicado | Regra |
|---|---|
| `is_valid_email(value) -> bool` | `local@domínio`, com domínio contendo ponto |
| `is_e164(value) -> bool` | `+` seguido de 8 a 15 dígitos |
| `is_valid_destination(type, value) -> bool` | `EMAIL` → `is_valid_email`; `SMS` → `is_e164`; `PUSH` → não vazio |
| `profile_violations(email, phone_number, preferred_channel) -> tuple[str, ...]` | Lista vazia se INV-NP-01..04 forem satisfeitas; senão, os IDs das invariantes violadas |

### 3.4 Strategy de envio

Cada canal tem uma strategy que adapta `subject` e `message_body` ao meio e delega o envio a um adapter do provedor.
A escolha é feita por **mapeamento `type → strategy`**, montado no composition root, sem cadeia de `if/else`
([REQ-20](requirements.md#23-conceitos-a-praticar)). O contrato é o `NotificationStrategyPort`
([use_cases §Catálogo de ports](use_cases.md#catálogo-de-ports)).

| `type` | Strategy | Provedor (adapter) | Adaptação ao canal |
|---|---|---|---|
| `EMAIL` | `EmailNotificationStrategy` | Amazon SES | `subject` ausente → "Aviso do ticketstream" |
| `SMS` | `SmsNotificationStrategy` | Amazon SNS (SMS) | Sem assunto. Corpo cortado em 160 caracteres, terminando em "…" |

- **PUSH não tem strategy registrada no MVP.** O mapeamento não o contém, e pedir PUSH resulta em
  `UnsupportedNotificationChannel` (UC-06). A strategy e o adapter de push chegam com a EXT-10.

### 3.5 Exceções de domínio

Vivem em `notifications/domain/exceptions/` e derivam de `DomainException`.

| Exceção | Quando |
|---|---|
| `InvalidNotification` | INV-NT-01..03, INV-NT-05 |
| `InvalidNotificationTransition` | Transição fora de INV-NT-04 |
| `InvalidNotificationProfile` | INV-NP-01..04 |
| `NaiveDatetime` | Data sem fuso (INV-GL-01). Cada contexto tem a sua, porque os contextos não se importam. |
