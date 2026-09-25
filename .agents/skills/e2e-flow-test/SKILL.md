---
name: e2e-flow-test
description: Cria e executa testes E2E que percorrem fluxos completos do sistema de ponta a ponta, do frontend à persistência, baseados no FRD e diagramas de estado. Use esta skill SEMPRE que o usuário pedir para criar testes E2E completos, testar fluxos fim a fim, validar o fluxo de compras, ou garantir que o sistema funciona de ponta a ponta. Também dispare com expressões como "testes E2E completos", "teste o fluxo inteiro", "E2E de ponta a ponta", "valide o fluxo", "teste fim a fim", "fluxo completo de compras", "E2E do frontend ao banco". Produz testes e um relatório em docs/[nome-da-feature]/e2e-report-[nome-da-feature].md. Faz parte do pipeline de features: pode ser acionada após feature-development ou após feature-review, quando os fluxos completos precisam de validação de ponta a ponta.
---

# Testes E2E de Fluxos Completos

O usuário quer validar que os fluxos completos do sistema funcionam de ponta a ponta — do frontend (ou ponto de entrada) até a persistência no banco, passando por todas as camadas intermediárias. Estes são os testes no topo da pirâmide: os mais custosos, mas os únicos que validam a integração real entre todas as partes.

## Fase 1 — Leitura e Mapeamento de Fluxos

Leia os documentos fornecidos:

**Especificações** — FRD, diagramas de estado, Blueprint (o que estiver disponível):
- Fluxos de negócio descritos (ex.: adicionar produto → aplicar cupom → finalizar compra → gerar pedido)
- Transições de estado e suas condições
- Edge cases e cenários de erro

**Código existente** — para entender como os fluxos estão implementados:
- Endpoints de API disponíveis
- Componentes de frontend (se houver)
- Lógica de negócio e validações

Mapeie todos os **fluxos críticos** — sequências de ações que um usuário real executaria e que exercitam múltiplas camadas do sistema. Para cada fluxo:
- Nome descritivo
- Passos em sequência (do início ao fim)
- Resultado esperado ao final
- Dados necessários (seeds, estado inicial)

Apresente a lista de fluxos identificados e confirme com o usuário antes de avançar.

## Fase 2 — Plano de Testes E2E

Apresente o plano **sem código** para aprovação:

### Para cada fluxo E2E
- **Nome do fluxo**: descritivo e claro
- **Pré-condições**: dados que precisam existir, estado inicial do sistema
- **Passos**: sequência de ações (requests HTTP, interações de frontend)
- **Verificações por passo**: o que confirmar em cada etapa (status code, estado no banco, resposta, UI)
- **Verificação final**: estado esperado do sistema ao término do fluxo completo
- **Cenários de erro**: o que acontece quando uma etapa falha no meio do fluxo

### Setup e infraestrutura
- Banco de teste: como preparar e limpar entre testes
- Seeds necessários: quais dados pré-existentes cada fluxo requer
- Ferramentas: biblioteca de teste E2E adequada à stack
- Isolamento: como garantir que testes não interferem uns nos outros

Pergunte: "O plano está alinhado? Posso implementar?"

**Não escreva código até receber aprovação.**

## Fase 3 — Implementação

Após aprovação, implemente na seguinte ordem:

1. **Setup de infraestrutura**: configuração do banco de teste, fixtures, helpers
2. **Seeds específicos dos fluxos**: dados de pré-condição para cada cenário
3. **Testes E2E de endpoint**: percorrem o fluxo via API, verificando responses e estado do banco
4. **Testes E2E de frontend**: percorrem o fluxo via interface, verificando interações e resultados visuais (se aplicável)

Para cada teste:
- Anuncie o que vai escrever
- Execute após escrever — não acumule
- Se falhar, identifique se é bug no teste ou no código e sinalize

### Se um teste revelar um bug no sistema

- Pare e sinalize: "O teste E2E revelou um bug: [descrição]"
- Proponha a correção
- Só aplique após autorização
- Registre para o relatório

## Fase 4 — Verificação

Execute toda a suíte E2E e mostre resultados consolidados:

- **Total de fluxos testados**: X
- **Passando**: Y
- **Falhando**: Z (com detalhes)
- **Bugs encontrados**: lista

Cruze com a especificação:
- Cada fluxo crítico do FRD/diagrama de estados está coberto?
- Cenários de erro foram exercitados?

Mostre evidências: comandos executados e outputs.

## Fase 5 — Relatório

Salve o relatório em `docs/[nome-da-feature]/e2e-report-[nome-da-feature].md`.

```
## Relatório E2E — [nome da funcionalidade]

### Resumo
- Fluxos testados: X
- Testes passando: Y
- Testes falhando: Z
- Bugs encontrados: N

### Fluxos Cobertos
| Fluxo | Passos | Status | Observação |
|-------|--------|--------|------------|
| Compra completa | 6 | Passando | — |
| Compra com cupom inválido | 4 | Passando | — |

### Bugs Encontrados
Lista com localização e status.

### Cenários Não Cobertos
Fluxos que não puderam ser testados (e por quê).

### Arquivos Criados
Lista de arquivos de teste com propósito.
```

## Princípios

- **Fluxos reais, não fragmentos**: cada teste E2E percorre um fluxo completo — não testa operações isoladas (para isso existem testes unitários e de integração)
- **Plano antes de código**: nunca implemente sem aprovação do plano
- **Bugs são achados, não escondidos**: se o teste revela um bug, sinalize
- **Seeds explícitos**: cada teste declara seus dados de pré-condição — nada implícito
- **Agnóstico de tecnologia e domínio**: adapte-se à stack e ao domínio do projeto
