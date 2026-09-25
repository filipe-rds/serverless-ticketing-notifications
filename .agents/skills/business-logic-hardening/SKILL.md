---
name: business-logic-hardening
description: Endurece lógica de negócio existente com base em especificações formais (diagramas de estado, regras de negócio, invariantes, contratos). Use esta skill SEMPRE que o usuário fornecer uma especificação formal (diagrama de estados, tabela de transições, regras de negócio, invariantes, contratos de interface) junto com código existente e pedir para implementar validações, máquinas de estado, guards, enforcement de regras, ou tornar a lógica mais rigorosa. Também dispare com expressões como "implemente a máquina de estados", "enforce as transições", "adicione validação de regras de negócio", "hardening de lógica", "garanta que as transições respeitem o diagrama", "implemente os guards", "torne a lógica mais estrita", "valide os estados". Respeita estritamente a especificação fornecida — não adiciona estados, transições ou regras que não estejam explícitos.
---

# Hardening de Lógica de Negócio

O usuário quer tornar a lógica de negócio existente mais rigorosa, baseando-se em uma especificação formal. O código pode já funcionar para o "caminho feliz", mas falta enforcement: transições inválidas não são bloqueadas, regras de negócio não são validadas antes de agir, invariantes não são garantidas.

Seu papel é ler a especificação formal, entender o código existente, e implementar o enforcement com precisão cirúrgica — sem adicionar nada além do que a especificação define.

## Fase 1 — Leitura e Mapeamento

Leia os documentos fornecidos:

**Especificação formal** — pode ser um ou mais de:
- Diagrama de estados (com transições e condições)
- Tabela de transições permitidas
- Regras de negócio documentadas (RNs de um FRD, ADR, ou doc livre)
- Invariantes e pré/pós-condições
- Contratos de interface (o que uma função/endpoint deve aceitar e rejeitar)

**Código existente** — os arquivos onde a lógica vive hoje.

Ao ler, construa dois mapas:

**Mapa da especificação** — o que deveria existir:
- Estados possíveis e transições permitidas (com condições/guards)
- Regras de validação e suas condições de disparo
- Invariantes que devem ser sempre verdadeiras
- O que é explicitamente proibido

**Mapa do código** — o que existe hoje:
- Como estados são representados (string, enum, constante, flag)
- Onde transições acontecem (quais funções, métodos, handlers)
- Que validações já existem e quais faltam
- O que acontece hoje quando uma operação inválida é tentada (nada? erro genérico? crash?)

Apresente a comparação: o que a especificação exige vs. o que o código faz hoje. Destaque os gaps.

Confirme com o usuário antes de avançar.

## Fase 2 — Plano de Hardening

Apresente o plano **sem código**. Para cada gap identificado:

- **O que endurecer**: descrição objetiva
- **Onde**: arquivo(s) e função(ões) afetados
- **Como**: abordagem técnica (enum, mapa de transições, função de guarda, validador, etc.)
- **Comportamento em caso de violação**: o que acontece quando a regra é quebrada (erro tipado, exceção, rejeição com mensagem clara)
- **Testes planejados**: quais testes escrever para cada enforcement:
  - Unitários: lógica isolada (função de transição, validador, guard)
  - Integração: interação entre componentes (service que usa o validador, handler que aplica a transição)
  - E2e de endpoint: se o enforcement afeta uma API, testar a rota com inputs válidos e inválidos
  - E2e de frontend: se o enforcement afeta a interface, testar o fluxo do usuário com cenários válidos e proibidos

### Padrões comuns de hardening

Adapte ao que a especificação exige — nem todos se aplicam a cada caso:

**Máquina de estados**
- Enum ou constantes com todos os estados válidos (e nenhum outro)
- Mapa de transições permitidas: estado atual → ação → estado destino
- Função de transição que valida antes de executar
- Rejeição explícita de transições proibidas com erro claro (não silenciosa)

**Validação de regras de negócio**
- Guards que verificam pré-condições antes de executar uma operação
- Validação de invariantes após mutações (o sistema está em estado consistente?)
- Rejeição com mensagem que explica qual regra foi violada

**Enforcement de contratos**
- Validação de inputs conforme o contrato definido (tipo, formato, range, obrigatoriedade)
- Validação de outputs antes de retornar (o resultado faz sentido?)
- Tratamento explícito de combinações inválidas de parâmetros

Pergunte: "O plano está alinhado? Posso implementar?"

**Não escreva código até receber aprovação.**

## Fase 3 — Implementação

Após aprovação, implemente seguindo o plano:

- Anuncie cada alteração antes de fazê-la
- Modifique os arquivos existentes — prefira refinar o código atual a reescrevê-lo do zero
- Respeite as convenções do projeto (nomenclatura, padrões, estilo)
- Escreva testes junto com cada enforcement implementado

### Regra de ouro

**Implemente somente o que a especificação define.** Se o diagrama tem 5 estados e 8 transições, implemente exatamente 5 estados e 8 transições. Se uma regra de negócio tem 3 condições, valide exatamente 3. Não adicione estados "que fazem sentido", transições "que provavelmente existem", ou validações "por precaução".

Se perceber que a especificação tem gaps (um estado sem transição de saída, uma regra que contradiz outra), **sinalize ao usuário** em vez de preencher por conta.

### Se precisar desviar do plano

- Pare e explique o que mudou
- Proponha o ajuste
- Só prossiga após o usuário concordar

## Fase 4 — Verificação

### Compilação e build
Execute o build do projeto e confirme que nenhum código existente quebrou.

### Testes
Execute todos os testes escritos e mostre os resultados:

- **Testes unitários**: lógica isolada de cada enforcement implementado
  - Transições válidas: cada transição permitida funciona corretamente
  - Transições proibidas: cada transição não permitida é rejeitada com erro claro e mensagem identificável
  - Validações de regras: inputs válidos passam, inválidos são rejeitados
  - Invariantes: após cada operação, o sistema está em estado consistente
- **Testes de integração**: interação entre o enforcement e os componentes que o utilizam
  - O service que invoca a transição recebe e propaga o erro corretamente?
  - O handler que aplica a validação responde de forma adequada?
- **Testes e2e de endpoint**: se o enforcement afeta rotas de API, testar com requests que exercitem caminhos válidos e proibidos — verificar status codes e mensagens de erro
- **Testes e2e de frontend**: se o enforcement afeta a interface do usuário, testar o fluxo com cenários válidos (ação permitida) e proibidos (ação bloqueada com feedback ao usuário)

Para cada teste, mostre: o que foi testado, o comando executado e o resultado. Se algum teste falhar, corrija antes de avançar.

### Validação contra a especificação
Cruze a especificação com o código final:
- Cada estado/regra da especificação está implementado?
- Cada rejeição produz uma mensagem que identifica a violação?
- Não há estados, transições ou regras extras que não estão na especificação?

Mostre evidências para cada verificação.

## Fase 5 — Relatório

Salve o relatório em `docs/[nome-da-feature]/hardening-[nome-da-feature].md`.

Apresente:

- **O que foi endurecido**: lista dos enforcements implementados
- **Arquivos modificados**: o que mudou em cada um
- **Testes executados**: resultados com evidência
- **Gaps identificados na especificação**: pontos que a especificação não cobre e que podem precisar de atenção futura
- **O que não foi alterado**: código existente que não foi tocado e por quê

## Princípios

- **A especificação é lei**: implemente exatamente o que está definido — nem mais, nem menos
- **Rejeições são features, não erros**: uma transição proibida rejeitada com mensagem clara é o sistema funcionando corretamente
- **Plano antes de código**: nunca implemente sem aprovação, mesmo que o gap pareça óbvio
- **Não invente regras**: se a especificação não cobre um cenário, sinalize em vez de assumir
- **Preserve o código existente**: prefira adicionar enforcement ao código atual a reescrevê-lo — minimize o risco de regredir funcionalidades que já funcionam
- **Agnóstico de tecnologia e domínio**: adapte-se à stack, padrões e linguagem do projeto
