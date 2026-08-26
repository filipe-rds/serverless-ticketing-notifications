# Domínio `ticketing`

## `Event`

Representa o evento disponível para venda.

**Atributos**

- `event_id`
- `name`
- `description`
- `location`
- `start_at`
- `end_at`
- `max_tickets_per_user`
- `categories`

**Observações**

- `start_at` e `end_at` definem o tempo de vigência do evento.
- `max_tickets_per_user` define o limite de ingressos por usuário no evento.
- `categories` define a lista de categorias do evento

## `TicketCategory`

Representa uma categoria de ingresso vinculada a um evento.

**Atributos**

- `ticket_category_id`
- `name`
- `price`
- `available_quantity`
- `reserved_quantity`

**Atributo derivado**

- `reservable_quantity`

**Regra do derivado**

- `reservable_quantity = available_quantity - reserved_quantity`

**Observações**

- `available_quantity` representa o estoque disponível real.
- `reserved_quantity` representa o estoque temporariamente bloqueado por reservas pendentes.

## `Reservation`

Representa a reserva temporária ou efetivada de ingressos.

**Atributos**

- `reservation_id`
- `ticket_category_id`
- `user_id`
- `quantity`
- `status`
- `created_at`
- `expires_at`
- `updated_at`

**Status possíveis**

- `PENDING`
- `CONFIRMED`
- `EXPIRED`
- `CANCELLED`

---

# Domínio `notifications`

## `Notification`

Representa o registro de uma notificação processada.

**Atributos**

- `notification_id`
- `user_id`
- `type`
- `destination`
- `status`
- `message_body`

**Tipos possíveis**

- `EMAIL`
- `SMS`
- `PUSH`

**Status possíveis**

- `PENDING`
- `SENT`
- `FAILED`

**Observações**

- `type` define o canal de envio da notificação.
- `destination` define o destino de envio de acordo com o canal:
    - e-mail, quando `type = EMAIL`
    - telefone, quando `type = SMS`
    - token ou identificador do dispositivo, quando `type = PUSH`
- `destination` deve ser validado de acordo com o `type`.
