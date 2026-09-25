# Documentação — ticketstream

Mapa dos documentos do projeto, a ordem de leitura e o procedimento para evoluir o sistema.

## Documentos

| Documento | Responde | Natureza |
|---|---|---|
| [`project_base.md`](project_base.md) | O que foi pedido? | **Enunciado original.** Não é editado. |
| [`requirements.md`](requirements.md) | Como cada pedido é atendido, que decisões foram tomadas e o que fica para depois? | Rastreabilidade, decisões, backlog |
| [`domain.md`](domain.md) | Quais são as entidades, as regras e os estados? | Modelo de domínio |
| [`use_cases.md`](use_cases.md) | O que cada caso de uso recebe, valida, devolve e como falha? | Especificação funcional |
| [`contracts.md`](contracts.md) | Qual é o formato exato do que entra e sai do sistema? | Contratos HTTP e SQS |
| [`persistence.md`](persistence.md) | Como os dados ficam no DynamoDB e como a concorrência é garantida? | Modelo físico |
| [`architecture.md`](architecture.md) | Como o sistema roda na AWS e no MiniStack? | Visão de execução |
| [`../AGENTS.md`](../AGENTS.md) | Como o código é organizado e como o trabalho é conduzido? | **Normativo** |

Ordem de leitura sugerida: `project_base` → `requirements` → `domain` → `use_cases` → `contracts` → `persistence` →
`architecture`.

## Precedência

1. **`AGENTS.md` prevalece sobre todos os demais.** Ele fixa a arquitetura de código, o modo de trabalho e o mapa
   normativo de erro para HTTP (§8.2).
2. `requirements.md` registra as decisões que interpretam o enunciado. Quando uma decisão diverge do `project_base.md`,
   a divergência é explícita e justificada ali (DEC-32 reúne as de modelagem).
3. `domain.md` e `use_cases.md` são a fonte das regras de negócio, dentro dos limites do `AGENTS.md`. `contracts.md`,
   `persistence.md` e `architecture.md` derivam deles.

Uma divergência entre documento e código é registrada em
[Dívidas conhecidas](../AGENTS.md#dívidas-conhecidas), não corrigida em silêncio.

## Identificadores

Todo item referenciável tem um ID estável. Um ID removido não é reaproveitado.

| Prefixo | Significado | Onde vive |
|---|---|---|
| `REQ-xx` | Requisito extraído do enunciado | `requirements.md` |
| `DEC-xx` | Decisão de interpretação ou de projeto | `requirements.md` |
| `QA-xx` | Questão em aberto | `requirements.md` |
| `EXT-xx` | Extensão planejada (backlog) | `requirements.md` |
| `INV-<AGG>-xx` | Invariante de domínio (`GL` = global) | `domain.md` |
| `UC-xx` | Caso de uso | `use_cases.md` |
| `AP-xx` | Padrão de acesso ao banco | `persistence.md` |
| `D1`–`D12` | Decisão arquitetural fixada | `AGENTS.md` §3 |
| Dívida `#n` | Divergência conhecida entre documento e código | `AGENTS.md` §10 |

Lacunas na numeração (por exemplo, dívidas 3, 11, 13…) são IDs já resolvidos ou retirados, nunca reaproveitados.

## Como adicionar uma funcionalidade

1. **Registrar a origem.** Novo pedido vira `EXT-xx` (ou `REQ-xx`, se vier de um enunciado) em `requirements.md`.
   Decisões tomadas no caminho viram `DEC-xx`.
2. **Modelar o domínio.** Atributos, estados e invariantes novos entram em `domain.md` com IDs próprios.
3. **Especificar o caso de uso.** Novo `UC-xx` em `use_cases.md`, seguindo o [modelo](use_cases.md#modelo-de-caso-de-uso).
   Todo erro precisa de família e destino (HTTP ou SQS).
4. **Fixar os contratos.** Endpoint ou mensagem nova entra em `contracts.md`. Mudança incompatível em mensagem
   exige nova versão.
5. **Desenhar o acesso a dados.** Padrão de acesso novo entra em `persistence.md`, junto com a condição atômica que o
   protege, se houver.
6. **Implementar como fatia vertical.** Seguir `AGENTS.md` §8 e o pipeline de skills do §13, com o ciclo de
   [DEC-25](requirements.md#dec-25--ciclo-de-uma-fatia-e-pirâmide-de-testes):
   1. teste unitário vermelho;
   2. implementação;
   3. integração com `moto`;
   4. função no `template.yaml` e E2E no MiniStack.
