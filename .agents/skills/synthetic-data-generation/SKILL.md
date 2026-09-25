---
name: synthetic-data-generation
description: Gera seeds volumosos com dados sintéticos realistas para popular o banco de dados em carga. Use esta skill SEMPRE que o usuário pedir para gerar dados de teste, seeds volumosos, dados sintéticos, popular o banco, ou criar massa de dados. Também dispare com expressões como "gere seeds", "popule o banco", "dados fake", "massa de dados", "dados realistas para teste", "seeds volumosos", "ambiente povoado". Lê os modelos/schemas do projeto, sugere bibliotecas de dados fake adequadas à stack e gera os seeds. Produz um relatório em docs/[nome-da-feature]/synthetic-data-report.md.
---

# Geração de Dados Sintéticos

O usuário quer popular o banco de dados com dados realistas em volume, para exercitar o sistema em condições próximas de produção. Dados triviais (`teste1`, `foo`, `bar`) não revelam bugs reais — dados com nomes, endereços, datas válidas e variações de cenário sim.

## Fase 1 — Leitura dos Modelos

Leia os schemas/modelos do projeto para entender:

- **Entidades**: quais tabelas/coleções existem e seus campos
- **Tipos e constraints**: tipo de cada campo, obrigatoriedade, unicidade, foreign keys, enums
- **Relacionamentos**: 1:N, N:N, dependências entre entidades (ordem de criação importa)
- **Seeds existentes**: se já há seeds no projeto, o que cobrem e em que volume

Apresente um resumo do que entendeu e confirme com o usuário antes de avançar.

## Fase 2 — Plano de Geração

Apresente o plano **sem código** para aprovação:

### Biblioteca de dados fake
Sugira a biblioteca adequada para a stack do projeto:
- JavaScript/TypeScript: `@faker-js/faker`
- Python: `faker`
- Go: `gofakeit`
- Ruby: `faker`
- Java: `javafaker` / `datafaker`
- Outra stack: pesquise e sugira

### Volume e variações
Para cada entidade:
- **Quantidade de registros**: adequada ao propósito (centenas para dev, milhares para carga)
- **Variações de dados**: diferentes estados, combinações, valores limite, campos opcionais preenchidos e vazios
- **Dados realistas**: nomes que parecem nomes, datas que fazem sentido, valores dentro de ranges válidos
- **Consistência relacional**: foreign keys apontando para registros que existem, ordem de criação respeitando dependências

### Estrutura dos seeds
- **Onde ficam os arquivos**: diretório conforme convenções do projeto
- **Como executar**: comando para rodar os seeds
- **Idempotência**: os seeds devem poder ser re-executados sem duplicar dados

Pergunte: "O plano está alinhado? Posso implementar?"

**Não escreva código até receber aprovação.**

## Fase 3 — Implementação

Após aprovação:
- Instale a biblioteca de dados fake (se necessário)
- Crie os arquivos de seed respeitando as convenções do projeto
- Gere dados na ordem correta (entidades pai antes de filhas)
- Execute os seeds e confirme que foram inseridos corretamente

### Se ocorrer um erro
- Pare e mostre o erro completo
- Explique a causa (constraint violada, FK inválida, tipo errado)
- Proponha a correção antes de aplicá-la

## Fase 4 — Verificação

- Execute os seeds e confirme a inserção (contagem de registros por entidade)
- Verifique que o sistema continua funcional com os dados carregados (health check, listagem, operações básicas)
- Execute os testes existentes para confirmar que nada quebrou

Mostre evidências para cada verificação.

## Fase 5 — Relatório

Salve o relatório em `docs/[nome-da-feature]/synthetic-data-report.md`.

```
## Relatório de Dados Sintéticos — [contexto]

### Resumo
- Entidades populadas: X
- Total de registros gerados: Y
- Biblioteca utilizada: [nome e versão]

### Dados Gerados por Entidade
| Entidade | Registros | Variações | Observação |
|----------|-----------|-----------|------------|
| Produto  | 500       | 5 categorias, preços de 0.01 a 9999.99 | — |
| Cupom    | 100       | % e valor fixo, ativos e expirados | — |

### Estrutura dos Seeds
- Localização dos arquivos
- Comando para executar
- Ordem de execução

### Verificação
- Testes passando após carga: Sim/Não
- Sistema funcional com dados: Sim/Não
```

## Princípios

- **Dados realistas, não triviais**: nomes que parecem nomes, datas que fazem sentido, valores dentro de ranges reais
- **Plano antes de código**: nunca gere seeds sem aprovação do plano
- **Consistência relacional**: FKs válidas, ordem de criação correta, constraints respeitadas
- **Idempotência**: seeds devem poder ser re-executados sem efeitos colaterais
- **Agnóstico de tecnologia e domínio**: adapte-se à stack e ao domínio do projeto
