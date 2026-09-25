---
name: feature-test-hardening
description: Planeja e implementa suítes de testes completas para funcionalidades existentes, incluindo seeds, test doubles, testes unitários, de integração e e2e. Use esta skill SEMPRE que o usuário pedir para criar, reforçar, organizar, endurecer ou planejar testes para uma funcionalidade já implementada. Também dispare com expressões como "crie testes para a feature", "planeje a suíte de testes", "hardening de testes", "melhore os testes", "adicione testes para", "planeje seeds e test doubles", "organize os testes", "cobertura de testes", "testes do carrinho", "testes da funcionalidade". Produz um plano para aprovação, executa as alterações, e gera um relatório em docs/[nome-da-feature]/test-report-[nome-da-feature].md. Faz parte do pipeline de features: pode ser usada após feature-development ou feature-review quando a cobertura de testes precisa de reforço.
---

# Planejamento e Hardening de Testes de Funcionalidade

O usuário quer garantir que uma funcionalidade já implementada tenha uma suíte de testes sólida, realista e bem estruturada. O código já existe — o objetivo é fortalecer os testes, não a funcionalidade em si.

Seu papel é analisar o que existe, identificar gaps de cobertura, planejar uma suíte completa e implementar após aprovação.

## Fase 1 — Leitura e Mapeamento

Leia os documentos fornecidos:

**Especificações** — FRD, diagramas de estado, regras de negócio, Blueprint (o que estiver disponível):
- Requisitos funcionais (RF-XXX) e regras de negócio (RN-XXX)
- Estados e transições
- Dados de entrada: campos, tipos, validações, limites
- Edge cases documentados
- Fora do escopo

**Código existente** — a implementação da funcionalidade:
- Modelos de dados e schemas
- Lógica de negócio (services, use cases, handlers)
- Interfaces (rotas, controllers, componentes de UI)
- Validações existentes
- Testes existentes (se houver)

Ao ler, construa três mapas:

**Mapa de cenários**: todos os comportamentos testáveis derivados da especificação — caminhos felizes, edge cases, transições válidas, transições proibidas, validações de input, erros esperados.

**Mapa de cobertura atual**: o que os testes existentes já cobrem (se existem testes).

**Mapa de gaps**: cenários que deveriam ser testados mas não são.

Apresente o diagnóstico: quantos cenários identificados, quantos cobertos, quantos faltando — agrupados por tipo (unitário, integração, e2e). Confirme com o usuário antes de avançar.

## Fase 2 — Plano de Testes

Apresente o plano completo **sem código** para aprovação. Organize por seção:

### Seeds e Dados de Teste

Defina os dados realistas que alimentarão os testes:

- **Entidades a criar**: quais objetos de teste são necessários e seus campos com valores representativos (não `test123` — dados que pareçam reais)
- **Variações**: diferentes estados, combinações de campos, valores limite (min, max, empty, null)
- **Onde ficam os seeds**: arquivo/diretório conforme as convenções do projeto
- **Como são carregados**: fixtures, factories, builders, seed scripts — o que a stack usa
- **Isolamento**: como garantir que testes não dependam uns dos outros (setup/teardown)

### Test Doubles

Sugira as bibliotecas de test doubles adequadas para a stack do projeto e planeje quais doubles serão necessários:

- **Quais dependências simular**: banco de dados, APIs externas, serviços, filas, envio de email, etc.
- **Tipo de double para cada caso**: mock, stub, spy, fake — e por quê
  - **Mock**: quando você precisa verificar que uma interação aconteceu (ex.: "o email foi enviado?")
  - **Stub**: quando você precisa controlar o retorno de uma dependência (ex.: "API retorna erro 500")
  - **Spy**: quando você quer observar sem alterar o comportamento (ex.: "quantas vezes o repositório foi chamado?")
  - **Fake**: quando você precisa de uma implementação simplificada mas funcional (ex.: banco em memória)
- **Estrutura de dados dos doubles**: qual a forma dos objetos que cada double vai retornar ou receber — não genérica, derivada dos modelos reais do projeto
- **Biblioteca recomendada**: qual e por quê (ex.: sinon, jest.mock, unittest.mock, testify/mock, gomock)

### Testes Unitários

Para cada componente com lógica de negócio:
- **O que testar**: função/método, cenário, resultado esperado
- **Cenários por componente**: caminho feliz + edge cases + erros
- **Quais doubles usar**: em cada teste, o que é mockado/stubbed
- **Onde fica o arquivo de teste**: caminho conforme convenções

### Testes de Integração

Para cada interação entre componentes:
- **O que testar**: quais camadas estão sendo exercitadas juntas (ex.: service → repository → banco)
- **Setup necessário**: banco de teste, container, serviço auxiliar
- **Seeds utilizados**: quais dados de teste são carregados
- **Cenários**: operações completas com verificação de side effects (dados persistidos, eventos emitidos)

### Testes E2E de Endpoint

Para cada rota/endpoint da funcionalidade:
- **O que testar**: rota, método HTTP, headers necessários
- **Inputs**: payloads válidos, inválidos, edge cases (campos faltando, tipos errados, valores limite)
- **Outputs esperados**: status code, corpo da resposta, headers
- **Cenários de erro**: autenticação faltando, autorização insuficiente, recurso não encontrado, conflito de estado

### Testes E2E de Frontend (se aplicável)

Para cada fluxo de usuário na interface:
- **O que testar**: fluxo, interações, resultado visual/funcional
- **Cenários**: caminho feliz + estados de erro + loading + empty states
- **Setup**: dados que precisam existir antes do teste rodar

Pergunte: "O plano está alinhado? Posso implementar?"

**Não escreva código até receber aprovação.**

## Fase 3 — Implementação

Após aprovação, implemente na seguinte ordem:

1. **Seeds e fixtures** — os dados de teste primeiro, pois tudo depende deles
2. **Test doubles** — configuração dos mocks, stubs e fakes
3. **Testes unitários** — lógica isolada
4. **Testes de integração** — interação entre camadas
5. **Testes e2e de endpoint** — rotas completas
6. **Testes e2e de frontend** — fluxos de usuário (se aplicável)

Para cada grupo:
- Anuncie o que vai fazer antes de fazer
- Crie os arquivos respeitando as convenções do projeto
- Execute os testes à medida que os escreve — não acumule tudo para o final

### Se encontrar bugs durante os testes

Se um teste revelar um bug no código da funcionalidade:
- Pare e sinalize ao usuário: "O teste revelou um bug em [localização]: [descrição]"
- Proponha a correção
- Só aplique após autorização
- Registre o bug encontrado para o relatório final

### Se precisar desviar do plano

- Pare e explique o que mudou
- Proponha o ajuste
- Só prossiga após o usuário concordar

## Fase 4 — Verificação

Execute toda a suíte de testes e mostre os resultados consolidados:

- **Testes unitários**: total, passando, falhando
- **Testes de integração**: total, passando, falhando
- **Testes e2e de endpoint**: total, passando, falhando
- **Testes e2e de frontend**: total, passando, falhando (se aplicável)

Para cada teste, mostre: o que foi testado, o comando executado e o resultado. Se algum teste falhar, corrija antes de avançar.

### Validação de cobertura

Cruze a suíte final contra a especificação:
- Cada RF/RN tem pelo menos um teste?
- Cada edge case documentado tem um teste?
- Cada transição de estado (válida e proibida) tem um teste?
- Cada validação de input tem teste para valor válido e inválido?

## Fase 5 — Relatório de Testes

Gere e salve o relatório em `docs/[nome-da-feature]/test-report-[nome-da-feature].md`.

### Formato do relatório

```
## Relatório de Testes — [nome da funcionalidade]

### Resumo
- Testes unitários: X total (Y passando, Z falhando)
- Testes de integração: X total (Y passando, Z falhando)
- Testes e2e de endpoint: X total (Y passando, Z falhando)
- Testes e2e de frontend: X total (Y passando, Z falhando)
- Bugs encontrados durante testes: N

### Seeds e Dados de Teste
- Entidades criadas e suas variações
- Localização dos arquivos de seed/fixtures

### Test Doubles
- Biblioteca utilizada e versão
- Doubles criados: tipo, dependência simulada, propósito

### Cobertura por Requisito
| RF/RN | Unitário | Integração | E2E Endpoint | E2E Frontend | Observação |
|-------|----------|------------|-------------|-------------|------------|
| RF-001 | 3 testes | 1 teste | 2 testes | 1 teste | — |
| RN-003 | 2 testes | — | 1 teste | — | Integração não aplicável |

### Bugs Encontrados
Lista de bugs revelados pelos testes, com localização e status (corrigido/pendente).

### Cenários Não Cobertos
Cenários que foram identificados mas não puderam ser testados (e por quê).

### Arquivos Criados/Modificados
Lista de todos os arquivos de teste com seu propósito.
```

## Princípios

- **Plano antes de código**: nunca implemente testes sem aprovação do plano
- **Dados realistas**: seeds devem parecer dados de produção, não `foo`, `bar`, `test123`
- **Testes são documentação**: um teste bem escrito explica o comportamento esperado — nomeie-os com clareza
- **Isolamento**: cada teste deve rodar independente dos outros; setup e teardown são obrigatórios
- **Bugs são achados, não escondidos**: se um teste revela um bug, sinalize — não ajuste o teste para passar
- **Cobertura com propósito**: testar por testar não ajuda; cada teste deve validar um cenário real derivado da especificação
- **Agnóstico de tecnologia e domínio**: adapte-se à stack, framework de testes e convenções do projeto
