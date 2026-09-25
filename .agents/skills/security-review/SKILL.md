---
name: security-review
description: Inspeciona código com foco em vulnerabilidades OWASP Top 10 e boas práticas de segurança, simulando um Red Team estático. Use esta skill SEMPRE que o usuário pedir para revisar segurança, fazer Red Team, auditar vulnerabilidades, checar OWASP, ou inspecionar brechas de segurança. Também dispare com expressões como "Red Team", "OWASP", "vulnerabilidades", "segurança do código", "brechas de segurança", "inspecione fragilidades", "auditoria de segurança", "shift-left security". Produz um relatório com findings de segurança e aplica correções após aprovação. Relatório salvo em docs/[nome-da-feature]/security-report-[nome-da-feature].md.
---

# Code Review Red Team (Segurança)

O usuário quer submeter o código a uma inspeção de segurança, simulando um Red Team estático. O objetivo é identificar vulnerabilidades que poderiam ser exploradas em produção — antes que cheguem lá.

Sua função é ser um **atacante que pensa antes do atacante real**. Leia o código com olhos de quem quer quebrá-lo.

## Fase 1 — Leitura e Mapeamento de Superfície de Ataque

Leia o código-fonte indicado pelo usuário. Ao ler, mapeie:

- **Pontos de entrada**: endpoints de API, formulários, uploads, webhooks — qualquer lugar onde dados externos entram no sistema
- **Autenticação e autorização**: como sessões são gerenciadas, onde tokens são validados, quais rotas são protegidas
- **Acesso a dados**: queries ao banco, ORMs, acesso a arquivos — onde dados são lidos ou escritos
- **Dependências externas**: chamadas a APIs de terceiros, serviços, filas
- **Segredos e configurações**: como credenciais são armazenadas e acessadas
- **Outputs**: o que o sistema retorna (logs, respostas de API, mensagens de erro)

Apresente o mapeamento da superfície de ataque e confirme com o usuário antes de avançar.

## Fase 2 — Análise de Vulnerabilidades

Analise o código contra as seguintes categorias (baseadas em OWASP Top 10 e boas práticas):

### Injection (SQL, NoSQL, Command, XSS)
- Inputs do usuário são sanitizados antes de uso em queries?
- Há concatenação de strings em queries SQL?
- Dados do usuário são renderizados no frontend sem escape?
- Há execução de comandos do sistema com input do usuário?

### Autenticação e Gerenciamento de Sessão
- Senhas são hasheadas com algoritmo seguro (bcrypt, argon2)?
- Tokens têm expiração?
- Sessões são invalidadas no logout?
- Há proteção contra brute force?

### Autorização e Controle de Acesso
- Cada endpoint verifica se o usuário tem permissão?
- Há risco de IDOR (Insecure Direct Object Reference)?
- Um usuário pode acessar dados de outro via manipulação de IDs?

### Exposição de Dados Sensíveis
- Respostas de API expõem dados internos desnecessários?
- Stack traces aparecem em mensagens de erro em produção?
- Logs contêm senhas, tokens ou PII?
- Headers de segurança estão configurados (CORS, CSP, HSTS)?

### Configuração Insegura
- Debug mode habilitado por padrão?
- Variáveis de ambiente com valores padrão inseguros?
- Portas ou serviços expostos desnecessariamente?
- Dependências com CVEs conhecidos?

### Outras Vulnerabilidades
- CSRF: formulários com proteção de token?
- Rate limiting: endpoints sensíveis têm limite de requisições?
- Upload de arquivos: validação de tipo e tamanho?
- Desserialização insegura?

Para cada vulnerabilidade encontrada, documente:
- **Severidade**: CRÍTICO / ALTO / MÉDIO / BAIXO
- **Localização**: arquivo e linha
- **Descrição**: o que é a vulnerabilidade
- **Vetor de ataque**: como alguém poderia explorá-la
- **Recomendação**: o que fazer para corrigir

Apresente os findings e pergunte: "Quais correções quer que eu aplique?"

## Fase 3 — Correções

Aplique apenas o que o usuário autorizar. Para cada correção:

- Anuncie o que vai mudar e por quê
- Implemente a correção
- Explique o que a correção faz (para o usuário aprender)

Após todas as correções:
- Execute os testes existentes e confirme que nada quebrou
- Se uma correção exigir novos testes (ex.: teste de sanitização de input), escreva-os

## Fase 4 — Verificação

- **Build**: projeto compila sem erros
- **Testes existentes**: todos passam após as correções
- **Novos testes de segurança**: se escritos, passam
- **Re-inspeção**: confirme que as vulnerabilidades corrigidas não estão mais presentes

Mostre evidências para cada verificação.

## Fase 5 — Relatório

Salve o relatório em `docs/[nome-da-feature]/security-report-[nome-da-feature].md`.

```
## Relatório de Segurança (Red Team) — [contexto]

### Resumo
- Total de findings: X (Y críticos, Z altos, ...)
- Corrigidos nesta sessão: N
- Pendentes: M

### Findings

#### [CRÍTICO] Título
**Categoria OWASP**: Injection / Auth / etc.
**Localização**: arquivo:linha
**Vetor de ataque**: como explorar
**Status**: Corrigido / Pendente
**Correção aplicada**: descrição (se corrigido)

### Testes de Segurança Adicionados
Lista de testes criados para validar as correções.

### Recomendações Pendentes
Findings que não foram corrigidos nesta sessão e por quê.
```

## Princípios

- **Pense como atacante**: não avalie se o código "parece seguro" — pergunte "como eu quebraria isso?"
- **Severidade honesta**: nem tudo é CRÍTICO — classifique com base no impacto real e facilidade de exploração
- **Correções sem regressão**: toda correção deve ser seguida de execução de testes — segurança não pode quebrar funcionalidade
- **Explique o porquê**: o usuário deve entender a vulnerabilidade, não só aplicar o fix
- **Agnóstico de tecnologia e domínio**: aplique os princípios de segurança à stack real do projeto, não a uma stack genérica
