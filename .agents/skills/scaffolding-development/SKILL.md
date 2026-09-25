---
name: scaffolding-development
description: Implementa um projeto em etapas a partir de um Blueprint de scaffolding aprovado. Use esta skill SEMPRE que o usuário fornecer um Blueprint de scaffolding (scaffolding-blueprint.md ou equivalente) e pedir para implementar, executar, criar o projeto, inicializar, instalar dependências, ou montar o boilerplate. Também dispare com expressões como "implemente o projeto", "execute o blueprint", "crie o scaffolding", "inicialize o projeto", "monte o boilerplate". O usuário não executa comandos manualmente — apenas revisa e autoriza cada etapa. A skill executa tudo e verifica o funcionamento ao final. Faz parte de um pipeline: antecedida por scaffolding-blueprint. Se o Blueprint ou o contexto mencionar Docker, containerização ou deploy em container, acione docker-advisor para criar Dockerfile e docker-compose com boas práticas antes de implementar essas etapas.
---

# Implementação do Scaffolding por Etapas

O usuário quer que você implemente o projeto a partir de um Blueprint aprovado. Sua função é executar cada etapa do plano com precisão, comunicar o que está fazendo e por quê, e aguardar revisão antes de avançar onde necessário.

**Regra fundamental**: o usuário não executa comandos manualmente. Você executa tudo. O usuário revisa e autoriza.

## Fase 1 — Leitura do Blueprint

Leia o arquivo de Blueprint fornecido (`docs/scaffolding-blueprint.md` ou o caminho indicado).

Extraia e confirme mentalmente:
- Stack e versões
- Estrutura de diretórios esperada
- Dependências a instalar
- Convenções e padrões obrigatórios
- Sequência de etapas aprovada
- Critérios de sucesso (o que precisa funcionar ao final)
- Entidade de exemplo do fluxo fim a fim

Se o Blueprint estiver incompleto ou ambíguo em algum ponto que bloqueie a implementação, sinalize antes de começar.

## Fase 2 — Apresentação do Plano de Execução

Antes de executar qualquer coisa, apresente ao usuário:

1. **Resumo do que será feito** — as etapas em sequência, de forma concisa
2. **O que você vai executar** — comandos, arquivos a criar, configurações
3. **O que NÃO está no escopo** — para alinhar expectativas

Pergunte: "Posso começar?"

Não execute nada até receber confirmação.

## Fase 3 — Implementação em Etapas

Execute o Blueprint etapa por etapa, **na ordem definida**. Para cada etapa:

### Durante a execução
- Anuncie o que vai fazer antes de fazer: "**Etapa N — [nome]**: vou [descrição]"
- Execute os comandos necessários (inicialização, instalação de dependências, criação de arquivos, configurações)
- Crie os arquivos respeitando rigorosamente as convenções do Blueprint: nomenclatura, estrutura de pastas, padrões de código
- Após concluir, mostre o resultado: saída dos comandos, arquivos criados, o que mudou

### Quando pausar para revisão
Pause e aguarde confirmação do usuário antes de avançar quando:
- A etapa envolve decisões que o Blueprint não detalhou completamente
- Ocorreu um erro ou resultado inesperado
- A etapa seguinte é destrutiva ou irreversível (ex.: sobrescrever arquivos existentes, modificar banco de dados)
- O usuário sinalizou que quer revisar cada etapa

Em casos sem ambiguidade e sem risco, avance direto para a próxima etapa sem interromper o fluxo.

### `.gitignore`

Crie o `.gitignore` na raiz do projeto como parte das etapas iniciais de setup, antes de qualquer commit. O conteúdo deve ser derivado da stack definida no Blueprint — não use um template genérico copiado cegamente.

Inclua padrões para:
- **Dependências**: diretórios de pacotes da stack (ex.: `node_modules/`, `.venv/`, `vendor/`)
- **Build e compilação**: artefatos gerados (ex.: `dist/`, `build/`, `*.pyc`, `__pycache__/`)
- **Ambiente local**: arquivos de variáveis de ambiente com segredos (`.env`, `.env.local` — mas **não** `.env.example`, que deve ser commitado)
- **IDEs e editores**: arquivos de configuração local (ex.: `.idea/`, `.vscode/`, `*.swp`)
- **Sistema operacional**: arquivos do SO que não pertencem ao repositório (ex.: `.DS_Store`, `Thumbs.db`)
- **Logs e temporários**: arquivos gerados em runtime (ex.: `*.log`, `tmp/`, `coverage/`)
- **Qualquer artefato específico da stack** identificado no Blueprint (ex.: `.terraform/`, `*.egg-info`, `.next/`)

Se o Blueprint usar uma stack com convenção consolidada de `.gitignore` (ex.: projeto Node, Python, Go, Rails), siga essa convenção como base e adapte ao que foi definido.

### `README.md`

Crie ou atualize o `README.md` na raiz do projeto após as etapas de inicialização estarem concluídas. O conteúdo deve refletir o estado real do projeto — não um template genérico.

Inclua obrigatoriamente todos os **comandos de inicialização executados** durante o setup (instalação de dependências, configuração de ambiente, migrations, seed, etc.), na ordem correta, prontos para copiar e colar. Se o dev precisar rodar algo para colocar o projeto de pé, deve estar aqui.

Estrutura mínima:
- **Descrição**: o que o projeto faz (extraído do Blueprint)
- **Pré-requisitos**: versões de runtime, ferramentas necessárias
- **Setup**: passo a passo completo desde o clone até o projeto rodando localmente
- **Comandos úteis**: dev, build, test, seed — o que cada script faz
- **Variáveis de ambiente**: referência ao `.env.example` e o que cada variável controla

### Se ocorrer um erro
- Pare imediatamente
- Mostre o erro completo
- Explique o que causou o problema
- Proponha a correção antes de aplicá-la
- Não tente workarounds silenciosos

## Fase 4 — Verificação Final

Após concluir todas as etapas, execute uma verificação do funcionamento do projeto. O que verificar depende do Blueprint, mas no mínimo:

1. **Saúde do sistema**: se o projeto define um endpoint ou mecanismo de health check, execute-o e confirme a resposta esperada
2. **Fluxo fim a fim da entidade de exemplo**: execute o fluxo completo definido no Blueprint (ex.: listar registros via API, verificar persistência no banco) e confirme que funciona conforme os critérios de sucesso
3. **Seed**: se o Blueprint inclui seed, execute-o e verifique que os dados foram inseridos corretamente
4. **Testes**: execute todos os testes criados durante o scaffolding e mostre os resultados:
   - **Testes unitários**: lógica isolada da entidade de exemplo
   - **Testes de integração**: interação entre camadas (ex.: service → repository → banco)
   - **Testes e2e de endpoint**: rotas da API com inputs e outputs esperados (se aplicável)
   - **Testes e2e de frontend**: fluxo do usuário na interface (se aplicável)

Para cada verificação, mostre o comando executado e a saída obtida. Não declare sucesso sem evidência. Se algum teste falhar, corrija antes de avançar para o relatório final.

## Fase 5 — Relatório Final

Apresente um resumo conciso:

- **O que foi implementado**: lista das etapas concluídas
- **Estrutura criada**: árvore de diretórios do que foi gerado
- **Verificações realizadas**: resultados das verificações com evidências
- **O que ficou fora do escopo**: o que não foi implementado nesta sessão e por quê
- **Próximos passos sugeridos**: o que naturalmente vem a seguir (sem executar — apenas informar)

## Princípios

- **Fiel ao Blueprint**: não improvise nem adicione o que não está no plano aprovado; se perceber algo faltando, aponte no relatório final
- **Transparência total**: sempre comunique o que vai fazer antes de fazer
- **Sem surpresas**: erros, desvios e decisões implícitas são comunicados imediatamente
- **Agnóstico de tecnologia e domínio**: adapte-se completamente à stack e ao domínio definidos no Blueprint
- **O usuário não digita comandos**: você executa tudo; o papel do usuário é revisar, autorizar e receber o resultado
