---
name: feature-blueprint
description: Lê um FRD e documentos de arquitetura e produz um Blueprint técnico detalhado para implementação de uma funcionalidade. Use esta skill SEMPRE que o usuário fornecer um FRD (ou requisitos funcionais equivalentes) junto com documentos de arquitetura, diagramas de estado, ou contexto técnico do projeto, e pedir para planejar a implementação, criar um blueprint técnico, detalhar tarefas, definir schemas, ou especificar o caminho de implementação. Também dispare com expressões como "gere um blueprint", "plano técnico", "blueprint de implementação", "como implementar essa feature", "detalhe as tarefas", "especifique os schemas", "caminho' de implementação", "planeje o desenvolvimento desta funcionalidade". Produz como saída um Blueprint técnico autocontido em docs/[nome-da-feature]/blueprint-[nome-da-feature].md. Faz parte de um pipeline: antecedida por feature-spec-brainstorm, seguida por feature-development para implementação tarefa a tarefa.
---

# Blueprint Técnico de Funcionalidade

O usuário quer transformar um FRD aprovado em um **plano técnico de implementação** — detalhado o suficiente para que outra sessão de IA (ou outro dev) execute a feature integralmente, sem precisar interpretar requisitos ou tomar decisões arquiteturais.

A diferença entre este skill e o `scaffolding-blueprint` é o ponto de partida: aqui o projeto já existe, a arquitetura já está definida, e o objetivo é planejar a implementação de uma **funcionalidade específica** dentro desse contexto.

## Fase 1 — Leitura e Compreensão

Leia todos os documentos fornecidos: FRD, documentos de arquitetura, diagramas de estado, e qualquer outro contexto.

Construa dois mapas mentais simultâneos:

**Mapa funcional** (do FRD):
- Requisitos funcionais (RF-XXX) e suas condições
- Regras de negócio (RN-XXX) e suas prioridades
- Dados de entrada: campos, tipos, validações, origens
- Estados e transições: diagrama completo
- Edge cases e tratamentos de erro
- O que está fora do escopo

**Mapa técnico** (da arquitetura):
- Componentes existentes e suas responsabilidades
- Camadas do sistema e como se comunicam
- Stack, linguagens, frameworks e versões
- Convenções de código, nomenclatura, organização de módulos
- Padrões já estabelecidos que esta feature deve seguir

Apresente um resumo curto do que entendeu: a feature em uma frase, o contexto arquitetural relevante, e qualquer ponto que ficou ambíguo. Confirme com o usuário antes de avançar.

## Fase 2 — Decomposição Técnica

Traduza o FRD em building blocks técnicos, **adaptados à arquitetura real do projeto**. Não use termos genéricos — use os nomes, padrões e convenções que existem no projeto.

### 2.1 Modelos de Dados

Para cada entidade envolvida na funcionalidade:
- Atributos, tipos, obrigatoriedade, valores padrão
- Relacionamentos com outras entidades (existentes ou novas)
- Validações derivadas das regras de negócio
- Mapeamento explícito: cada campo → RF ou RN que o origina

A nomenclatura se adapta à stack: podem ser tabelas SQL, document schemas, interfaces TypeScript, structs, protobuf messages, dataclasses — o que o projeto usar.

### 2.2 Componentes e Módulos

Identifique quais partes do sistema serão criadas ou modificadas:
- Novos módulos a criar e onde vivem na estrutura de pastas
- Módulos existentes que precisam de alteração
- Para cada um: qual sua responsabilidade e quais RFs/RNs ele atende

### 2.3 Interfaces

O que a funcionalidade expõe ou consome. A natureza depende da arquitetura — podem ser:
- Endpoints de API (REST, GraphQL, gRPC)
- Comandos CLI
- Telas ou componentes de UI
- Eventos publicados/consumidos (Kafka, SQS, WebSocket)
- Funções ou métodos em bibliotecas internas
- Qualquer outro ponto de contato

Para cada interface:
- **Entrada**: o que recebe, formato, validações
- **Saída**: o que retorna, formato
- **Comportamento**: o que acontece internamente (resumo)
- **Erros**: o que pode falhar e como é comunicado

### 2.4 Gestão de Estado

Como os estados definidos no FRD se traduzem tecnicamente:
- Onde o estado é armazenado (campo em tabela, máquina de estados, workflow engine, etc.)
- Quais ações disparam cada transição
- Guardas: condições que impedem uma transição
- O que acontece com entidades em estados intermediários durante operações concorrentes

### 2.5 Lógica de Negócio

Para cada regra de negócio complexa (RN-XXX), escreva pseudo-código ou uma descrição algorítmica:
- Inputs da regra
- Lógica de decisão (if/else, cálculos, validações compostas)
- Output e side effects
- Onde na arquitetura essa lógica vive (qual camada, módulo, serviço)

Apresente a decomposição completa e pergunte: "A decomposição técnica está alinhada? Algo precisa de ajuste antes de eu planejar as tarefas?"

Não avance sem confirmação.

## Fase 3 — Planejamento de Tarefas

Converta a decomposição em tarefas numeradas, sequenciadas e com dependências explícitas.

Para cada tarefa:
- **ID**: T-001, T-002...
- **Título**: descrição concisa
- **O que**: o que precisa ser construído ou alterado
- **Onde**: arquivos e módulos afetados (caminhos reais quando conhecidos)
- **Dependências**: IDs das tarefas que precisam estar concluídas antes (T-XXX)
- **Critério de aceite**: como verificar que a tarefa está feita — vinculado a RF/RN específicos
- **Testes planejados**: para cada tarefa, quais testes escrever:
  - Unitários: o que testar isoladamente (lógica, validações, transformações)
  - Integração: quais interações entre componentes validar
  - E2e: endpoint e/ou frontend, conforme aplicável à tarefa
- **Complexidade**: Baixa / Média / Alta

Agrupe as tarefas em **fases de implementação**. A ordem das fases se adapta à arquitetura — não existe uma sequência fixa. Em um projeto com API REST pode ser "modelos → lógica → endpoints → testes". Em um pipeline de dados pode ser "ingestão → transformação → output → monitoramento". Em um app mobile pode ser "state management → UI → integração → testes". Siga o que faz sentido para o projeto.

Inclua também tarefas que não são código mas são necessárias: migrations, seeds, configurações de ambiente, atualizações de documentação, setup de testes.

Apresente e confirme.

## Fase 4 — Autovalidação

Antes de finalizar, faça um cross-reference sistemático do Blueprint contra o FRD. Este passo existe para pegar o que escapou — trate-o com rigor.

### Checklist de validação

**Matriz de rastreabilidade**
Apresente uma tabela: cada RF-XXX e RN-XXX do FRD → ID(s) da(s) tarefa(s) correspondente(s). Se algum requisito não tem tarefa associada, é um gap que precisa ser resolvido.

**Completude dos modelos de dados**
Cada campo mencionado em "Dados de Entrada" e cada estado mencionado em "Estados e Transições" do FRD deve aparecer nos modelos. Campos faltando = gap.

**Consistência da lógica de negócio**
Cada pseudo-código deve implementar fielmente a RN correspondente. Contradições entre o pseudo-código e a regra de negócio = erro a corrigir.

**Cobertura de edge cases**
Cada cenário da seção "Edge Cases e Tratamento de Erros" do FRD deve ter tratamento explícito em alguma tarefa. Cenários não cobertos = gap.

**Dependências entre tarefas**
Verificar: há dependências circulares? Tarefas órfãs (sem dependência mas que deveriam ter)? Prerequisites faltando?

**Cobertura de testes**
Cada tarefa tem testes planejados para os níveis aplicáveis (unitário, integração, e2e)? Tarefas que alteram lógica de negócio sem testes planejados = gap.

**Tarefas esquecidas**
Com base na arquitetura, há algo que o plano não contemplou? Considere: migrations de banco, alterações de configuração, setup de testes, atualização de documentação, alterações em CI/CD, impacto em funcionalidades existentes.

Se houver gaps, proponha as correções. Apresente os resultados da validação e peça aprovação final antes de persistir.

## Fase 5 — Persistência do Blueprint

Após aprovação, salve o Blueprint em `docs/[feature-name]/blueprint-[feature-name].md`.

O documento deve ser **autocontido**. Quem executar não pode precisar consultar o FRD, os docs de arquitetura, ou qualquer outro arquivo. Inclua todo o contexto necessário dentro do próprio Blueprint.

### Estrutura do documento

```markdown
# Blueprint Técnico — [Nome da Funcionalidade]

## 1. Contexto
- Resumo da funcionalidade e qual problema resolve
- Arquitetura do sistema (partes relevantes)
- Stack, versões e convenções do projeto
- Premissas técnicas adotadas

## 2. Modelos de Dados
(entidades, atributos, tipos, relacionamentos, validações, mapeamento RF/RN)

## 3. Componentes e Módulos
(criações e modificações, responsabilidades, mapeamento RF/RN)

## 4. Interfaces
(cada interface com entrada, saída, comportamento, erros)

## 5. Gestão de Estado
(estados, transições, guardas, concorrência)

## 6. Lógica de Negócio
(pseudo-código para cada RN complexa, localização na arquitetura)

## 7. Tarefas de Implementação
(T-001... agrupadas por fase, com dependências, critérios de aceite e testes planejados)

## 8. Matriz de Rastreabilidade
(tabela RF/RN → Tarefas | tabela Edge Case → Tratamento)

## 9. Riscos e Pontos de Atenção
(dependências críticas, decisões técnicas em aberto, o que pode complicar)

## 10. Fora do Escopo Técnico
(o que o FRD define mas não será implementado nesta iteração, e por quê)
```

## Princípios

- **Fiel ao FRD**: o Blueprint implementa o que o FRD especifica — nem mais, nem menos. Se algo que o FRD exige não parece viável tecnicamente, sinalize em vez de omitir
- **Agnóstico de tecnologia e domínio**: adapte-se à arquitetura real do projeto; não assuma REST + SQL se o projeto é um CLI em Go com arquivos locais
- **Autocontido**: o Blueprint deve ser legível e executável sem consultar outros documentos
- **Rastreável**: cada tarefa deve apontar para um requisito; cada requisito deve ter pelo menos uma tarefa — a matriz de rastreabilidade é obrigatória, não opcional
- **Iterativo**: apresente cada fase para revisão antes de avançar; não despeje o Blueprint completo de uma vez
- **Sem ambiguidade**: se a arquitetura ou o FRD deixam algo incerto que afeta o plano técnico, pergunte antes de assumir
