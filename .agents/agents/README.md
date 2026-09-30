# Agentes do ticketstream

Subagentes especializados, cada um com um papel do fluxo de trabalho do `AGENTS.md`. Eles aplicam as skills de
`.agents/skills/` com as adaptações do `AGENTS.md` §13 e respeitam o modo executor conservador (§2.1): nada é executado sem plano aprovado pelo usuário, os testes são
congelados antes do código de produção, e só o `slice-implementer` escreve em `src/`.

| Agente | Papel | Escreve em | Skills que aplica | Quando |
|---|---|---|---|---|
| [`slice-planner`](slice-planner.md) | Planeja a fatia: FRD e Blueprint | `docs/<fatia>/` | `feature-spec-brainstorm`, `feature-blueprint` | Início de cada Etapa |
| [`test-writer`](test-writer.md) | Matriz regra → teste, testes vermelhos, fakes, fixtures, E2E; congelamento | `tests/` | `feature-test-hardening`, `e2e-flow-test`, `business-logic-hardening` (testes) | Início de toda tarefa de código (Portões 1 e 2) |
| [`slice-implementer`](slice-implementer.md) | Implementa a tarefa sob testes congelados | `src/` | `feature-development` (Fases 3 e 4) | Tarefa de código após o Portão 3 |
| [`local-infra-engineer`](local-infra-engineer.md) | MiniStack, SAM, scripts, Makefile | arquivos mecânicos (§2.1) | `docker-advisor` | Etapa 1B e cada função nova no template |
| [`architecture-reviewer`](architecture-reviewer.md) | Revisão contra Dependency Rule e specs | `docs/<fatia>/review-*.md` | `feature-review` (com Eixo 0) | Fim de cada tarefa ou fatia |
| [`security-reviewer`](security-reviewer.md) | Red Team estático, foco serverless | `docs/<fatia>/security-report-*.md` | `security-review` | Handler novo (leve); Etapa 9 (completa) |
| [`docs-auditor`](docs-auditor.md) | Código × docs e docs × docs | nada (só relatório) | `reverse-engineering` | Fechamento de cada Etapa |

## Fluxo de uma fatia com os agentes

Segue a ordem do `AGENTS.md` §8 e o ciclo da DEC-25:

```text
slice-planner ─► FRD + Blueprint aprovados
   │
   ├─► test-writer ──────────► matriz regra → teste (Portão 1) → testes vermelhos congelados (Portão 2)
   │      └─► slice-implementer ─► plano (Portão 3) → implementa até ficar verde, sem tocar em tests/
   │
   ├─► test-writer ──────────► teste de integração (moto) congelado → slice-implementer implementa o adapter
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
- Os revisores (`architecture-reviewer`, `security-reviewer` e `docs-auditor`) **só reportam**. Quem decide é o usuário;
  a correção segue o ciclo do `AGENTS.md` §2.1.
- Nada é executado sem plano aprovado pelo usuário, e a aprovação de uma tarefa não se estende à seguinte.
- Depois do congelamento, nenhum agente edita `tests/` nem a configuração de verificação (`AGENTS.md` §2.1.2).
- Deploy em conta AWS real só com pedido explícito. O padrão é o MiniStack.

## Como os harnesses encontram os agentes
- **Claude Code:** só procura subagentes em `.claude/agents/`, por isso o repositório tem o link simbólico
  `.claude/agents -> ../.agents/agents`. Os agentes aparecem a partir da próxima sessão.
- **Outros harnesses:** não existe formato comum de agente entre as ferramentas. Eles usam estes arquivos como
  instrução: quando a tarefa corresponder à descrição de um agente, abrem o arquivo e seguem o papel descrito.
- **Edite sempre aqui, em `.agents/agents/`**, nunca pelo caminho do link (`AGENTS.md` §2.3).

Agente novo: crie `.agents/agents/<nome>.md` com frontmatter `name` (igual ao nome do arquivo), `description` e
`tools`, com aspas na descrição se ela tiver `: `.
