---
name: reverse-engineering
description: Gera um FRD reverso a partir do código-fonte, ignorando especificações originais, e compara com o FRD original para identificar divergências. Use esta skill SEMPRE que o usuário pedir para fazer engenharia reversa, gerar FRD a partir do código, extrair regras de negócio do código, comparar implementação com especificação, ou auditar se o código reflete o que foi especificado. Também dispare com expressões como "engenharia reversa", "FRD reverso", "extraia as regras do código", "o que o código realmente faz?", "compare com o FRD original", "auditoria de implementação", "lógicas perdidas". Produz um FRD reverso e um relatório de divergências.
---

# Engenharia Reversa — FRD a partir do Código

O usuário quer fazer o caminho inverso: em vez de código a partir da especificação, extrair a especificação a partir do código. O objetivo é verificar a sanidade da implementação — o que o código **realmente faz** vs. o que **deveria fazer**.

Este é um exercício de auditoria. Você deve ler o código com "olhos cegos" — como se a especificação original não existisse.

## Fase 1 — Leitura do Código (Sem Especificação)

Leia **apenas** o código-fonte indicado pelo usuário. **Ignore qualquer FRD, Blueprint ou especificação fornecida nesta fase** — se estiverem disponíveis, você os usará apenas na Fase 3 para comparação.

Ao ler, extraia:

- **Regras de negócio**: condições, validações, cálculos, lógica condicional
- **Entidades e relacionamentos**: modelos de dados, seus campos e como se relacionam
- **Estados e transições**: se há máquina de estados, quais são os estados e transições implementados
- **Fluxos de operação**: o que acontece quando cada endpoint/função é chamado, passo a passo
- **Validações de entrada**: o que é aceito e rejeitado, com quais mensagens
- **Tratamento de erros**: o que acontece quando algo dá errado
- **Comportamentos implícitos**: lógica que existe no código mas não é óbvia (defaults, side effects, triggers)

Apresente um resumo do que encontrou e confirme com o usuário antes de avançar.

## Fase 2 — Geração do FRD Reverso

Gere um FRD completo baseado **exclusivamente** no que o código implementa. Use a mesma estrutura de um FRD convencional:

```markdown
# FRD Reverso — [Nome da Funcionalidade]

## 1. Visão Geral
Descrição do que a funcionalidade faz, inferida do código.

## 2. Atores
Quem interage, derivado dos endpoints/interfaces.

## 3. Requisitos Funcionais
Numerados (RF-R001, RF-R002...). Cada comportamento encontrado no código.

## 4. Regras de Negócio
Numeradas (RN-R001, RN-R002...). Cada regra/validação implementada.

## 5. Dados de Entrada
Campos, tipos, validações — conforme implementado.

## 6. Estados e Transições
Diagrama ou tabela — conforme implementado.

## 7. Tratamento de Erros
Cenários de erro encontrados e como são tratados.

## 8. Observações
Comportamentos ambíguos, lógica que parece incompleta, ou código morto.
```

O prefixo `R` nos IDs (RF-R001, RN-R001) distingue os requisitos reversos dos originais.

Salve em `docs/[nome-da-feature]/reverse-frd-[nome-da-feature].md`.

## Fase 3 — Comparação com FRD Original

Agora, e apenas agora, leia o FRD original. Compare os dois documentos e identifique:

### Lacunas (no FRD original mas não no código)
Regras ou requisitos que foram especificados mas não implementados. Podem ser:
- Features que ficaram de fora
- Regras de negócio ignoradas
- Validações ausentes

### Excessos (no código mas não no FRD original)
Lógica implementada que não está na especificação. Podem ser:
- Over-engineering
- Features não solicitadas
- Validações extras adicionadas "por precaução"

### Divergências (ambos existem mas diferem)
Requisitos que existem nos dois mas com comportamento diferente. Podem ser:
- Interpretações diferentes da mesma regra
- Bugs na implementação
- Evolução não documentada

Execute o diff entre os dois arquivos:
```bash
diff docs/[nome-da-feature]/frd-[nome-da-feature].md docs/[nome-da-feature]/reverse-frd-[nome-da-feature].md > docs/[nome-da-feature]/diferencas.txt
```

## Fase 4 — Relatório de Divergências

Apresente o relatório consolidado e salve junto ao FRD reverso:

```
## Relatório de Engenharia Reversa — [nome da funcionalidade]

### Resumo
- Requisitos no FRD original: X
- Requisitos inferidos do código: Y
- Lacunas (especificado, não implementado): N
- Excessos (implementado, não especificado): M
- Divergências (comportamento diferente): P

### Lacunas
| RF/RN Original | Descrição | Impacto |
|---------------|-----------|---------|
| RF-003 | Validação de estoque antes de adicionar ao carrinho | Alto — pode vender produto sem estoque |

### Excessos
| RF/RN Reverso | Descrição | Avaliação |
|--------------|-----------|-----------|
| RN-R007 | Limite de 99 itens por produto no carrinho | Não especificado — avaliar se é desejável |

### Divergências
| Original | Reverso | Diferença |
|----------|---------|-----------|
| RN-003: desconto máximo 30% | RN-R003: desconto máximo 50% | Valor limite diverge |

### Conclusão
Avaliação geral: a implementação está [fiel / parcialmente fiel / significativamente divergente] da especificação.
```

## Princípios

- **Olhos cegos na Fase 1**: leia o código sem consultar a especificação — a honestidade da engenharia reversa depende disso
- **Reporte, não corrija**: o produto é um diagnóstico, não uma correção; o usuário decide o que fazer com as divergências
- **Lacunas e excessos não são necessariamente erros**: uma lacuna pode ser intencional (feature para versão futura) e um excesso pode ser desejável (melhoria legítima)
- **Agnóstico de tecnologia e domínio**: adapte-se à stack e ao domínio do projeto
