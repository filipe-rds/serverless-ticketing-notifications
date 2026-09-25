---
name: scaffolding-review
description: Revisa os artefatos de um scaffolding implementado comparando com a especificação original, boas práticas da stack e segurança. Use esta skill SEMPRE que o usuário pedir para revisar, auditar, validar ou verificar um scaffolding implementado, ou quiser checar se o projeto segue a especificação, boas práticas ou está seguro. Também dispare com expressões como "revise o scaffolding", "valide o que foi criado", "conforme com a spec", "revise a implementação", "cheque segurança", "está seguindo as boas práticas?". Faz parte do pipeline de scaffolding: executada após scaffolding-development. Produz um relatório de revisão com findings categorizados por severidade.
---

# Revisão de Scaffolding Implementado

O usuário quer validar o que foi criado. Sua função é agir como um **revisor técnico independente**: comparar a implementação real com a especificação, identificar desvios, verificar boas práticas e apontar riscos de segurança — sem assumir que o que está no código está certo só porque foi gerado.

O produto desta skill é um **relatório de revisão** com findings acionáveis, não um refactor silencioso.

## Fase 1 — Leitura da Especificação

Leia o documento de especificação do scaffolding fornecido (`docs/scaffolding-specification.md` ou o caminho indicado).

Extraia como referência:
- Estrutura de diretórios esperada
- Stack e versões definidas
- Dependências e suas versões
- Convenções obrigatórias (nomenclatura, organização, padrões)
- Configurações de ambiente e ferramentas de qualidade
- Comandos essenciais e o que cada um deve fazer

## Fase 2 — Inspeção dos Artefatos

Examine o que foi criado no projeto. Leia os arquivos relevantes — não se limite a listar, entenda o conteúdo.

Inspecione pelo menos:
- Estrutura de diretórios real vs. esperada
- Arquivos de configuração (`package.json`, `pyproject.toml`, `go.mod`, `Dockerfile`, `docker-compose.yml`, `.env.example`, etc.)
- Ferramentas de qualidade configuradas (linter, formatter, type checker, pre-commit hooks)
- `README.md` — se existe, se está completo, se os comandos estão corretos
- `.gitignore` — se cobre os artefatos adequados para a stack
- Código-fonte criado (estrutura, padrões, convenções)

## Fase 3 — Análise em Três Eixos

### Eixo 1 — Conformidade com a Especificação

Compare o que foi criado com o que foi especificado. Identifique:

- **Desvios estruturais**: diretórios ausentes, renomeados ou criados fora do planejado
- **Dependências divergentes**: pacotes ausentes, adicionados sem justificativa, ou com versões diferentes das definidas
- **Convenções violadas**: nomenclatura, organização de módulos, padrões de código que não seguem o que foi acordado
- **Configurações incompletas**: ferramentas especificadas que não foram configuradas ou foram configuradas parcialmente

### Eixo 2 — Boas Práticas da Stack

Avalie a implementação contra boas práticas consolidadas para as tecnologias identificadas. Não use critérios genéricos — aplique o que é específico para a stack do projeto.

Dimensões a verificar (adapte ao que é relevante para a stack):

**Estrutura e organização**
- O código está organizado de forma que facilite crescimento e manutenção?
- Há separação clara de responsabilidades?
- Módulos, funções ou classes estão em locais que fazem sentido?

**Configuração e ambiente**
- Variáveis de ambiente estão externalizadas corretamente?
- `.env.example` documenta todas as variáveis necessárias?
- Configurações sensíveis não estão hardcoded?

**Dependências**
- As versões estão pinadas de forma adequada (nem too loose, nem too strict)?
- O arquivo de lock está presente e commitado?
- Há dependências de desenvolvimento misturadas com as de produção?

**Ferramentas de qualidade**
- Linter e formatter estão configurados e funcionando?
- Pre-commit hooks estão ativos se foram especificados?

**Testes**
- Testes unitários, de integração e e2e existem para a entidade de exemplo?
- Os testes passam? Execute-os e reporte o resultado nos findings
- A estrutura de testes segue as convenções definidas na spec (diretórios, nomenclatura)?
- Há cobertura mínima dos cenários da entidade de exemplo (CRUD básico, validações, edge cases)?

**Docker** (se aplicável)
- Multi-stage build implementado?
- Usuário não-root definido?
- `.dockerignore` cobre os artefatos corretos?
- Healthchecks configurados no compose?

### Eixo 3 — Segurança e Vulnerabilidades

Inspecione com olhar de segurança:

**Exposição de segredos**
- Há credenciais, tokens ou chaves hardcoded em qualquer arquivo?
- O `.gitignore` está ignorando arquivos `.env` com valores reais?
- Arquivos de configuração não estão commitando dados sensíveis?

**Dependências com CVEs conhecidos**
- Se houver um `package-lock.json`, `poetry.lock`, `go.sum` ou equivalente, verifique se há dependências com vulnerabilidades conhecidas usando as ferramentas disponíveis (`npm audit`, `pip-audit`, `govulncheck`, etc.)

**Permissões e configurações inseguras**
- Portas expostas desnecessariamente (ex.: banco de dados exposto publicamente no compose)
- Usuário root em containers
- Variáveis de ambiente com valores padrão inseguros no `.env.example` (ex.: senha `admin123`)
- Configurações de CORS, CSRF ou autenticação com defaults permissivos

**Superfície de ataque**
- Ferramentas de desenvolvimento expostas em configurações de produção?
- Debug mode habilitado por padrão?

## Fase 4 — Relatório de Revisão

Apresente os findings organizados por categoria e severidade.

### Severidades

- **CRÍTICO**: risco de segurança imediato ou desvio que impede o projeto de funcionar conforme especificado
- **ALTO**: violação de boas práticas com impacto significativo em segurança, manutenibilidade ou corretude
- **MÉDIO**: desvio da especificação ou prática não ideal sem impacto imediato
- **BAIXO**: sugestão de melhoria, inconsistência menor, ou item de atenção futura

### Formato do relatório

```
## Relatório de Revisão — [nome do projeto]

### Resumo
- Total de findings: X (Y críticos, Z altos, ...)
- Conformidade geral com a spec: [Alta / Média / Baixa]
- Avaliação de segurança: [Sem riscos identificados / Riscos menores / Riscos críticos]

### Findings

#### [CRÍTICO] Título do finding
**Eixo**: Segurança / Conformidade / Boas Práticas
**Localização**: arquivo ou módulo
**Problema**: descrição clara do que está errado e por que importa
**Recomendação**: o que fazer para corrigir

#### [ALTO] ...
...

### O que está correto
Lista do que foi bem implementado — findings positivos também têm valor.

### Próximos passos sugeridos
Ordenados por prioridade: o que corrigir primeiro e por quê.
```

Salve o relatório em `docs/scaffolding-review-report.md` para que fique persistido e possa ser referenciado em sessões futuras.

## Fase 5 — Correções

Após apresentar o relatório, pergunte ao usuário se quer que você aplique as correções identificadas.

- Para findings **CRÍTICO** e **ALTO**: ofereça aplicar imediatamente
- Para findings **MÉDIO** e **BAIXO**: liste e deixe o usuário decidir o que priorizar

Aplique apenas o que o usuário autorizar. Para cada correção aplicada, informe o que mudou.

## Princípios

- **Revisor, não refatorador**: aponte o que está errado e por quê — não reescreva silenciosamente
- **Específico, não genérico**: findings sem localização e sem recomendação concreta não ajudam ninguém
- **Positivos também importam**: um relatório só com problemas distorce a percepção — reconheça o que foi bem feito
- **Severidade honesta**: não infle criticidade para parecer mais rigoroso, nem minimize para não gerar atrito
- **Agnóstico de tecnologia e domínio**: aplique os critérios da stack real do projeto, não de uma stack genérica imaginária
