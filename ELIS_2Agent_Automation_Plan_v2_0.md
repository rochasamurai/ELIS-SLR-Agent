# ELIS — Plano de Aperfeiçoamento do Modelo 2-Agents Autônomo

**Versão:** 2.0
**Data:** 2026-03-25
**Autor:** PM (Carlo) + Claude Code (análise e redação)
**Base:** Avaliação do modelo 2-Agents de 2026-03-25 · AGENTS.md v2.0 · ELIS_MultiAgent_Implementation_Plan_v1_6.md

---

## Changelog

| Versão | Data | Resumo |
|---|---|---|
| v1.0 | 2026-03-25 | Plano inicial — avaliação de gaps e 4 fases de automação (Fases A–D, 10 PEs) |
| v2.0 | 2026-03-25 | Adição da Fase 0 (auth sem API keys) com PE-AUTH-01 e PE-AUTH-02; avaliação e descarte de `agent-browser` para auth; adição de PE-SLR-HARVEST-WEB como PE futuro de SLR |

---

## Sumário Executivo

O modelo 2-Agents atual (CODEX + Claude Code, alternando implementer/validator por PE) tem uma
governança sólida mas exige intervenção manual do PO em cada PE: o PO faz PM-CHORE, assina o
Validator, lê PR comments e executa o merge. Este plano transforma o modelo em um **loop
autônomo** onde:

1. O **PM Agent** (ELIS no `elis-server`) recebe um plano, abre cada PE, notifica os agentes e
   fecha o loop de merge sem intervenção humana.
2. O par **Implementer + Validator** trabalha inteiramente via GitHub Actions, PR comments e
   REVIEW files.
3. Quando ocorre **divergência** (>2 FAILs, scope dispute, blocker técnico), o PM Agent arbitra.
   Somente em casos excepcionais o PO humano é notificado.
4. Os agentes autenticam-se usando **tokens de subscription** (sem API keys), reduzindo custo
   operacional e dependência de cotas de API.

O plano é dividido em **5 fases** (Fase 0 + Fases A–D), totalizando **12 PEs** de automação mais
um PE futuro de SLR.

> **Estado atual vs. estado-alvo:** Tudo descrito a partir da Fase B (loop autônomo) é um
> **estado-alvo futuro**, não o modelo de governança atual. O `AGENTS.md` permanece
> **autoritativo** até que cada PE de automação seja mergeado e explicitamente adotado.
> As Fases A–D não substituem nem conflituam com o workflow atual — elas o estendem
> progressivamente após validação.

---

## Estrutura do Plano

```
Fase 0  Auth sem API keys           2 PEs   (pré-bloqueante)
Fase A  Fundação — gaps estruturais 3 PEs   (pré-requisito para B)
Fase B  Loop autônomo               3 PEs   (pré-requisito para C)
Fase C  PM Agent árbitro            2 PEs   (pré-requisito para D)
Fase D  Operação completa           2 PEs
                                   ──────
Total                              12 PEs automação + 1 PE SLR (futuro)
```

---

## Análise de Contexto — Autenticação via Browser

### Documento avaliado

`open_claw_browser_auth_configuration_chat_gpt_claude.md` (ChatGPT, 2026-03-25)

### O que estava correto no documento ChatGPT

| Item | Status |
|---|---|
| `codex auth login` — OAuth browser flow | Válido — mecanismo real do Codex CLI |
| `claude setup-token` — token headless | Válido — suportado pelo Claude Code |
| Não copiar cookies / não interceptar tráfego | Correto — prática de segurança padrão |
| Role distribution (Codex=impl, Claude=validation) | Alinhado com AGENTS.md |

### O que estava fabricado (hallucinations)

| Afirmação | Problema |
|---|---|
| `openclaw models auth login --provider openai-codex` | Comando não existe no OpenClaw |
| `openclaw models auth paste-token --provider anthropic` | Idem — sem evidência no codebase |
| `"$schema": "https://docs.openclaw.ai/schema/openclaw.json"` | URL inexistente |
| Estrutura `agents.defaults.model.primary` + `agents.defaults.models` | Incompatível com `openclaw.json` real (`agents.list[]`) |
| `openai-codex/gpt-5.4` como ID de modelo | O repo usa `openai/gpt-5.1-codex` |
| `openai/gpt-5-mini` | Model ID não confirmado no runtime ELIS (não presente em `openclaw.json`) |
| `"context1m": false` | Parâmetro fictício da API Anthropic |

### Problema arquitetural central

O OpenClaw chama as APIs da OpenAI e Anthropic via HTTP com API keys
(`Authorization: Bearer sk-*`). A sessão de browser do ChatGPT.com ou Claude.ai usa cookies
de sessão que **não são aceitos** pelo endpoint `api.openai.com` ou `api.anthropic.com`.
São dois sistemas de autenticação completamente separados:

```
ChatGPT.com ←── browser session cookies ──→ chat.openai.com   (consumer web)
OpenAI API  ←── Authorization: Bearer sk-* ─→ api.openai.com  (developer API)
```

A solução correta para reduzir dependência de API keys é usar os binários CLI
(`codex`, `claude`) como execution backends nos runners de CI, autenticados via
OAuth token (`codex auth login`) e setup-token (`claude setup-token`) respectivamente.

### Avaliação de `vercel-labs/agent-browser`

**Repo:** `https://github.com/vercel-labs/agent-browser` · v0.22.2 · Rust · Apache-2.0

O `agent-browser` é uma CLI de automação de browser headless (Rust + CDP + Chrome headless)
projetada para ser usada **por** agentes de IA como ferramenta de trabalho — não como
mecanismo de autenticação.

| Uso proposto | Avaliação |
|---|---|
| Substituir `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` no OpenClaw | **Inaplicável** — não interfere com chamadas HTTP à API |
| Auth contínua para Codex/Claude no loop autônomo | **Inaplicável** — setup-token já é headless |
| Setup único de `codex auth login` em servidor headless | **Útil condicionalmente** — se port-forwarding não for viável |
| Harvest SLR de fontes sem API pública (IEEE, ACM, Springer) | **Adotar** — caso de uso de alto valor |
| Testes de smoke do PM Agent web | **Adotar futuramente** |

**Compatibilidade com elis-server:** ✓ Ubuntu 24.04 · x86_64 · headless · systemd-compatible

O `agent-browser` entra como PE futuro na fase de SLR (ver seção PE-SLR-HARVEST-WEB), não
na Fase 0 de autenticação.

---

## Fase 0 — Autenticação sem API Keys

> **Objetivo:** Substituir `OPENAI_API_KEY` e `ANTHROPIC_API_KEY` por autenticação via
> subscription nos runners de CI (GitHub Actions). É pré-requisito bloqueante para a Fase B,
> pois os runners de agente não devem depender de API keys.
>
> **Escopo:** GitHub Actions runners. O OpenClaw no `elis-server` mantém API keys até que
> o suporte a binários CLI como backends seja verificado (documentado em PE-AUTH-02).

---

### PE-AUTH-01 · Codex CLI — OAuth Token para Runners Headless

| Campo | Valor |
|---|---|
| Domínio | auth |
| Depends On | — |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Contexto:** O `codex auth login` abre um browser para o redirect OAuth. Em um runner
headless, o flow interativo não é aplicável. A solução proposta é um **offline token extraction**:
o PO faz `codex auth login` uma vez na máquina local; o token persistido é extraído e
armazenado como GitHub Secret.

> **⚠️ Mecanismo a validar — não assumir como fundação até PE-AUTH-01 concluído:**
> A portabilidade do token gerado pelo `codex auth login` entre máquinas, e o suporte oficial
> para reuso headless, não estão documentados publicamente. A Pré-verificação abaixo é
> **pré-requisito bloqueante** — o mecanismo exato só fica determinado após execução real.
> Fases posteriores (PE-AUTO-04 em diante) dependem do resultado desta validação.

**Pré-verificação obrigatória antes de implementar:**

```bash
# Na máquina do PO
codex auth login
# Após browser callback, localizar arquivo de token:
find ~/.codex ~/.config/openai -name "*.json" 2>/dev/null
codex auth status --verbose
```

O resultado determina o mecanismo exato:

| Cenário | Mecanismo |
|---|---|
| Token em arquivo JSON (`~/.codex/auth.json`) | Extrair refresh token → `CODEX_OAUTH_TOKEN` no GitHub Secrets |
| Token via variável de ambiente | Armazenar como `CODEX_ACCESS_TOKEN` |

**Entregáveis:**

- `docs/openclaw/CODEX_AUTH_SETUP.md` — runbook: geração, extração, armazenamento, renovação
- `scripts/extract_codex_token.py` — lê token local, imprime apenas metadados (expiry, scope) — nunca o valor (regra `§13`)
- `scripts/verify_codex_auth.py` — verifica se o token está válido no runner (existence check + `codex auth status`)

```python
# scripts/verify_codex_auth.py
import subprocess, sys
result = subprocess.run(["codex", "auth", "status"], capture_output=True, text=True)
if "authenticated" not in result.stdout.lower():
    print("FAIL: codex not authenticated", file=sys.stderr)
    sys.exit(1)
print("OK: codex auth valid")
```

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | `codex auth status` retorna `authenticated` em runner headless com secret configurado |
| AC-2 | Nenhum valor de token aparece em nenhum log de CI |
| AC-3 | `scripts/verify_codex_auth.py` exits 0 no runner |
| AC-4 | Runbook documenta procedimento de renovação com data de expiração esperada |
| AC-5 | Nenhum `OPENAI_API_KEY` presente nos workflows de runner de agente |

**Limitações documentadas:**

- Sujeito a limites de uso do ChatGPT Plus — não equivalente a throughput de API
- Token expira — renovação obrigatória antes de cada série longa de PEs
- [A VALIDAR] Monitoramento de quota: verificar se `codex auth status` expõe informação
  de cota/expiração antes de incluir no PM Agent loop (flag `--quota` não confirmado)

---

### PE-AUTH-02 · Claude Code — setup-token em Runners e Verificação no elis-server

| Campo | Valor |
|---|---|
| Domínio | auth |
| Depends On | — (paralelo a PE-AUTH-01) |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Dois contextos com mecanismos diferentes:**

#### Contexto A: GitHub Actions runner (agentes headless)

`claude setup-token` gera um token para uso CI/headless — mecanismo oficial da Anthropic.

```bash
# Na máquina do PO — gerar uma vez
claude setup-token
# Output: token "sk-ant-st-..."
# Armazenar como CLAUDE_SETUP_TOKEN no GitHub Secrets
```

No runner:

```bash
export CLAUDE_SETUP_TOKEN="${{ secrets.CLAUDE_SETUP_TOKEN }}"
claude --version   # verifica que funciona sem ANTHROPIC_API_KEY
```

`scripts/verify_claude_auth.py`:

```python
import subprocess, sys, os
if not os.environ.get("CLAUDE_SETUP_TOKEN"):
    print("FAIL: CLAUDE_SETUP_TOKEN not set", file=sys.stderr)
    sys.exit(1)
result = subprocess.run(["claude", "--version"], capture_output=True)
if result.returncode != 0:
    print("FAIL: claude CLI not available", file=sys.stderr)
    sys.exit(1)
print("OK: claude auth ready")
```

#### Contexto B: OpenClaw no elis-server

Pré-verificação obrigatória — determina se `ANTHROPIC_API_KEY` pode ser eliminada do elis-server:

```bash
# No elis-server — testar as três hipóteses:

# Hipótese 1: OpenClaw aceita CLAUDE_SETUP_TOKEN como variável de ambiente alternativa
CLAUDE_SETUP_TOKEN=<token> openclaw agent run --agent-id infra-impl-claude --task "ping"

# Hipótese 2: setup-token pode ser convertido em API key temporária
claude api-key --from-setup-token  # se existir

# Hipótese 3: OpenClaw não suporta — ANTHROPIC_API_KEY permanece para o elis-server
```

**Se Context B não for suportado:** `ANTHROPIC_API_KEY` permanece no `elis-server` (documentado
com data de revisão). O setup-token é aplicado apenas aos runners de CI (Context A).

**Entregáveis:**

- `docs/openclaw/CLAUDE_AUTH_SETUP.md` — runbook completo para ambos os contextos
- `scripts/verify_claude_auth.py`
- Resultado documentado da verificação de Context B

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Runner headless executa `claude --version` sem `ANTHROPIC_API_KEY`, usando `CLAUDE_SETUP_TOKEN` |
| AC-2 | Nenhum valor de token em nenhum log |
| AC-3 | `scripts/verify_claude_auth.py` exits 0 |
| AC-4 | Context B documentado com resultado de verificação (suportado / não-suportado / workaround) |
| AC-5 | Se Context B não-suportado: decisão registrada com data de revisão no runbook |

---

## Fase A — Fundação (gaps estruturais)

> **Objetivo:** Eliminar os três gaps estruturais que impedem automação confiável, identificados
> na avaliação de 2026-03-25. Pré-requisito para a Fase B.

---

### PE-AUTO-01 · Bot Accounts e GitHub Fine-Grained PATs

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTH-01, PE-AUTH-02 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Problema que resolve:** Single-account GitHub constraint — o Validator não pode emitir
GitHub Review formal no próprio PR (avaliação §2.1).

**Três identidades GitHub separadas:**

| Conta | Engine | Papel | PAT Scopes |
|---|---|---|---|
| `elis-codex-bot` | CODEX | Implementer ou Validator conforme PE | Contents write, Pull requests write, Issues write |
| `elis-claude-bot` | Claude Code | Implementer ou Validator conforme PE | Contents write, Pull requests write, Issues write |
| `elis-pm-bot` | PM Agent / CI orchestration | Sequencer, arbiter, merge | Contents write, Pull requests write, Issues write, Workflows read |

GitHub Secrets do repositório:

```
CODEX_BOT_TOKEN        ← PAT de elis-codex-bot
CLAUDE_BOT_TOKEN       ← PAT de elis-claude-bot
PM_BOT_TOKEN           ← PAT de elis-pm-bot
CODEX_OAUTH_TOKEN      ← token OAuth do Codex CLI (PE-AUTH-01)
CLAUDE_SETUP_TOKEN     ← setup-token do Claude Code (PE-AUTH-02)
```

**Branch protection atualizada para `main`:**

- Require 1 approving review de `elis-claude-bot` ou `elis-codex-bot` (não o autor do PR)
- Status checks obrigatórios: `quality`, `tests`, `validate`, `gate-1`
- Direct push bloqueado — PRs obrigatórios

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | `elis-codex-bot` abre PR e `elis-claude-bot` aprova (sem "Cannot approve your own PR") |
| AC-2 | Branch protection ativa — PR sem status check verde não mergea |
| AC-3 | Secrets configurados — `verify_codex_auth.py` e `verify_claude_auth.py` exitam 0 nos runners |
| AC-4 | `OPENAI_API_KEY` e `ANTHROPIC_API_KEY` removidos dos runners de agente |

---

### PE-AUTO-02 · Validação de CURRENT_PE.md no CI

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-01 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Problema que resolve:** `CURRENT_PE.md` como single point of failure sem schema validation
(avaliação §2.2). Elimina a classe de erro LL-05 (PE pulado por edição manual incorreta).

**Entregáveis:**

`scripts/check_current_pe.py` — verifica:

1. Todos os campos obrigatórios presentes e não-vazios (`PE`, `Branch`, `Base branch`,
   `Plan file`, `Agent roles`)
2. PE ID no formato correto (`PE-[A-Z]+-[0-9]+`)
3. Branch segue convenção `feature/pe-*` ou `chore/*`
4. Status do PE ativo é `planning` ou `implementing`
5. **Alternation rule:** engine do implementer ≠ engine do último PE `merged` no mesmo domínio
6. Agent roles são opostos (impl engine ≠ val engine)

CI step em pushes para `main` (`ci.yml`):

```yaml
- name: Validate CURRENT_PE.md
  run: python scripts/check_current_pe.py
```

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | `check_current_pe.py` exits 0 no estado atual do `CURRENT_PE.md` |
| AC-2 | Campo em branco → exits 1 com mensagem de erro descritiva |
| AC-3 | Violação de alternation rule → exits 1 |
| AC-4 | CI step ativo — push com `CURRENT_PE.md` inválido é bloqueado |
| AC-5 | 8 testes unitários cobrindo todos os casos de validação |

---

### PE-AUTO-03 · Pre-commit Hooks + HANDOFF Namespacing

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-02 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Problemas que resolve:**

- Ausência de pre-commit hooks — black/ruff só verificados no CI após push (avaliação §2.5)
- `HANDOFF.md` no root sobrescrito a cada PE — colisão entre PEs (avaliação §2.4)

**`.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
  - repo: local
    hooks:
      - id: scope-gate
        name: Agent scope gate
        entry: python scripts/check_agent_scope.py
        language: python
        pass_filenames: false
      - id: current-pe-validation
        name: Validate CURRENT_PE.md
        entry: python scripts/check_current_pe.py
        language: python
        files: CURRENT_PE.md
        pass_filenames: false
```

**Namespacing de HANDOFF:**

```
handoffs/
  HANDOFF_PE-MS-06.md    ← histórico imutável (migrado do root)
  HANDOFF_PE-MS-05.md
  HANDOFF_PE-MS-04.md
  ...
HANDOFF.md               ← cópia gerada por script do PE ativo
                           (NOT symlink — symlinks são frágeis no Windows/git)
```

O `pe_sequencer.py` escreve a cópia de `handoffs/HANDOFF_{PE_ATIVO}.md` para o root
`HANDOFF.md` a cada avanço de PE. Não utilizar symlinks — comportamento inconsistente
entre Windows (core.symlinks=false por padrão) e Linux.

`check_handoff.py` atualizado para:
- Aceitar root `HANDOFF.md` (forma atual) durante migração
- Após migração completa: verificar também `handoffs/HANDOFF_{PE_ID}.md` com base no
  `CURRENT_PE.md`

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | `pre-commit run --all-files` exits 0 no estado atual do repo |
| AC-2 | `git commit` com black error é bloqueado localmente (pre-commit hook ativo) |
| AC-3 | HANDOFFs históricos migrados para `handoffs/` — root `HANDOFF.md` é cópia gerada por script (não symlink) |
| AC-4 | `check_handoff.py` exits 0 resolvendo via root `HANDOFF.md` e via `handoffs/HANDOFF_{PE_ID}.md` |
| AC-5 | Documentação de onboarding atualizada com instrução de `pre-commit install` |

---

## Fase B — Loop Autônomo de PE

> **Objetivo:** O par Implementer + Validator executa um PE completo sem intervenção humana.
> O trigger é o push de `CURRENT_PE.md` pelo PM Agent; o fechamento é o auto-merge do Gate 2.

---

### PE-AUTO-04 · Implementer Agent Runner

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTH-01, PE-AUTH-02, PE-AUTO-01 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Trigger:** push de `CURRENT_PE.md` para `main` com status `planning → implementing`
(detectado por `ci-current-pe.yml` → `workflow_dispatch` para `implementer-runner.yml`).

**`implementer-runner.yml` (fragmento):**

```yaml
name: Implementer Agent Runner
on:
  workflow_dispatch:
    inputs:
      pe_id:       { required: true }
      branch:      { required: true }
      engine:      { required: true }   # codex | claude
      plan_file:   { required: true }
      base_branch: { required: true }

jobs:
  run-implementer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate Codex CLI
        if: inputs.engine == 'codex'
        env:
          CODEX_OAUTH_TOKEN: ${{ secrets.CODEX_OAUTH_TOKEN }}
        run: python scripts/verify_codex_auth.py

      - name: Authenticate Claude CLI
        if: inputs.engine == 'claude'
        env:
          CLAUDE_SETUP_TOKEN: ${{ secrets.CLAUDE_SETUP_TOKEN }}
        run: python scripts/verify_claude_auth.py

      - name: Run Implementer Agent (CODEX)
        if: inputs.engine == 'codex'
        env:
          GH_TOKEN: ${{ secrets.CODEX_BOT_TOKEN }}
        run: |
          python scripts/run_codex_agent.py \
            --pe-id "${{ inputs.pe_id }}" \
            --plan "${{ inputs.plan_file }}" \
            --branch "${{ inputs.branch }}"

      - name: Run Implementer Agent (Claude)
        if: inputs.engine == 'claude'
        env:
          GH_TOKEN: ${{ secrets.CLAUDE_BOT_TOKEN }}
        run: |
          python scripts/run_claude_agent.py \
            --pe-id "${{ inputs.pe_id }}" \
            --plan "${{ inputs.plan_file }}" \
            --branch "${{ inputs.branch }}"
```

Os scripts `run_codex_agent.py` / `run_claude_agent.py`:

1. Constroem o prompt de sistema a partir de `AGENTS.md` + `CURRENT_PE.md` + acceptance
   criteria do PE no plano
2. Invocam o binário CLI (`codex` / `claude`) com tool use (git, gh CLI, python)
3. Seguem o fluxo §5.1 autonomamente: implementar → quality gates → HANDOFF → draft PR
   → ready PR → Status Packet
4. Têm limite de `MAX_COMMITS=20` e timeout de 4h por segurança

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Runner dispara ao detectar mudança em `CURRENT_PE.md` com status `implementing` |
| AC-2 | Auth via `CODEX_OAUTH_TOKEN` / `CLAUDE_SETUP_TOKEN` — sem `OPENAI_API_KEY` |
| AC-3 | PR aberto pela conta correta (`elis-codex-bot` ou `elis-claude-bot`) |
| AC-4 | `HANDOFF.md` commitado antes do PR ser convertido para ready |
| AC-5 | Runner encerra com exit 1 se `MAX_COMMITS` ou timeout forem atingidos |

---

### PE-AUTO-05 · Validator Agent Runner

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-04 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Trigger:** Gate 1 CI posta o comment `@claude-code — assigned as Validator. Begin review.`
(já implementado em `auto-assign-validator.yml`). Novo workflow `validator-dispatch.yml`
detecta o comment e dispara `validator-runner.yml` com o engine correto.

**Fluxo do Validator Runner:**

1. Lê `HANDOFF.md` e verifica scope via `git diff --name-status`
2. Roda quality gates
3. Valida cada AC verbatim do plano
4. Adiciona testes adversariais
5. Escreve `REVIEW_PE<N>.md` com veredicto
6. Verifica com `check_review.py` antes de commitar
7. Posta PR review formal via `elis-claude-bot` ou `elis-codex-bot`
   (conta oposta ao author do PR — eliminando o single-account constraint)

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Validator dispara automaticamente após comment de Gate 1 |
| AC-2 | `REVIEW_PE<N>.md` commitado na branch com evidência verbatim |
| AC-3 | GitHub Review formal (`approve` / `request-changes`) postado pela conta oposta |
| AC-4 | Gate 2 lê o veredicto e auto-merges no PASS |
| AC-5 | No FAIL: Implementer recebe fix assignment via PR comment de `elis-pm-bot` |

---

### PE-AUTO-06 · PE Sequencer — Avanço Automático entre PEs

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-02, PE-AUTO-05 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Trigger:** `pull_request` tipo `closed` + `merged == true` em branches `feature/**`.

**`scripts/pe_sequencer.py`:**

1. Lê o plano e identifica o PE merged
2. Marca status `merged` no registry de `CURRENT_PE.md`
3. Identifica o próximo PE na sequência respeitando `Depends On` (DAG)
4. Aplica a alternation rule para definir engine do próximo implementer
5. Abre novo branch via `git checkout -b`
6. Atualiza `CURRENT_PE.md` com novo PE, branch, e agent roles
7. Commita como `elis-pm-bot` com mensagem `chore(pm): auto-advance to PE-XXXX`
8. Dispara `implementer-runner.yml` via `workflow_dispatch`

Se não houver próximo PE disponível (dependência não satisfeita ou fim da série):
notifica PM Agent no Discord e encerra o loop aguardando instrução do PO.

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Após merge de PE-N, `CURRENT_PE.md` é atualizado automaticamente para PE-N+1 |
| AC-2 | Alternation rule é respeitada — verificada por `check_current_pe.py` |
| AC-3 | Se próximo PE tiver dependência não satisfeita: loop para e notifica Discord |
| AC-4 | Fim da série: PM Agent posta summary de conclusão no Discord |
| AC-5 | Todos os PM-CHOREs automáticos ficam registrados no housekeeping table |

---

## Fase C — PM Agent como Árbitro

> **Objetivo:** O PM Agent (ELIS) resolve divergências entre agentes sem escalar para o PO.
> Ativado pelos gatilhos abaixo; o PO só é chamado em casos excepcionais.

---

### PE-AUTO-07 · Protocolo de Arbitragem do PM Agent

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-04, PE-AUTO-05 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Gatilhos de arbitragem:**

| Gatilho | Condição | Detecção |
|---|---|---|
| FAIL round 3 | Terceiro ciclo de FAIL no mesmo PE | Counter no PR labels |
| Scope dispute | Validator alega out-of-scope, Implementer discorda | Keyword no REVIEW file |
| Blocker técnico | CI falha com `pm-escalation` flag | Workflow output |
| Timeout | Runner sem commit por >4h | Workflow elapsed time check |

**Fluxo de arbitragem (`pm-arbiter.yml`):**

```
Trigger detectado
  └─> PM Agent lê:
        - CURRENT_PE.md (contexto do PE)
        - acceptance criteria no plano
        - HANDOFF.md (posição do Implementer)
        - REVIEW_PE<N>.md (posição do Validator)
        - git diff --name-status (scope real vs. declarado)
  └─> Decide entre 4 opções:
        SIDE_IMPLEMENTER  → Validator overscoped; PM justifica e instrui aceitar
        SIDE_VALIDATOR    → Implementer deve corrigir; post fix assignment
        SPLIT_PE          → Conflito legítimo; cria PE adicional no plano
        ESCALATE_PO       → Além da capacidade de arbitragem; notifica PO humano
  └─> Posta decisão no PR como elis-pm-bot (seção "## PM Arbitration")
  └─> Atualiza CURRENT_PE.md status → "arbitration-resolved" ou "blocked"
  └─> Adiciona entrada em LESSONS_LEARNED.md automaticamente
```

**Critérios de escalonamento para PO humano** (únicos casos que chegam ao humano):

- Conflito de arquitetura que exige decisão sobre escopo do produto
- Ambiguidade no plano que o PM Agent não consegue resolver pelos acceptance criteria
- >3 iterações de arbitragem no mesmo PE
- Qualquer PE que toque secrets ou credenciais de produção

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Arbitragem disparada automaticamente no FAIL round 3 |
| AC-2 | Decisão postada como PR comment de `elis-pm-bot` com seção `## PM Arbitration` |
| AC-3 | Entrada criada em `LESSONS_LEARNED.md` para cada arbitragem |
| AC-4 | ESCALATE_PO notifica PO no Discord com resumo estruturado |
| AC-5 | Nenhum PE em `blocked` por mais de 24h sem notificação ao PO |

---

### PE-AUTO-08 · Discord Loop para Operação Autônoma

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-06, PE-AUTO-07 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

O PM Agent já tem integração Discord (PE-MS-03). Esta PE expande o protocolo para o loop
autônomo, adicionando eventos de ciclo de vida de PE e comandos de controle do PO.

**Eventos reportados automaticamente:**

```
[AUTO] PE-MS-07 started · Implementer: elis-codex-bot · Auth: OAuth ✓
[AUTO] PE-MS-07 Gate 1 PASS · Validator assigned: elis-claude-bot
[AUTO] PE-MS-07 FAIL round 2 · Arbiter triggered
[ARBITER] PE-MS-07 → SIDE_VALIDATOR · fix AC-3 scope
[AUTO] PE-MS-07 PASS · merged · next: PE-MS-08 auto-starting
[ESCALATE] PE-MS-09 requires PO decision · reason: architecture ambiguity
```

**Comandos Discord do PO:**

| Comando | Ação |
|---|---|
| `!pe status` | Estado do loop — PE ativo, round, agentes, quota de auth |
| `!pe veto` | Aplica `pm-review-required` no PR aberto |
| `!pe pause` | Para o sequencer após o PE atual |
| `!pe resume` | Retoma o sequencer |
| `!pe auth-check` | Verifica validade dos tokens OAuth/setup-token sem imprimir valores |
| `!pe override PASS` | Força merge com auditoria obrigatória em `LESSONS_LEARNED.md` |

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Cada evento de ciclo de vida de PE postado no Discord dentro de 60s do trigger |
| AC-2 | `!pe status` retorna estado atual com taxa de autonomia |
| AC-3 | `!pe veto` aplica label e para o sequencer em <30s |
| AC-4 | `!pe auth-check` reports token status sem expor valores |
| AC-5 | ESCALATE_PO menciona `@` do PO no Discord |

---

## Fase D — Operação Completa

> **Objetivo:** O PO entrega um novo plano e o sistema executa todos os PEs autonomamente,
> com visibilidade contínua via Discord e dashboard.

---

### PE-AUTO-09 · Plan Loader — Ingestão de Novo Plano

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-06, PE-AUTO-08 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Entregável:** `scripts/plan_loader.py` + JSON Schema `schemas/plan_schema.json`

Validações antes de iniciar a série:

1. Schema JSON válido (campos obrigatórios por PE: `id`, `domain`, `depends_on`,
   `implementer`, `validator`, `acceptance_criteria`)
2. Todos os `depends_on` formam um DAG válido (sem ciclos)
3. Alternation rule pode ser aplicada a toda a série sem violações
4. Primeira PE tem `depends_on: []` ou dependências já `merged`

**Interfaces de entrega:**

- **Discord:** `!plan load` com arquivo `.md` ou `.json` anexado
- **PR direto:** PO abre PR com o arquivo do plano. CI valida. Aprovação do PR = autorização de início.

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | `plan_loader.py` exits 0 para plano válido, 1 com diagnóstico para inválido |
| AC-2 | Ciclo em DAG de dependências → rejeitado com diagrama do ciclo |
| AC-3 | Violação de alternation rule → rejeitado com indicação do PE problema |
| AC-4 | `CURRENT_PE.md` gerado automaticamente para o primeiro PE |
| AC-5 | Discord `!plan load` confirma validação antes de iniciar sequencer |

---

### PE-AUTO-10 · Observability Dashboard

| Campo | Valor |
|---|---|
| Domínio | infra |
| Depends On | PE-AUTO-09 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Entregável:** `scripts/generate_pe_status_report.py`

Saída de exemplo:

```
PE Series: ELIS MiniServer v1.6
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PE-MS-01  merged    2026-03-23  PASS (round 1)
PE-MS-02  merged    2026-03-23  PASS (round 1)
PE-MS-03  merged    2026-03-24  PASS (round 3 — 2 arbiter interventions)
PE-MS-04  merged    2026-03-25  PASS (round 1)
PE-MS-05  merged    2026-03-25  PASS (round 1)
PE-MS-06  active    —           implementing · elis-codex-bot · started 14:32
PE-MS-07  planned   —           waiting on PE-MS-06
PE-MS-08  planned   —           waiting on PE-MS-07
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Autonomy rate: 5/5 PEs merged sem escalonamento (100%)
Arbiter interventions: 2 (PE-MS-03)
PO interventions: 0
Auth status: codex OK (expires 2026-04-25) · claude OK (no expiry)
```

Postado no canal Discord `#pe-status` a cada hora via PM Agent cron.

**Acceptance Criteria:**

| # | Critério |
|---|---|
| AC-1 | Report gerado corretamente a partir do estado atual de `CURRENT_PE.md` |
| AC-2 | Taxa de autonomia calculada corretamente |
| AC-3 | Status de validade de auth incluído sem expor valores |
| AC-4 | PM Agent posta report no Discord a cada hora |
| AC-5 | `!pe status` usa o mesmo report para resposta on-demand |

---

## PE Futuro — SLR Harvest Web

### PE-SLR-HARVEST-WEB · agent-browser para Fontes sem API Pública

| Campo | Valor |
|---|---|
| Domínio | slr |
| Depends On | PE-MS-06 (workspaces SLR phase) |
| Implementer | `harvest-impl-codex` |
| Validator | `harvest-val-claude` |

**Motivação:** O pipeline SLR atual tem 3 adaptadores (Crossref, OpenAlex, Scopus). Fontes
relevantes como IEEE Xplore, ACM Digital Library, Springer Link e Web of Science não têm
API pública gratuita mas têm portais web com suporte a busca avançada.

**`agent-browser`** (`vercel-labs/agent-browser` v0.22.2, Apache-2.0) é uma CLI de automação
de browser headless em Rust, compatível com Ubuntu 24.04 x86_64, com daemon persistente
e criptografia AES-256-GCM de estado de sessão.

**Compatibilidade com elis-server:**

| Requisito | elis-server | agent-browser | Status |
|---|---|---|---|
| OS | Ubuntu 24.04.4 LTS | Linux x64 nativo | ✓ |
| Arquitetura | x86_64 | `agent-browser-linux-x64` | ✓ |
| Chrome | Não instalado | `agent-browser install --with-deps` | ✓ |
| Display | Headless | Daemon headless por padrão | ✓ |
| Systemd | Ativo | `AGENT_BROWSER_IDLE_TIMEOUT_MS` | ✓ |
| Criptografia de sessão | `§13` exige | AES-256-GCM via env var | ✓ |
| Memória | 16 GB total | ~400 MB por instância Chrome | Monitorar |

**Limitação operacional:** `maxConcurrent: 1` para agentes com `agent-browser` — evitar
instâncias paralelas de Chrome no NUC8i7BEH.

**Escopo desta PE:**

- Instalar `agent-browser` no `elis-server` como tool disponível nos workspaces de harvest
- Configurar criptografia de sessão (`AGENT_BROWSER_ENCRYPTION_KEY` em `.openclaw/.env`)
- Adaptar o pipeline de harvest para consumir saída de `agent-browser` via JSONL
- Documentar procedimento de login inicial para cada fonte (auth vault)

---

## Roadmap e Dependências

```
Fase 0 (auth)           Fase A (fundação)       Fase B (loop)           Fase C/D (árbitro+full)
━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━
PE-AUTH-01 Codex OAuth  PE-AUTO-01 Bot accounts  PE-AUTO-04 Impl runner  PE-AUTO-07 Arbitragem
PE-AUTH-02 Claude token PE-AUTO-02 CurrentPE CI  PE-AUTO-05 Val runner   PE-AUTO-08 Discord loop
(paralelos)             PE-AUTO-03 pre-commit     PE-AUTO-06 Sequencer   PE-AUTO-09 Plan loader
                                                                          PE-AUTO-10 Dashboard
[ pré-verificação ]     [ exige Fase 0 ]          [ exige Fase A ]       [ exige Fase B ]
~3–5 dias               ~1 semana                 ~2 semanas             ~1 semana
```

**Dependências críticas:**

| PE | Depende de | Motivo |
|---|---|---|
| PE-AUTO-01 | PE-AUTH-01 + PE-AUTH-02 | Runners precisam de tokens antes de usar os bots |
| PE-AUTO-04 | PE-AUTH-01/02 + PE-AUTO-01 | Engine + identidade GitHub separados |
| PE-AUTO-06 | PE-AUTO-02 | Sequencer só avança após validação de CURRENT_PE.md |
| PE-AUTH-02 Context B | Pré-verificação manual | Resultado determina se ANTHROPIC_API_KEY permanece no elis-server |
| PE-SLR-HARVEST-WEB | PE-MS-06 | Workspaces de harvest phase devem existir |

---

## Riscos e Mitigações

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| Token OAuth Codex expira durante série longa | Alta | Alto | [A VALIDAR em PE-AUTH-01] Renovação manual obrigatória; `!pe auth-check` on-demand; mecanismo de monitoramento de quota a ser determinado após validação do token |
| Agente implementer em loop de commits | Média | Alto | `MAX_COMMITS=20` e timeout 4h no runner; exit 1 automático |
| PM Agent toma decisão de arbitragem errada | Média | Médio | Todo arbiramento registrado em PR comment auditável; PO pode rever e usar `!pe override` |
| GitHub rate limit por uso de bot accounts | Baixa | Alto | Fine-grained PATs com escopo mínimo; `elis-pm-bot` separa operações de merge das de código |
| CURRENT_PE.md corrompido pelo sequencer | Baixa | Alto | `check_current_pe.py` bloqueia estado inválido antes de dispatch; git history preserva estado |
| Chrome headless consome memória excessiva | Média (harvest) | Médio | `maxConcurrent: 1` para agentes com agent-browser; monitoramento via PM Agent |
| OpenClaw não suporta setup-token em Context B | Alta | Baixo | Documentado em AC-5 de PE-AUTH-02; ANTHROPIC_API_KEY permanece no elis-server com plano de revisão |

---

## O que NÃO foi incorporado do documento ChatGPT

| Item descartado | Motivo |
|---|---|
| `openclaw models auth login/paste-token` | Comando não existe no OpenClaw real |
| Formato JSON `agents.defaults.model.primary` | Incompatível com `openclaw.json` real do projeto |
| `openai-codex/gpt-5.4` / `openai/gpt-5-mini` | Model IDs não confirmados no runtime ELIS — repo usa `openai/gpt-5.1-codex` |
| `"context1m": false` | Parâmetro fictício da API Anthropic |
| `agent-browser` como substituto de API key | Tecnicamente incompatível — browser cookies ≠ API keys |

---

*ELIS 2-Agent Automation Plan v2.0 · 2026-03-25*
