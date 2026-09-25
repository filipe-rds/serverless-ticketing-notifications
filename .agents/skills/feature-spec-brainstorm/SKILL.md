---
name: feature-spec-brainstorm
description: Conduz um brainstorming iterativo para fechar o escopo de uma funcionalidade e produz um FRD (Functional Requirements Document). Use esta skill SEMPRE que o usuário fornecer requisitos de alto nível, diagramas de estado, ou descrição de uma feature e pedir para discutir escopo, levantar perguntas, especificar regras de negócio, ou fechar requisitos funcionais. Também dispare com expressões como "faça perguntas críticas", "fechar escopo", "especificar a funcionalidade", "levantar requisitos", "escrever o FRD", "definir regras de negócio", "o que precisa estar claro antes de implementar". Produz como saída um FRD completo em docs/[nome-da-feature]/frd-[nome-da-feature].md. Faz parte de um pipeline: após esta skill, use feature-blueprint para planejar a implementação técnica da funcionalidade.
---

# Brainstorming e Especificação de Funcionalidade (FRD)

O usuário quer fechar o escopo de uma funcionalidade antes de implementá-la. Sua função é fazer as perguntas certas para eliminar ambiguidades, identificar edge cases e regras de negócio não documentadas — e ao final consolidar tudo em um FRD que sirva como contrato entre produto e engenharia.

O produto desta skill é clareza, não código.

## Fase 1 — Leitura dos Documentos

Leia todos os documentos fornecidos: requisitos de alto nível, diagramas de estado, wireframes, ADRs, ou qualquer outro contexto disponível.

Ao ler, mapeie:
- **O que está definido**: regras e comportamentos explícitos
- **O que está implícito mas não documentado**: comportamentos assumidos que precisam de confirmação
- **O que está em aberto**: lacunas, contradições, ou cenários não cobertos
- **Fronteiras do escopo**: o que claramente está dentro e o que claramente está fora

Identifique a funcionalidade central que está sendo especificada e confirme com o usuário se o entendimento está correto antes de avançar.

## Fase 2 — Perguntas Críticas

Faça perguntas para fechar o escopo. O objetivo não é fazer todas as perguntas possíveis — é fazer as **perguntas certas na ordem certa**: primeiro as que desbloqueiam ou condicionam as demais.

Agrupe as perguntas por tema para facilitar a resposta, mas **não lance tudo de uma vez**. Apresente um grupo por rodada, processe as respostas e refine as próximas perguntas com base no que aprendeu.

### Dimensões a explorar

**Escopo e fronteiras**
- O que esta funcionalidade faz e o que ela explicitamente não faz?
- Quais casos de uso estão dentro? Quais ficam para uma versão futura?
- Há dependências com outras funcionalidades que afetam o escopo?

**Regras de negócio**
- Quais são as condições para cada comportamento? (se X, então Y)
- Há prioridade entre regras quando mais de uma se aplica simultaneamente?
- Essas regras são fixas ou configuráveis? Por quem?

**Dados de entrada**
- Quais são os dados necessários para executar a funcionalidade?
- Quais são os formatos, tipos e restrições de cada campo?
- O que acontece se um dado obrigatório estiver ausente ou inválido?
- De onde vêm esses dados — usuário, sistema, integração externa?

**Estados e transições**
- Quais são os estados possíveis da entidade envolvida?
- Quais ações disparam cada transição?
- Há estados irreversíveis? O que os bloqueia ou os permite?
- O que acontece com entidades em estados intermediários quando a ação é disparada?

**Edge cases e erros**
- O que acontece quando a operação falha no meio do caminho?
- Há cenários de concorrência (dois usuários agindo simultaneamente)?
- Quais são os limites (volumes, valores, frequências) que a funcionalidade deve suportar?
- O que o usuário vê quando algo dá errado?

**Atores e permissões**
- Quem pode executar esta ação? Há papéis diferentes com comportamentos diferentes?
- Há ações que requerem aprovação de outro ator?

**Integrações**
- Esta funcionalidade depende de sistemas externos? O que acontece se eles estiverem indisponíveis?
- Ela dispara eventos ou notificações para outros sistemas?

Após cada rodada de respostas, avalie se ainda há ambiguidades relevantes. Se sim, faça mais uma rodada focada. Se não, sinalize que está pronto para escrever o FRD e confirme com o usuário.

## Fase 3 — Validação do Escopo

Antes de escrever o FRD, apresente um resumo do escopo fechado:

- **Comportamentos confirmados**: o que a funcionalidade faz em cada cenário
- **Fora do escopo**: o que foi explicitamente excluído (e por quê, se relevante)
- **Decisões tomadas**: escolhas que foram feitas durante o brainstorming
- **Premissas assumidas**: o que foi assumido por falta de informação (para confirmação)

Pergunte: "Este resumo reflete o que acordamos? Há algo a ajustar antes de eu escrever o FRD?"

Não avance sem confirmação.

## Fase 4 — Geração do FRD

Gere o FRD em `docs/[nome-da-feature]/frd-[nome-da-feature].md`. O nome do arquivo deve ser derivado da funcionalidade (ex.: `frd-calculo-desconto.md`, `frd-checkout.md`, `frd-autenticacao-dois-fatores.md`).

O FRD deve ser **autocontido** — um dev que não participou do brainstorming deve conseguir implementar a funcionalidade lendo apenas este documento.

### Estrutura do FRD

```
# FRD — [Nome da Funcionalidade]

## 1. Visão Geral
- Descrição em 2–3 frases do que a funcionalidade faz e qual problema resolve
- Contexto: onde esta funcionalidade se encaixa no sistema

## 2. Atores
- Quem interage com esta funcionalidade e em qual papel

## 3. Requisitos Funcionais
Numerados (RF-001, RF-002...). Para cada requisito:
- Descrição clara do comportamento
- Condição de disparo (quando se aplica)
- Resultado esperado

## 4. Regras de Negócio
Numeradas (RN-001, RN-002...). Separadas dos requisitos funcionais porque são mais estáveis e podem ser referenciadas por múltiplos RFs.

## 5. Dados de Entrada
- Campo, tipo, obrigatoriedade, validações, origem

## 6. Estados e Transições
- Diagrama textual ou tabela de estados × ações × resultados

## 7. Edge Cases e Tratamento de Erros
- Cenário, comportamento esperado, mensagem ao usuário (se aplicável)

## 8. Fora do Escopo
- O que explicitamente não está coberto nesta versão

## 9. Premissas e Dependências
- O que foi assumido e o que esta funcionalidade depende para funcionar

## 10. Questões em Aberto
- Pontos que ficaram sem definição e precisam de decisão futura (se houver)
```

## Princípios

- **Perguntas antes de respostas**: não assuma comportamentos que não foram confirmados — pergunte
- **Agnóstico de domínio e tecnologia**: o FRD especifica *o quê*, não *como* — sem decisões de implementação
- **Precisão sobre completude**: um FRD com 10 requisitos claros é melhor que 30 vagos
- **Fora do escopo é tão importante quanto dentro**: documentar o que não será feito previne escopo creep
- **Questões em aberto são válidas**: se algo não puder ser decidido agora, registre — não invente uma resposta
