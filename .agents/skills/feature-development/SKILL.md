---
name: feature-development
description: Implementa tarefas de um Blueprint técnico de funcionalidade, uma ou poucas por vez, seguindo o FRD como referência. Use esta skill SEMPRE que o usuário indicar tarefa(s) específica(s) de um Blueprint (T-001, T-002...) e pedir para implementar, codificar, desenvolver ou construir. Também dispare com expressões como "implemente a tarefa T-001", "desenvolva esta tarefa do blueprint", "codifique essa parte", "implemente a próxima tarefa", "execute as tarefas X e Y do blueprint". O usuário fornece o Blueprint e o FRD como contexto. Faz parte de um pipeline: antecedida por feature-blueprint, seguida por feature-review para revisão da implementação. O usuário seleciona tarefas progressivamente até completar o Blueprint.
---

# Implementação de Tarefas do Blueprint

O usuário está implementando uma funcionalidade tarefa por tarefa, seguindo um Blueprint técnico aprovado. Cada sessão cobre uma ou poucas tarefas selecionadas pelo usuário — não o Blueprint inteiro de uma vez.

O Blueprint é o plano. O FRD é a referência de comportamento. Seu papel é executar com precisão, testar, e entregar código funcionando.

## Fase 1 — Leitura e Contexto

Leia os documentos fornecidos:
- **Blueprint**: o plano técnico completo (modelos, interfaces, tarefas, dependências)
- **FRD**: a especificação funcional (RFs, RNs, edge cases, dados de entrada)

Identifique a(s) tarefa(s) que o usuário indicou (ex.: T-003, T-004). Para cada uma, extraia:
- O que precisa ser feito (do Blueprint)
- Onde: arquivos e módulos afetados
- Dependências: quais tarefas anteriores precisam estar concluídas
- Critérios de aceite: como verificar que está pronto (ligados a RF/RN do FRD)
- RFs e RNs relacionados: o comportamento esperado segundo o FRD

Se uma tarefa depende de outra que ainda não foi implementada, sinalize imediatamente.

## Fase 2 — Plano de Implementação

Apresente um plano detalhado para cada tarefa — **não código, apenas o plano**:

- **Arquivos a criar ou modificar**: caminhos reais, o que muda em cada um
- **Abordagem técnica**: como você vai implementar, seguindo os padrões e convenções do projeto
- **Lógica de negócio**: como as RNs relevantes serão traduzidas em código (resumo, não pseudo-código completo — o Blueprint já tem isso)
- **Edge cases**: como serão tratados os cenários da seção 7 do FRD que se aplicam a esta tarefa
- **Testes planejados**: quais testes serão escritos e o que cada um valida
  - Testes unitários: lógica isolada
  - Testes de integração: interação entre componentes
  - Testes e2e: fluxo completo (endpoints, frontend se aplicável)
- **Ordem de execução**: em que sequência os passos serão feitos

Pergunte: "O plano está alinhado? Posso implementar?"

**Não escreva código até receber aprovação.**

## Fase 3 — Implementação

Após aprovação, implemente seguindo o plano. Para cada passo:

- Anuncie o que vai fazer antes de fazer
- Crie ou modifique os arquivos conforme planejado
- Respeite rigorosamente as convenções do projeto (nomenclatura, estrutura de pastas, padrões de código definidos no Blueprint)
- Escreva os testes junto com o código — não deixe para depois

### Se precisar desviar do plano

Se durante a implementação você perceber que o plano precisa de ajuste (algo que não funcionou como esperado, uma dependência que faltou, uma abordagem melhor):
- Pare e explique o que mudou
- Proponha o ajuste
- Só prossiga após o usuário concordar

### Se ocorrer um erro

- Pare imediatamente
- Mostre o erro completo
- Explique a causa
- Proponha a correção antes de aplicá-la

## Fase 4 — Verificação

Após a implementação, execute as verificações:

### Compilação e build
Execute o build do projeto e confirme que não há erros de compilação introduzidos.

### Testes
Execute todos os testes escritos e mostre os resultados:
- **Testes unitários**: lógica isolada de cada componente criado ou modificado
- **Testes de integração**: interação entre as partes (ex.: service → repository → banco)
- **Testes e2e**: fluxo completo conforme os critérios de aceite da tarefa
  - Se há endpoints: teste as rotas com os inputs e outputs esperados
  - Se há frontend: teste o fluxo do usuário

Para cada teste, mostre: o que foi testado, o comando executado, e o resultado.

### Validação contra o FRD
Verifique que os critérios de aceite da tarefa (do Blueprint) foram atendidos, cruzando com os RFs e RNs correspondentes do FRD.

Se algum teste falhar, corrija antes de considerar a tarefa concluída.

## Fase 5 — Relatório da Tarefa

Apresente um resumo conciso:

- **Tarefa(s) concluída(s)**: IDs e títulos
- **O que foi criado/modificado**: lista de arquivos com o que mudou
- **Testes executados**: resultados (passou/falhou) com evidência
- **RFs/RNs atendidos**: quais requisitos e regras de negócio foram implementados
- **Desvios do plano**: se houve algum ajuste, o que e por quê
- **Próximas tarefas sugeridas**: com base nas dependências do Blueprint, quais tarefas estão desbloqueadas para a próxima sessão

## Princípios

- **Fiel ao Blueprint e ao FRD**: implemente o que foi planejado e especificado — não adicione features, refactors ou melhorias que não estão no escopo da tarefa
- **Plano antes de código**: nunca implemente sem aprovação do plano, mesmo que a tarefa pareça trivial
- **Testes não são opcionais**: cada tarefa entregue deve incluir testes que comprovem o funcionamento
- **Agnóstico de tecnologia e domínio**: adapte-se completamente à stack e ao domínio do projeto
- **Transparência**: erros, desvios e decisões implícitas são comunicados imediatamente
- **Escopo atômico**: cada sessão cobre as tarefas indicadas pelo usuário — não avance para tarefas seguintes sem ser solicitado
