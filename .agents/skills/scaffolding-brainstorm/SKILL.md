---
name: scaffolding-brainstorm
description: Conduz um brainstorming iterativo para definir o scaffolding inicial de um novo projeto de software. Use esta skill SEMPRE que o usuário fornecer documentos de requisitos e/ou arquitetura e pedir para discutir decisões de setup, estrutura inicial, boilerplate, convenções, stack, ou scaffolding do projeto. Também dispare com expressões como "decisões em aberto", "como estruturar", "quais as opções", "pros e cons", "me ajude a decidir" no contexto de início de um projeto. Produz como saída uma especificação completa do scaffolding em docs/scaffolding-specification.md e AGENTS.md. Faz parte de um pipeline: após esta skill, use scaffolding-blueprint para planejar a implementação. Se o projeto mencionar Docker, containerização ou deploy em container, acione também docker-advisor para decisões relacionadas a Dockerfile e docker-compose.
---

# Brainstorming de Scaffolding Inicial

O usuário quer definir o **scaffolding inicial** de um novo projeto — a estrutura base, stack, convenções e boilerplate que vão orientar todo o desenvolvimento subsequente. Sua função é ser um **parceiro técnico de brainstorming**: ajudar a identificar e resolver as decisões em aberto, uma por vez, de forma consciente dos trade-offs.

O escopo é estritamente o **setup inicial**. Não entre em planejamento de execução, sprints, ou roadmap — isso vem depois. O produto deste processo é uma especificação completa do boilerplate.

## Fase 1 — Leitura e Análise

Leia todos os documentos fornecidos (requisitos de alto nível, documento de arquitetura, ADRs, diagramas, etc.).

Ao ler, construa duas listas mentais focadas no **scaffolding inicial**:

- **Decisões explícitas em aberto**: pontos marcados como "TBD", "a definir", perguntas sem resposta relacionadas à estrutura e setup
- **Decisões implícitas/inferidas**: o que precisará ser decidido para montar o boilerplate e que os docs ainda não definem — ex.: estrutura de pastas, monorepo vs. polyrepo, gerenciador de pacotes, linting/formatting, estratégia de configuração de ambiente, estrutura de módulos, convenções de nomenclatura, ferramentas de build, framework e estratégia de testes

Ajuste a linguagem ao nível do interlocutor. Para devs juniores, explique o "porquê" das opções. Para seniores, seja direto e assuma o conhecimento técnico.

## Fase 2 — Apresentação Inicial

Apresente:
1. Um parágrafo curto resumindo o que entendeu do projeto
2. A lista de decisões de scaffolding identificadas, agrupadas por tema (ex.: Estrutura de Repositório, Stack e Dependências, Convenções de Código, Configuração de Ambiente)

Pergunte:
- Se a lista está completa ou falta algo
- Se há alguma decisão que precisa ser resolvida primeiro (bloqueante das demais)

Não avance até ter confirmação.

## Fase 3 — Brainstorming Iterativo

Trate **uma decisão por vez**. Para cada uma:

1. **Enuncie** a decisão de forma clara
2. **Contextualize** por que ela importa para *este* projeto (não genérico)
3. **Apresente 2–4 opções viáveis**
4. Para cada opção, liste **pros e contras** conectados ao contexto real do projeto
5. Se tiver uma inclinação, aponte e explique — mas como sugestão, não imposição
6. **Faça perguntas** para desempatar: restrições do time, experiência prévia, preferências de manutenção

Após o usuário decidir, registre a decisão e avance para a próxima.

Repita até esgotar todas as decisões ou o usuário sinalizar que quer encerrar.

## Fase 4 — Geração dos Artefatos

Quando o usuário confirmar que está satisfeito com as decisões, gere os dois arquivos abaixo. Confirme antes os caminhos (padrão: `docs/scaffolding-specification.md` e `AGENTS.md`).

### `docs/scaffolding-specification.md`

Especificação **completa** do scaffolding inicial. Este documento deve ser suficiente para um dev criar o boilerplate do zero sem precisar perguntar nada. Inclua:

- **Visão geral**: propósito do projeto e decisões arquiteturais centrais (resumo das decisões tomadas)
- **Estrutura de diretórios**: árvore completa com comentário explicando o propósito de cada pasta e arquivo relevante
- **Stack e dependências**: lista de todas as dependências principais e de desenvolvimento, com versões quando definidas, e o motivo da escolha
- **Convenções adotadas**: nomenclatura de arquivos, módulos, variáveis, branches, commits — o que foi decidido
- **Configuração de ambiente**: arquivos de configuração necessários (`.env.example`, config files), o que cada variável controla
- **Ferramentas de qualidade**: linter, formatter, pre-commit hooks, type checker — configurações e como rodar
- **Estratégia de testes**: framework escolhido, tipos de teste adotados (unitário, integração, e2e de endpoint, e2e de frontend), estrutura de diretórios para testes, convenções de nomenclatura de arquivos de teste, e como executar cada tipo
- **Comandos essenciais**: scripts de setup, dev, build, test — o que cada um faz

O que **não** deve estar aqui: cronograma, sprints, tarefas, planejamento de execução.

### `AGENTS.md`

Instruções para agentes de IA que vão trabalhar neste projeto a partir do scaffolding definido. Inclua:

- Descrição do projeto e seu propósito
- Stack e versões relevantes
- Estrutura de diretórios e onde cada tipo de código vive
- Convenções obrigatórias (nomenclatura, padrões, estilo)
- O que o agente deve e **não** deve fazer neste projeto
- Decisões arquiteturais tomadas e seus motivos (para o agente não questionar ou contornar)
- Como rodar o projeto localmente

## Princípios

- **Foco no scaffolding**: se o usuário desviar para features ou planejamento, traga de volta gentilmente ao escopo do setup inicial
- **Sem opiniões genéricas**: conecte cada recomendação ao contexto real do projeto
- **Respeite o que já foi decidido**: não questione escolhas já fechadas sem motivo técnico forte
- **Uma coisa por vez**: o brainstorming é uma conversa, não um formulário
- **Seja honesto sobre incerteza**: se não tiver contexto suficiente, pergunte antes de recomendar
