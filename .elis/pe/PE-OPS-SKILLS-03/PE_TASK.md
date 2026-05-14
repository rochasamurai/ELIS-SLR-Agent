{
  "pe_id": "PE-OPS-SKILLS-03",
  "title": "Containerisation Phase-Gate Skill Implementation",
  "description": "Implement the containerisation phase-gate skill for Planning, Build-preflight, Smoke-test, and Cutover phases.",
  "scope": [
    "Define containerisation phase-gate skill",
    "Keep smoke-test as a rule only",
    "Do NOT run container tests or smoke-tests in this PE",
    "Do NOT change runtime/config/auth/container/GitHub/A2A/Dash/model/provider settings"
  ],
  "deliverables": [
    "docs/governance/ELIS_Container_Pilot_Phase_Gate_Skill.md",
    ".elis/pe/PE-OPS-SKILLS-03/HANDOFF.md",
    ".elis/pe/PE-OPS-SKILLS-03/validation-evidence.md",
    ".elis/pe/PE-OPS-SKILLS-03/rollback-plan.md"
  ],
  "acceptance_criteria": [
    "Phase-gate skill correctly defines Planning, Build-preflight, Smoke-test, and Cutover phases",
    "Smoke-test is defined as a rule only without execution",
    "No containerisation changes or test executions in this PE",
    "All governance documentation is consistent"
  ],
  "phase_gate_skill": {
    "definition": "Containerisation phase-gate skill that governs infrastructure changes through four distinct phases",
    "phases": {
      "planning": "Initial planning and design of containerisation strategy",
      "build_preflight": "Preparation and validation before container build",
      "smoke_test": "Basic verification phase only (no execution)",
      "cutover": "Migration and transition to containerised environment"
    }
  }
}