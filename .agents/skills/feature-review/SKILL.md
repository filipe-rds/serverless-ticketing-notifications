---
name: feature-review
description: Revisa a implementação de uma funcionalidade comparando com o Blueprint técnico, o FRD e boas práticas da stack. Use esta skill SEMPRE que o usuário pedir para revisar, auditar, validar ou verificar o código de uma feature implementada, ou quiser checar se a implementação segue o Blueprint, o FRD, boas práticas ou está segura. Também dispare com expressões como "revise a feature", "revise a implementação da funcionalidade", "está conforme o blueprint?", "code review", "revise o código do carrinho", "valide a implementação", "audite o que foi feito". Faz parte do pipeline de features: executada após feature-development. Produz um relatório de revisão com findings categorizados por severidade e salvo em docs/[nome-da-feature]/review-[nome-da-feature].md.
---

# Revisão de Funcionalidade Implementada

O usuário quer validar a implementação de uma funcionalidade. Sua função é agir como um **revisor técnico independente**: comparar o código com o Blueprint e o FRD, verificar boas práticas, avaliar a cobertura de testes e apontar riscos de segurança — sem assumir que o que está no código está certo só porque foi gerado.

O produto desta skill é um **relatório de revisão** com findings acionáveis, não um refactor silencioso.

## Fase 1 — Leitura das Referências

Leia os documentos fornecidos:

**Blueprint técnico** — o plano de implementação aprovado:
- Modelos de dados, interfaces, componentes, lógica de negócio
- Tarefas (T-XXX) com critérios de aceite
- Testes planejados para cada tarefa
- Matriz de rastreabilidade RF/RN → Tarefas

**FRD** — a especificação funcional:
- Requisitos funcionais (RF-XXX)
- Regras de negócio (RN-XXX)
- Dados de entrada e validações
- Estados e transições
- Edge cases e tratamento de erros
- O que está fora do escopo

Se o usuário indicar tarefas específicas (ex.: "revise T-003 e T-004"), foque a revisão nessas tarefas. Caso contrário, revise toda a funcionalidade.

## Fase 2 — Inspeção do Código

Examine o código implementado. Leia os arquivos relevantes — não se limite a listar, entenda o conteúdo.

Inspecione:
- Arquivos criados ou modificados durante a implementação
- Modelos de dados (schema, entidades, migrations)
- Lógica de negócio (services, use cases, handlers)
- Interfaces (rotas, controllers, componentes de UI)
- Validações e tratamento de erros
- Testes escritos (unitários, integração, e2e)
- Configurações alteradas

## Fase 3 — Análise em Quatro Eixos

### Eixo 1 — Conformidade com o Blueprint

Compare a implementação com o que foi planejado:

- **Modelos de dados**: todos os campos, tipos, relacionamentos e validações do Blueprint foram implementados?
- **Interfaces**: cada endpoint/componente/handler definido existe e funciona conforme descrito (entrada, saída, comportamento, erros)?
- **Lógica de negócio**: cada RN foi traduzida em código conforme o pseudo-código do Blueprint?
- **Tarefas concluídas**: os critérios de aceite de cada tarefa (T-XXX) foram atendidos?
- **Desvios**: há algo implementado que não estava no Blueprint? Há algo do Blueprint que não foi implementado?

### Eixo 2 — Conformidade com o FRD

Cruze a implementação diretamente com o FRD:

- **Requisitos funcionais**: cada RF-XXX tem implementação correspondente que produz o comportamento esperado?
- **Regras de negócio**: cada RN-XXX está enforced no código? As condições estão corretas?
- **Dados de entrada**: validações de tipo, obrigatoriedade, formato e range estão implementadas conforme o FRD?
- **Estados e transições**: a máquina de estados (se aplicável) respeita o diagrama do FRD?
- **Edge cases**: cada cenário da seção "Edge Cases e Tratamento de Erros" do FRD tem tratamento no código?
- **Fora do escopo**: há algo implementado que o FRD definiu como fora do escopo?

### Eixo 3 — Boas Práticas e Qualidade de Código

Avalie contra boas práticas da stack do projeto:

**Estrutura e organização**
- O código segue as convenções do projeto (nomenclatura, organização de módulos, padrões)?
- Há separação clara de responsabilidades (não mistura lógica de negócio com infraestrutura)?
- Funções e métodos têm responsabilidades coesas?

**Tratamento de erros**
- Erros são tratados explicitamente (não engolidos silenciosamente)?
- Mensagens de erro são claras e identificam o problema?
- Falhas de dependências externas (banco, APIs) são tratadas?

**Testes**
- Testes unitários cobrem a lógica isolada de cada componente?
- Testes de integração validam a interação entre camadas?
- Testes e2e de endpoint testam as rotas com inputs válidos e inválidos?
- Testes e2e de frontend testam o fluxo do usuário (se aplicável)?
- Os testes passam? Execute-os e reporte o resultado nos findings
- Os testes cobrem os edge cases do FRD?
- Os testes planejados no Blueprint foram todos escritos?

**Performance** (quando relevante)
- Há queries N+1 ou operações desnecessariamente custosas?
- Índices de banco necessários foram criados?
- Há operações síncronas que deveriam ser assíncronas?

### Eixo 4 — Segurança

**Validação de inputs**
- Inputs do usuário são validados antes de processamento?
- Há proteção contra injection (SQL, NoSQL, command, XSS)?
- Dados sensíveis são sanitizados antes de log ou resposta?

**Autenticação e autorização**
- Endpoints/ações protegidos verificam autenticação?
- Permissões de papel (role) são validadas onde necessário?
- Há risco de IDOR (Insecure Direct Object Reference)?

**Exposição de dados**
- Respostas de API não expõem dados internos desnecessários (IDs internos, stack traces, dados de outros usuários)?
- Logs não contêm dados sensíveis (senhas, tokens, PII)?

## Fase 4 — Relatório de Revisão

Apresente os findings organizados por eixo e severidade.

### Severidades

- **CRÍTICO**: bug funcional que viola um RF/RN, risco de segurança imediato, ou teste falhando
- **ALTO**: lógica de negócio incorreta, edge case não tratado, teste ausente para cenário importante
- **MÉDIO**: desvio do Blueprint sem impacto funcional, prática não ideal, teste incompleto
- **BAIXO**: sugestão de melhoria, inconsistência menor, item de atenção futura

### Formato do relatório

```
## Relatório de Revisão — [nome da funcionalidade]

### Resumo
- Total de findings: X (Y críticos, Z altos, ...)
- Conformidade com o Blueprint: [Alta / Média / Baixa]
- Conformidade com o FRD: [Alta / Média / Baixa]
- Cobertura de testes: [Completa / Parcial / Insuficiente]
- Avaliação de segurança: [Sem riscos identificados / Riscos menores / Riscos críticos]

### Findings

#### [CRÍTICO] Título do finding
**Eixo**: Blueprint / FRD / Qualidade / Segurança
**Localização**: arquivo:linha ou módulo
**RF/RN relacionado**: RF-XXX ou RN-XXX (quando aplicável)
**Problema**: descrição clara do que está errado e por que importa
**Recomendação**: o que fazer para corrigir

#### [ALTO] ...
...

### Matriz de Cobertura
| RF/RN | Implementado? | Testado? | Observação |
|-------|--------------|----------|------------|
| RF-001 | Sim | Sim | — |
| RN-003 | Sim | Não | Falta teste de integração |
| RF-007 | Parcial | Não | Edge case X não tratado |

### O que está correto
Lista do que foi bem implementado — findings positivos também têm valor.

### Próximos passos sugeridos
Ordenados por prioridade: o que corrigir primeiro e por quê.
```

Salve o relatório em `docs/[nome-da-feature]/review-[nome-da-feature].md`.

## Fase 5 — Correções

Após apresentar o relatório, pergunte ao usuário se quer que você aplique as correções identificadas.

- Para findings **CRÍTICO** e **ALTO**: ofereça aplicar imediatamente
- Para findings **MÉDIO** e **BAIXO**: liste e deixe o usuário decidir o que priorizar

Aplique apenas o que o usuário autorizar. Para cada correção:
- Informe o que mudou
- Execute os testes afetados e confirme que passam
- Se a correção envolver novos testes, escreva-os

## Princípios

- **Revisor, não refatorador**: aponte o que está errado e por quê — não reescreva silenciosamente
- **Rastreável**: cada finding deve referenciar o RF/RN ou a tarefa do Blueprint que está sendo violada, quando aplicável
- **Específico, não genérico**: findings sem localização e sem recomendação concreta não ajudam ninguém
- **Positivos também importam**: um relatório só com problemas distorce a percepção — reconheça o que foi bem feito
- **Severidade honesta**: não infle criticidade para parecer mais rigoroso, nem minimize para não gerar atrito
- **Testes são evidência**: execute os testes existentes e use os resultados como evidência nos findings — não confie apenas na leitura do código
- **Agnóstico de tecnologia e domínio**: aplique os critérios da stack real do projeto, não de uma stack genérica imaginária
