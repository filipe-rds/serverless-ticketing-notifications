---
name: scaffolding-blueprint
description: Lê uma especificação de scaffolding e produz um Blueprint de desenvolvimento para revisão e aprovação antes da implementação começar. Use esta skill SEMPRE que o usuário fornecer uma especificação de scaffolding (scaffolding-specification.md ou equivalente) e pedir um plano, blueprint, roteiro ou análise do que implementar primeiro. Também dispare com expressões como "plano de desenvolvimento", "o que implementar primeiro", "Blueprint", "prova de saúde do fluxo", "end-to-end", "fluxo fim a fim", "me mostre o plano antes de começar". Produz um documento Blueprint para aprovação do usuário. Faz parte de um pipeline: antecedida por scaffolding-brainstorm, seguida por scaffolding-development. Se a spec ou o contexto mencionar Docker, containerização ou deploy em container, inclua etapas de Docker no Blueprint e acione docker-advisor para gerar Dockerfile e docker-compose com boas práticas.
---

# Blueprint de Desenvolvimento

O usuário quer, a partir de uma especificação de scaffolding, um **plano de desenvolvimento estruturado** para revisar e aprovar **antes** de qualquer linha de código ser escrita. Sua função é analisar a spec e propor um Blueprint claro, sequenciado e tecnicamente fundamentado.

O Blueprint tem dois objetivos simultâneos:
1. **Planejar a implementação de uma entidade de exemplo** — que percorre o fluxo completo do sistema (ex.: da interface ao banco de dados), servindo como prova da saúde da arquitetura
2. **Planejar a geração de dados de seed** — para popular o ambiente com dados representativos que permitam validar o fluxo

Este não é o momento de implementar. É o momento de pensar, alinhar e aprovar.

## Fase 1 — Leitura da Especificação

Leia o documento de scaffolding fornecido com atenção aos seguintes aspectos:

- **Stack e camadas**: quais tecnologias compõem cada camada (frontend, backend, banco de dados, etc.)
- **Estrutura de módulos/pastas**: como o código está organizado e onde cada responsabilidade vive
- **Convenções**: nomenclatura, padrões de arquivo, estilo de código definidos
- **Integrações e dependências externas**: o que o sistema depende para funcionar
- **Restrições e decisões arquiteturais**: o que já foi definido e não deve ser questionado

Se a spec for ambígua em algum ponto relevante para o plano, anote e pergunte ao usuário antes de avançar.

## Fase 2 — Identificação da Entidade de Exemplo

Identifique (ou confirme com o usuário) qual entidade do domínio será usada como **exemplo de implementação fim a fim**.

Esta entidade deve ser:
- **Simples o suficiente** para ser implementada rapidamente sem distração
- **Representativa o suficiente** para exercitar todas as camadas do sistema
- **Central ao domínio** — algo que faça sentido para o usuário validar

Se o usuário não especificou, sugira uma entidade com base no que você leu na spec e no domínio aparente do projeto. Confirme com o usuário antes de prosseguir.

## Fase 3 — Elaboração do Blueprint

Gere o Blueprint completo, tecnicamente fundamentado, **adaptado à stack e às convenções descritas na spec**. Nunca use nomes genéricos como "Tabela X" ou "Componente Y" — use os nomes e padrões reais do projeto.

O Blueprint deve conter as seguintes seções:

### 1. Visão Geral do Plano
- O que será implementado e por quê (propósito de cada parte)
- O que **não** está no escopo desta implementação inicial
- Critérios de sucesso: como saberemos que o fluxo está saudável?

### 2. Implementação da Entidade de Exemplo

Descreva cada etapa da implementação em ordem de execução, do banco de dados à interface (ou da interface ao banco, dependendo da arquitetura). Para cada etapa:

- **O que fazer**: descrição objetiva da tarefa
- **Onde**: arquivo(s) ou módulo(s) envolvidos, respeitando a estrutura da spec
- **Como**: abordagem técnica, respeitando as convenções e padrões definidos
- **Resultado esperado**: o que estará funcionando ao final desta etapa

As etapas devem cobrir o fluxo completo — da camada de persistência à camada de apresentação — sem pular nenhuma fronteira arquitetural.

### 3. Plano de Seed

Descreva como popular o sistema com dados de exemplo para validação. Inclua:

- **O que gerar**: quais entidades e quantos registros representativos
- **Onde fica o seed**: arquivo/módulo, conforme a estrutura da spec
- **Como executar**: comando ou mecanismo para rodar o seed
- **Dados representativos**: que tipos de variação os dados devem cobrir (sem ser dados reais ou sensíveis)

### 4. Plano de Testes

Descreva como configurar e executar testes para a entidade de exemplo. Estes testes servem como template para features futuras. Inclua:

- **Setup do framework**: o que instalar e configurar para rodar testes (conforme a spec)
- **Testes unitários**: o que testar isoladamente na lógica da entidade de exemplo (validações, transformações, regras)
- **Testes de integração**: quais interações entre camadas validar (ex.: service → repository → banco)
- **Testes e2e de endpoint**: se há API, testar as rotas da entidade com inputs e outputs esperados
- **Testes e2e de frontend**: se há interface, testar o fluxo do usuário (listagem, interação)
- **Como executar**: comandos para rodar cada tipo de teste

### 5. Sequência de Implementação

Lista numerada e ordenada de todas as tarefas, do início ao fim. Cada item deve ser atômico o suficiente para ser uma unidade de trabalho clara.

### 6. Pontos de Atenção

O que pode complicar a implementação com base na spec: dependências entre tarefas, configurações que precisam ser feitas antes, decisões que ainda precisam de confirmação.

## Fase 4 — Revisão e Aprovação

Após apresentar o Blueprint, pergunte explicitamente:

> "Este plano está alinhado com o que você espera? Há algo que quer ajustar, adicionar ou remover antes de começar a implementação?"

Não avance para nenhuma implementação até receber aprovação explícita. Se o usuário pedir ajustes, revise o Blueprint e apresente novamente.

## Fase 5 — Persistência do Blueprint

Após aprovação, salve o Blueprint em `docs/scaffolding-blueprint.md`.

Este arquivo é o **handoff para a sessão de implementação** — outra sessão de IA (ou outro dev) deve conseguir executar o plano integralmente a partir deste documento, sem precisar consultar outros arquivos ou fazer perguntas.

Para garantir isso, o arquivo deve ser **autocontido**. Inclua:

- **Contexto do projeto**: stack, estrutura de pastas relevante, convenções adotadas — o suficiente para não precisar ler a spec de scaffolding
- **Entidade de exemplo escolhida** e por que ela foi escolhida
- **Critérios de sucesso** claros e verificáveis
- **Todas as etapas da implementação** com: o que fazer, onde (caminhos reais de arquivo/módulo), como (abordagem técnica com os padrões do projeto), e o resultado esperado
- **Plano de seed** completo: o que gerar, onde fica o arquivo, como executar
- **Sequência de implementação** numerada e ordenada
- **Pontos de atenção** e dependências entre tarefas
- **O que está fora do escopo** desta implementação inicial

Não omita detalhes por economia de espaço. O objetivo é que quem executar este plano nunca precise adivinhar nada.

## Princípios

- **Agnóstico de tecnologia e domínio**: o Blueprint se molda à stack e ao domínio do projeto lido na spec — nunca assuma uma tecnologia que não foi definida
- **Fiel à spec**: respeite rigorosamente as convenções, estruturas e decisões definidas no scaffolding
- **Planejar antes de fazer**: o produto desta skill é um documento para aprovação, não código
- **Clareza sobre escopo**: deixe explícito o que está e o que não está no plano
- **Sem ambiguidade**: se a spec não deixar claro algo relevante para o plano, pergunte antes de assumir
