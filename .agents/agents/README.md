# Agentes do ticketstream

Subagentes especializados, cada um com um papel do fluxo de trabalho do `AGENTS.md`. Eles aplicam as skills de
`.agents/skills/` com as adaptações do `AGENTS.md` §13 e respeitam o modo socrático (§2.1): nenhum deles escreve código
de produção em `src/`.

| Agente | Papel | Escreve em | Skills que aplica | Quando |
|---|---|---|---|---|
| [`slice-planner`](slice-planner.md) | Planeja a fatia: FRD e Blueprint | `docs/<fatia>/` | `feature-spec-brainstorm`, `feature-blueprint` | Início de cada Etapa |
| [`test-writer`](test-writer.md) | Testes vermelhos, fakes, fixtures, E2E | `tests/` | `feature-test-hardening`, `e2e-flow-test`, `business-logic-hardening` (testes) | Tarefas de teste do Blueprint |
| [`socratic-mentor`](socratic-mentor.md) | Guia a implementação sem escrevê-la | nada | `feature-development` (Fase 3 socrática) | Tarefas de autor "desenvolvedor" |
| [`local-infra-engineer`](local-infra-engineer.md) | MiniStack, SAM, scripts, Makefile | arquivos mecânicos (§2.1) | `docker-advisor` | Etapa 1B e cada função nova no template |
| [`architecture-reviewer`](architecture-reviewer.md) | Revisão contra Dependency Rule e specs | `docs/<fatia>/review-*.md` | `feature-review` (com Eixo 0) | Fim de cada tarefa ou fatia |
| [`security-reviewer`](security-reviewer.md) | Red Team estático, foco serverless | `docs/<fatia>/security-report-*.md` | `security-review` | Handler novo (leve); Etapa 9 (completa) |
| [`docs-auditor`](docs-auditor.md) | Código × docs e docs × docs | nada (só relatório) | `reverse-engineering` | Fechamento de cada Etapa |

## Fluxo de uma fatia com os agentes

Segue a ordem do `AGENTS.md` §8 e o ciclo da DEC-25:

```text
slice-planner ─► FRD + Blueprint aprovados
   │
   ├─► test-writer ──────────► teste vermelho (domínio / use case)
   │      └─► socratic-mentor ─► desenvolvedor implementa até ficar verde
   │
   ├─► test-writer ──────────► teste de integração (moto) → desenvolvedor implementa o adapter
   │
   ├─► local-infra-engineer ─► função no template.yaml + deploy no MiniStack
   │      └─► test-writer ────► teste E2E (MiniStack)
   │
   ├─► architecture-reviewer ─► relatório de revisão   (+ security-reviewer, leve)
   │
   └─► docs-auditor ──────────► dívidas novas ao fechar a Etapa
```

## Regras comuns
- O `AGENTS.md` prevalece sobre qualquer agente e sobre qualquer skill.
- Um agente por vez, uma fatia por vez. Nenhum agente emenda o trabalho do seguinte sem pedido.
- Os revisores (`architecture-reviewer`, `security-reviewer` e `docs-auditor`) **só reportam**. Quem decide e corrige é
  o desenvolvedor.
- Deploy em conta AWS real só com pedido explícito. O padrão é o MiniStack.

## Como os harnesses encontram os agentes
- **Claude Code:** só procura subagentes em `.claude/agents/`, por isso o repositório tem o link simbólico
  `.claude/agents -> ../.agents/agents`. Os agentes aparecem a partir da próxima sessão.
- **Outros harnesses:** não existe formato comum de agente entre as ferramentas. Eles usam estes arquivos como
  instrução: quando a tarefa corresponder à descrição de um agente, abrem o arquivo e seguem o papel descrito.
- **Edite sempre aqui, em `.agents/agents/`**, nunca pelo caminho do link (`AGENTS.md` §2.3).

Agente novo: crie `.agents/agents/<nome>.md` com frontmatter `name` (igual ao nome do arquivo), `description` e
`tools`, com aspas na descrição se ela tiver `: `.
