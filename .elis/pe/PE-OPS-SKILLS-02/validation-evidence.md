# Validation Evidence

## worktree-status
```text
$ git status -sb
## feature/pe-ops-skills-02-live-openclaw-context-gates...origin/main
?? .elis/pe/PE-OPS-SKILLS-02/
exit=0
```

## branch
```text
$ git branch --show-current
feature/pe-ops-skills-02-live-openclaw-context-gates
exit=0
```

## head
```text
$ git rev-parse HEAD
ea8a8c3b4e032cf2d7f4bc10125f7cb73f965bce
exit=0
```

## pointer-check
```text
$ bash -lc 'grep -n '"'"'Adjacent workspace skills\|Read `./SKILLS.md`'"'"' /home/samurai/openclaw/workspace-pm/AGENTS.md /home/samurai/openclaw/workspace-infra-impl/AGENTS.md /home/samurai/openclaw/workspace-infra-val/AGENTS.md /home/samurai/openclaw/workspace-prog-impl/AGENTS.md /home/samurai/openclaw/workspace-prog-val/AGENTS.md'
/home/samurai/openclaw/workspace-pm/AGENTS.md:6:## Adjacent workspace skills
/home/samurai/openclaw/workspace-pm/AGENTS.md:8:Read `./SKILLS.md` after this file. `AGENTS.md` stays the entry point; `SKILLS.md` holds the detailed model-agnostic operating rules for this workspace.
/home/samurai/openclaw/workspace-infra-impl/AGENTS.md:10:## Adjacent workspace skills
/home/samurai/openclaw/workspace-infra-impl/AGENTS.md:12:Read `./SKILLS.md` after this file. `AGENTS.md` stays the entry point; `SKILLS.md` holds the detailed model-agnostic operating rules for this workspace.
/home/samurai/openclaw/workspace-infra-val/AGENTS.md:9:## Adjacent workspace skills
/home/samurai/openclaw/workspace-infra-val/AGENTS.md:11:Read `./SKILLS.md` after this file. `AGENTS.md` stays the entry point; `SKILLS.md` holds the detailed model-agnostic operating rules for this workspace.
/home/samurai/openclaw/workspace-prog-impl/AGENTS.md:10:## Adjacent workspace skills
/home/samurai/openclaw/workspace-prog-impl/AGENTS.md:12:Read `./SKILLS.md` after this file. `AGENTS.md` stays the entry point; `SKILLS.md` holds the detailed model-agnostic operating rules for this workspace.
/home/samurai/openclaw/workspace-prog-val/AGENTS.md:10:## Adjacent workspace skills
/home/samurai/openclaw/workspace-prog-val/AGENTS.md:12:Read `./SKILLS.md` after this file. `AGENTS.md` stays the entry point; `SKILLS.md` holds the detailed model-agnostic operating rules for this workspace.
exit=0
```

## skills-exists
```text
$ bash -lc 'for f in /home/samurai/openclaw/workspace-pm/SKILLS.md /home/samurai/openclaw/workspace-infra-impl/SKILLS.md /home/samurai/openclaw/workspace-infra-val/SKILLS.md /home/samurai/openclaw/workspace-prog-impl/SKILLS.md /home/samurai/openclaw/workspace-prog-val/SKILLS.md; do test -f "$f" && echo FOUND:$f; done'
FOUND:/home/samurai/openclaw/workspace-pm/SKILLS.md
FOUND:/home/samurai/openclaw/workspace-infra-impl/SKILLS.md
FOUND:/home/samurai/openclaw/workspace-infra-val/SKILLS.md
FOUND:/home/samurai/openclaw/workspace-prog-impl/SKILLS.md
FOUND:/home/samurai/openclaw/workspace-prog-val/SKILLS.md
exit=0
```

## after-hashes
```text
$ bash -lc 'cat /opt/elis/agent-worktrees/PE-OPS-SKILLS-02/.elis/pe/PE-OPS-SKILLS-02/after-hashes.txt'
/home/samurai/openclaw/workspace-pm/AGENTS.md 5af8511c33df5220fffcbeea18eb0ad51f9b15721159895ad70ed1adcefc708a
/home/samurai/openclaw/workspace-pm/MEMORY.md 74b158a5f27f2a859b1644e56ce112b3c72727a142df55221f9cd7bfc45abdfb
/home/samurai/openclaw/workspace-pm/SKILLS.md 06d9797c1bfab285370f3d208131c22b6e2107cc90b89e1c2db9c0547a6b9938
/home/samurai/openclaw/workspace-infra-impl/AGENTS.md 0639c6298bf034cb992472bd495ec919a5b3e352f9527e6f7cd77ab7a4d89475
/home/samurai/openclaw/workspace-infra-impl/SKILLS.md f7359fe564003c81a74afbc3be04588f9022262fb36155c6f2a4651829ff06fb
/home/samurai/openclaw/workspace-infra-val/AGENTS.md 05dc067067e2da1aacda63d4eb791c5048e7e1381d8a27bdeb48dbeff13cf64b
/home/samurai/openclaw/workspace-infra-val/SKILLS.md 24f3981928047c37c4704fc9d7a502361a8ceda4737ad6af7a21d8d5574b4b88
/home/samurai/openclaw/workspace-prog-impl/AGENTS.md ea06f3dbdad66bdcce9a7f1b2411ab5eefc56e8faf11cd1a3e9f36d73352ae1c
/home/samurai/openclaw/workspace-prog-impl/SKILLS.md edcf844f6a1a061876714c30e589051b412130ed323b0f4ba0fb0389fb9b6878
/home/samurai/openclaw/workspace-prog-val/AGENTS.md 05a166c32c3158d8399f3a28ab297a1e7e5d6240586d97d2195318fe2166983f
/home/samurai/openclaw/workspace-prog-val/SKILLS.md b68433a8b0b831ba27da9cfd1e883601bd2d62f82a270b98f3171a847f9e42c7
exit=0
```
## backup-check
```text
$ bash -lc 'for f in /home/samurai/openclaw/workspace-pm/AGENTS.md.bak.20260514T0748Z /home/samurai/openclaw/workspace-pm/MEMORY.md.bak.20260514T0748Z /home/samurai/openclaw/workspace-infra-impl/AGENTS.md.bak.20260514T0748Z /home/samurai/openclaw/workspace-infra-val/AGENTS.md.bak.20260514T0748Z /home/samurai/openclaw/workspace-prog-impl/AGENTS.md.bak.20260514T0748Z /home/samurai/openclaw/workspace-prog-val/AGENTS.md.bak.20260514T0748Z; do test -f "$f" && echo FOUND:$f; done'
FOUND:/home/samurai/openclaw/workspace-pm/AGENTS.md.bak.20260514T0748Z
FOUND:/home/samurai/openclaw/workspace-pm/MEMORY.md.bak.20260514T0748Z
FOUND:/home/samurai/openclaw/workspace-infra-impl/AGENTS.md.bak.20260514T0748Z
FOUND:/home/samurai/openclaw/workspace-infra-val/AGENTS.md.bak.20260514T0748Z
FOUND:/home/samurai/openclaw/workspace-prog-impl/AGENTS.md.bak.20260514T0748Z
FOUND:/home/samurai/openclaw/workspace-prog-val/AGENTS.md.bak.20260514T0748Z
exit=0
```

## scope-check
```text
Agent scope clean — no secret-pattern files detected in worktree.
```
