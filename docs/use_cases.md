> **Base no markdown:**  
> O arquivo `project_base.md` explicita:
>
> - `GET /events`
> - `GET /events/{event_id}/tickets`
> - `POST /events/{event_id}/reservations`
> - `POST /reservations/{reservation_id}/checkout`
> - notificações assíncronas via SQS, com SES/SNS e Strategy
>
> **Adições por refinamento de domínio:**
>
> - `ExpirePendingReservationsUseCase`
> - `CancelReservationUseCase`
> - limite de reservas por usuário em um evento

---

# 1. `ListEventsUseCase`

**Objetivo**  
Listar eventos disponíveis e quantidade de ingressos restantes.

**Entrada**

- sem entrada obrigatória

**Saída**

- lista de eventos
- quantidade restante por evento

**Regras**

- pertence ao domínio `ticketing`
- é um caso de uso de consulta

**Fluxo de sucesso**

1. Buscar eventos disponíveis
2. Montar resposta com quantidade restante
3. Retornar lista

**Fluxos de erro**

- Ocorreu um erro inesperado ao listar os eventos. (`UnexpectedError`)

---

# 2. `ListEventTicketsUseCase`

**Objetivo**  
Listar categorias de ingressos e preços de um evento.

**Entrada**

- `event_id`

**Saída**

- `event_id`
- lista de categorias
- preços

**Regras**

- pertence ao domínio `ticketing`
- retorna categorias e preços do evento
- pode aplicar taxa de conveniência, se isso entrar no escopo final

**Fluxo de sucesso**

1. Receber `event_id`
2. Validar existência do evento
3. Buscar categorias e preços
4. Retornar resultado

**Fluxos de erro**

- O evento informado não foi encontrado. (`EventNotFound`)
- Ocorreu um erro inesperado ao listar os ingressos do evento. (`UnexpectedError`)

---

# 3. `CreateReservationUseCase`

**Objetivo**  
Criar uma reserva temporária de ingresso.

**Entrada**

- `event_id`
- `user_id`
- `ticket_category`
- `quantity`

**Saída**

- `reservation_id`
- `status`
- `event_id`
- `user_id`
- `ticket_category`
- `quantity`
- `created_at`
- `expires_at`

**Regras**

- pertence ao domínio `ticketing`
- a reserva nasce em `PENDING`
- reserva é um pré-pedido
- só cria se houver quantidade reservável suficiente
- ao criar a reserva, a quantidade fica bloqueada
- múltiplos ingressos por reserva são permitidos
- a primeira gravação válida vence em cenário de concorrência
- deve evitar overbooking
- valida limite de ingressos por usuário no evento
- o limite por usuário considera reservas em:
    - `PENDING`
    - `CONFIRMED`
- não considera:
    - `EXPIRED`
    - `CANCELLED`

**Fluxo de sucesso**

1. Validar entrada
2. Validar existência do evento
3. Validar existência da categoria
4. Validar quantidade solicitada
5. Validar limite por usuário no evento
6. Validar disponibilidade para reserva
7. Criar reserva com status `PENDING`
8. Atualizar bloqueio da quantidade reservada
9. Persistir dados
10. Publicar intenção de notificação, se adotado
11. Retornar reserva criada

**Fluxos de erro**

- O evento informado não foi encontrado. (`EventNotFound`)
- A categoria de ingresso informada não foi encontrada. (`TicketCategoryNotFound`)
- A quantidade informada para reserva é inválida. (`InvalidReservationQuantity`)
- O usuário excedeu o limite permitido de ingressos para este evento. (`UserReservationLimitExceeded`)
- Não há quantidade disponível para atender a reserva solicitada. (`InsufficientReservableQuantity`)
- A reserva não pôde ser concluída por conflito de concorrência. (`ConcurrencyConflict`)
- Não foi possível salvar a reserva. (`PersistenceError`)
- A reserva foi criada, mas houve falha ao publicar a notificação. (`NotificationPublishError`)
- Ocorreu um erro inesperado ao criar a reserva. (`UnexpectedError`)

---

# 4. `CheckoutReservationUseCase`

**Objetivo**  
Efetivar a compra de uma reserva.

**Entrada**

- `reservation_id`

**Saída**

- `reservation_id`
- `status`
- `confirmed_at`

**Regras**

- pertence ao domínio `ticketing`
- confirma apenas reserva em `PENDING`
- simula pagamento
- ao confirmar a compra:
    - remove a quantidade do bloco reservado
    - reduz o estoque disponível
- reserva vencida não pode ser confirmada
- reserva cancelada não pode ser confirmada
- após confirmação, pode publicar mensagem de notificação

**Fluxo de sucesso**

1. Buscar reserva
2. Validar existência
3. Validar que está em `PENDING`
4. Validar que não expirou
5. Simular pagamento
6. Alterar status para `CONFIRMED`
7. Atualizar estoque
8. Persistir dados
9. Publicar notificação de sucesso
10. Retornar resultado

**Fluxos de erro**

- A reserva informada não foi encontrada. (`ReservationNotFound`)
- A reserva já foi confirmada anteriormente. (`ReservationAlreadyConfirmed`)
- A reserva está expirada e não pode ser confirmada. (`ReservationExpired`)
- A reserva foi cancelada e não pode ser confirmada. (`ReservationCancelled`)
- A reserva está em um estado inválido para checkout. (`InvalidReservationState`)
- O pagamento simulado não pôde ser concluído. (`PaymentFailed`)
- Não foi possível salvar a confirmação da reserva. (`PersistenceError`)
- A compra foi confirmada, mas houve falha ao publicar a notificação. (`NotificationPublishError`)
- Ocorreu um erro inesperado ao realizar o checkout da reserva. (`UnexpectedError`)

---

# 5. `ExpirePendingReservationsUseCase`

**Objetivo**  
Expirar reservas pendentes vencidas e liberar a quantidade bloqueada.

**Entrada**

- `reference_time` opcional

**Saída**

- `expired_count`
- `expired_reservation_ids`

**Regras**

- pertence ao domínio `ticketing`
- foi adicionado para suportar o lock temporário
- só reservas `PENDING` podem expirar
- ao expirar:
    - status muda para `EXPIRED`
    - libera a quantidade reservada
    - não reduz estoque vendido
- reservas já confirmadas ou canceladas não entram no processamento

**Fluxo de sucesso**

1. Buscar reservas pendentes vencidas
2. Marcar cada reserva como `EXPIRED`
3. Liberar a quantidade bloqueada
4. Persistir alterações
5. Retornar quantidade e ids expirados

**Fluxos de erro**

- Não há reservas pendentes vencidas para expirar. (`NoExpiredReservationsFound`)
- Foi identificada uma inconsistência no estado de uma das reservas pendentes. (`InconsistentReservationState`)
- Não foi possível salvar a expiração das reservas pendentes. (`PersistenceError`)
- Ocorreu um erro inesperado ao expirar reservas pendentes. (`UnexpectedError`)

---

# 6. `CancelReservationUseCase`

**Objetivo**  
Cancelar uma reserva pendente e liberar a quantidade bloqueada.

**Entrada**

- `reservation_id`

**Saída**

- `reservation_id`
- `status`
- `cancelled_at`

**Regras**

- pertence ao domínio `ticketing`
- só reserva `PENDING` pode ser cancelada
- ao cancelar:
    - status muda para `CANCELLED`
    - libera a quantidade reservada
    - não reduz estoque vendido
- reserva confirmada não pode ser cancelada
- reserva expirada não pode ser cancelada

**Fluxo de sucesso**

1. Buscar reserva
2. Validar existência
3. Validar que está em `PENDING`
4. Alterar status para `CANCELLED`
5. Liberar quantidade bloqueada
6. Persistir alterações
7. Retornar resultado

**Fluxos de erro**

- A reserva informada não foi encontrada. (`ReservationNotFound`)
- A reserva já foi confirmada e não pode ser cancelada. (`ReservationAlreadyConfirmed`)
- A reserva já expirou e não pode ser cancelada. (`ReservationExpired`)
- A reserva já foi cancelada anteriormente. (`ReservationAlreadyCancelled`)
- A reserva está em um estado inválido para cancelamento. (`InvalidReservationState`)
- Não foi possível salvar o cancelamento da reserva. (`PersistenceError`)
- Ocorreu um erro inesperado ao cancelar a reserva. (`UnexpectedError`)

---

# 7. `ProcessNotificationUseCase`

**Objetivo**  
Consumir a mensagem da fila e enviar a notificação pelo canal correto.

**Entrada**

- `notification_id`
- `user_id`
- `type`
- `destination`
- `message_body`

**Saída**

- status da notificação:
    - `SENT`
    - `FAILED`

**Regras**

- Deve pertencer ao domínio `notifications`.
- Não deve possuir endpoint público.
- Deve ser orientado a eventos.
- Deve usar Strategy para escolher o canal de envio.
- Deve considerar os canais previstos no markdown:
    - e-mail via SES
    - SMS/Push via SNS
- Deve receber ou resolver um `destination` válido para envio.
- Deve validar o `destination` de acordo com o `type`.
- Deve registrar:
    - `Type`
    - `Status`
    - `MessageBody`
- Pode encaminhar mensagens para DLQ em caso de falhas repetidas.

**Fluxo de sucesso**

1. Receber mensagem
2. Interpretar os dados da notificação
3. Validar o tipo de canal informado
4. Validar ou resolver o `destination` para envio
5. Escolher a estratégia de envio
6. Formatar a mensagem
7. Enviar notificação
8. Registrar status `SENT`

**Fluxos de erro**

- A mensagem recebida é inválida ou está incompleta. (`InvalidNotificationMessage`)
- O tipo de canal informado não é suportado. (`UnsupportedNotificationChannel`)
- O destino informado é inválido para o canal selecionado. (`InvalidNotificationDestination`)
- Não foi possível obter um destino válido para envio. (`NotificationDestinationNotFound`)
- O envio da notificação falhou no provedor configurado. (`NotificationDeliveryFailed`)
- Não foi possível registrar o status da notificação. (`PersistenceError`)
- A mensagem excedeu o número de tentativas permitidas e deve seguir para a DLQ. (`MaxRetriesExceeded`)
- Ocorreu um erro inesperado ao processar a notificação. (`UnexpectedError`)
