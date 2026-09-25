# Persistência — Amazon DynamoDB

Modelo físico e garantias de concorrência. Tudo aqui é **detalhe de infraestrutura** (`AGENTS.md` §5): vive em
`*/infrastructure/persistence/` (models `pydynox`, mappers e repositórios) e nunca vaza para o núcleo. Os ports
devolvem entidades de domínio. A escrita atômica informa se venceu a condição por um **valor simples**, nunca por
exceção de negócio (`AGENTS.md` §6.5).

> **Status:** proposta de referência. Cada fatia confirma ou ajusta a parte que implementar, e a mudança é registrada
> aqui.

---

## 1. Princípios

1. **Uma tabela por bounded context** ([REQ-15](requirements.md#22-arquiteturais-e-de-infraestrutura)): `Ticket` e
   `Notification`. Single-table design fica fora do escopo.
2. **Padrão de acesso primeiro.** Chaves e índices existem para atender a um padrão de acesso da §2, e nenhum é criado
   "por precaução".
3. **Consistência pela condição, não pela leitura.** A validação em memória do use case produz a mensagem de erro. A
   condição atômica no banco é o que impede o overbooking de fato (`AGENTS.md` §6.8).
4. **Sem aritmética em condição.** O DynamoDB não avalia `a + b <= c` numa `ConditionExpression`. Por isso toda condição
   compara **um atributo com um valor** calculado pelo adapter
   ([DEC-05](requirements.md#dec-05--estoque-em-três-contadores-no-domínio-e-um-contador-materializado-no-banco)).

---

## 2. Padrões de acesso

| # | Padrão | Caso de uso | Operação |
|---|---|---|---|
| AP-01 | Listar todos os eventos com as categorias | UC-01 | `Scan` na tabela `Ticket` (volume didático; EXT-04 troca por GSI) |
| AP-02 | Carregar um evento com as categorias | UC-02, UC-03, UC-04, UC-05, UC-07 | `Query` com `PK = EVENT#<event_id>` |
| AP-03 | Carregar uma reserva por id | UC-04, UC-07 | `GetItem` em `RESERVATION#<id>` / `METADATA`, com leitura fortemente consistente |
| AP-04 | Quantidade ativa do usuário no evento | UC-03 | `GetItem` em `EVENT#<event_id>` / `USER#<user_id>`. Item ausente → `0`. |
| AP-05 | Reservas pendentes vencidas | UC-05 | `Query` no GSI `PendingByExpiration` com `pending_expires_at ≤ :now` e `Limit = batch_limit` |
| AP-06 | Criar reserva com bloqueio de estoque | UC-03 | `TransactWriteItems` ([§4.1](#41-criar-reserva--uc-03)) |
| AP-07 | Confirmar reserva | UC-04 | `TransactWriteItems` ([§4.2](#42-confirmar-reserva--uc-04)) |
| AP-08 | Expirar ou cancelar reserva | UC-05, UC-07 | `TransactWriteItems` ([§4.3](#43-expirar-ou-cancelar-reserva--uc-05-uc-07)) |
| AP-09 | Buscar notificação por id (idempotência) | UC-06 | `GetItem` em `USER#<user_id>` / `NOTIF#<id>` |
| AP-10 | Gravar ou atualizar notificação | UC-06 | `PutItem` / `UpdateItem` |
| AP-11 | Perfil de notificação do usuário | UC-06 | `GetItem` em `USER#<user_id>` / `PROFILE` |
| AP-12 | Criar ou atualizar perfil, sem regredir | UC-11 | `PutItem` condicional ([§4.5](#45-perfil-de-notificação--uc-11)) |

---

## 3. Tabelas e itens

### 3.1 Tabela `Ticket`

| Item | `PK` | `SK` | Atributos |
|---|---|---|---|
| Evento | `EVENT#<event_id>` | `METADATA` | `name`, `description`, `location`, `start_at`, `end_at`, `max_tickets_per_user`, `convenience_fee_percentage` |
| Categoria | `EVENT#<event_id>` | `TICKET_TIER#<ticket_category_id>` | `name`, `base_price`, `capacity`, `reserved`, `sold`, `available_quantity` |
| Total do usuário no evento | `EVENT#<event_id>` | `USER#<user_id>` | `held_quantity` (soma em `PENDING` + `CONFIRMED`) |
| Reserva | `RESERVATION#<reservation_id>` | `METADATA` | `event_id`, `ticket_category_id`, `user_id`, `quantity`, `total_price`, `status`, `created_at`, `expires_at`, `updated_at`, `pending_expires_at`\* |

- O evento, as categorias e os totais por usuário ficam na **mesma partição**, e um único `Query` (AP-02) remonta o
  agregado. O mapper ignora os itens `USER#` ao montar o `Event`.
- `available_quantity` é a cópia materializada de `reservable`. A cada escrita vale
  `available_quantity = capacity - sold - reserved`.
- \* `pending_expires_at` só existe enquanto a reserva está `PENDING`. É removido na transição, o que torna o GSI
  **esparso**.
- Dinheiro é gravado como número DynamoDB (precisão decimal) e convertido para `Decimal` com 2 casas no mapper.
- **Datas** são gravadas como string no formato canônico `YYYY-MM-DDTHH:MM:SSZ`, sem frações de segundo
  ([DEC-30](requirements.md#dec-30--formato-canônico-de-datas-e-dinheiro)). As condições e o GSI comparam essas
  strings, então o formato precisa ser idêntico em todo item.

**GSI `PendingByExpiration`**

| Chave | Atributo |
|---|---|
| Partition | `pending_bucket` (constante `"PENDING"`, só em itens pendentes) |
| Sort | `pending_expires_at` |
| Projeção | `ALL` (o UC-05 remonta a `Reservation` sem segunda leitura) |

- Leitura de GSI é **eventualmente consistente**: uma reserva recém-confirmada ainda pode aparecer. Isso é seguro,
  porque a escrita de expiração exige `status = PENDING` e simplesmente perde a condição (UC-05, regra 3).
- *Trade-off:* a partição constante concentra as leituras, o que é aceitável no volume do projeto. Em escala, o bucket
  passa a incluir um sufixo (por exemplo, a hora).

### 3.2 Tabela `Notification`

| Item | `PK` | `SK` | Atributos |
|---|---|---|---|
| Notificação | `USER#<user_id>` | `NOTIF#<notification_id>` | `type`, `destination`, `subject`, `message_body`, `status`, `failure_reason`, `created_at`, `updated_at` |
| Perfil de notificação | `USER#<user_id>` | `PROFILE` | `email`, `phone_number`, `preferred_channel`, `updated_at` |

- As chaves e os atributos `Type`, `Status` e `MessageBody` seguem o enunciado. Os nomes estão em `snake_case`, como no
  resto do projeto.
- O perfil fica **na mesma partição** das notificações do usuário. Uma notificação e o perfil que a resolveu estão sob
  o mesmo `USER#<user_id>`.
- Origem do perfil: seed até a Etapa 9; depois, o UC-11 a partir de `UserRegistered`
  ([DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)).

### 3.3 Usuários

**Não há tabela de usuários.** Usuários, senhas e unicidade do e-mail ficam no Cognito User Pool
([DEC-19](requirements.md#dec-19--autenticação-com-cognito-no-contexto-identity)). O `user_id` gravado em reservas e
notificações é o `sub` do Cognito.

Cada contexto guarda só o seu recorte ([DEC-27](requirements.md#dec-27--dados-de-usuário-divididos-por-contexto)):
- a tabela `Ticket` só tem o `user_id`, na reserva e no total do usuário por evento;
- a tabela `Notification` tem o perfil de envio.

Nenhuma consulta cruza as duas tabelas.

---

## 4. Escritas atômicas

Toda mudança de estoque é **uma** `TransactWriteItems`. Se qualquer condição falhar, nada é gravado. O adapter
traduz `TransactionCanceledException` em um resultado "conflito", que o use case converte em
`Err(ConcurrencyConflict)`. Dois motivos de cancelamento contam como conflito:

- `ConditionalCheckFailed`: a condição de negócio deixou de valer (estoque acabou, reserva mudou de estado);
- `TransactionConflict`: outra transação escrevia no mesmo item no mesmo instante, o que é típico do item quente de
  uma categoria concorrida ([architecture §9.2](architecture.md#92-gargalos-conhecidos)).

O adapter não repete a transação por conta própria. O `409` devolve a decisão ao cliente.

**Condição de integridade separada.** Perder `reserved >= :q` (§4.2, §4.3) ou `held_quantity >= :q` (§4.3) não é
corrida: significa contadores corrompidos. O adapter também devolve `CONFLICT`, mas registra o caso em log de erro com
métrica própria, para não se confundir com concorrência.

Notação: `q` é a quantidade da reserva, `max` é `max_tickets_per_user` e `now` é o `updated_at` da entidade, que o
use case preencheu com o `now` da execução.

### 4.1 Criar reserva — UC-03

| # | Item | Operação | Condição |
|---|---|---|---|
| 1 | Categoria | `SET reserved = reserved + :q, available_quantity = available_quantity - :q` | `available_quantity >= :q` |
| 2 | Total do usuário | `ADD held_quantity :q` | `attribute_not_exists(held_quantity) OR held_quantity <= :max_minus_q` |
| 3 | Reserva | `Put` (com `pending_bucket` e `pending_expires_at`) | `attribute_not_exists(PK)` |

`:max_minus_q = max - q` é calculado pelo adapter. É isso que evita aritmética na condição (princípio 4).

**Pré-condição do adapter:** `q ≤ max`. Se o item do usuário não existe, a condição 2 passa por
`attribute_not_exists`, sem comparar com o limite. O use case já garante `held + q ≤ max` (UC-03, passo 6), e o
adapter confere `q ≤ max` antes de montar a transação, levantando exceção se for violada (é bug, não corrida).

### 4.2 Confirmar reserva — UC-04

| # | Item | Operação | Condição |
|---|---|---|---|
| 1 | Reserva | `SET status = CONFIRMED, updated_at = :now REMOVE pending_bucket, pending_expires_at` | `status = PENDING AND expires_at > :now` |
| 2 | Categoria | `SET reserved = reserved - :q, sold = sold + :q` | `reserved >= :q` |

`available_quantity` e `held_quantity` não mudam: o ingresso passa de reservado para vendido.

### 4.3 Expirar ou cancelar reserva — UC-05, UC-07

| # | Item | Operação | Condição |
|---|---|---|---|
| 1 | Reserva | `SET status = EXPIRED \| CANCELLED, updated_at = :now REMOVE pending_bucket, pending_expires_at` | `status = PENDING` e, na expiração, `expires_at <= :now`; no cancelamento, `expires_at > :now` |
| 2 | Categoria | `SET reserved = reserved - :q, available_quantity = available_quantity + :q` | `reserved >= :q` |
| 3 | Total do usuário | `ADD held_quantity :minus_q` | `held_quantity >= :q` |

### 4.4 Notificação — UC-06

| Port | Escrita | Condição | Perder a condição significa |
|---|---|---|---|
| `save_pending` | `PutItem` do item `PENDING` | `attribute_not_exists(PK) OR status = PENDING` | Já está em estado final: `CONFLICT` |
| `save_final` a partir de `PENDING` | `UpdateItem` para `SENT` ou `FAILED` | `status = PENDING` | Outra entrega concluiu: `CONFLICT`, e o use case devolve o status gravado |
| `save_final` de uma falha antes do envio | `PutItem` já `FAILED` (`Notification.failed`) | `attribute_not_exists(PK) OR status = PENDING` | Outra entrega concluiu: `CONFLICT` |

### 4.5 Perfil de notificação — UC-11

- `PutItem` do item `USER#<user_id>` / `PROFILE`, com condição
  `attribute_not_exists(PK) OR updated_at < :occurred_at`.
- Perder a condição significa que o evento é igual ou mais antigo que o perfil gravado. O adapter informa isso como
  resultado simples, e o use case responde `Ok(applied=false)`. Duplicatas e mensagens fora de ordem ficam inofensivas.

---

## 5. Dados iniciais

Não há caso de uso de cadastro de eventos (EXT-07). Eventos, categorias e perfis de notificação entram por **seed**,
um script idempotente fora de `src/`. Os perfis do seed usam os mesmos `user_id` dos testes E2E, até a Etapa 9 passar
a criá-los pelo cadastro. Dados sintéticos em volume ficam com a skill `synthetic-data-generation`
(`AGENTS.md` §13).
