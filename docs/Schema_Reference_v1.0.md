# Schema Reference v1.0

Este documento descreve a estrutura de schemas utilizados pelo **ELIS SLR Agent** para padronizar os dados em todas as etapas da Revisão Sistemática de Literatura (SLR).  
Baseado em: `ELIS_Data_Sheets_2025-08-17_v1.0.xlsx`

---

## Estrutura dos Schemas

### 1. Appendix A – Search Queries Schema
Define o formato das consultas de busca.

```json
{
  "id": "string",
  "database": "string",
  "query": "string",
  "date": "YYYY-MM-DD",
  "status": "draft | final",
  "notes": "string"
}
```

---

### 2. Appendix B – Screening Decisions Schema
Estrutura para registrar decisões de inclusão/exclusão.

```json
{
  "study_id": "string",
  "title": "string",
  "abstract": "string",
  "decision": "include | exclude | maybe",
  "criteria": "string",
  "reviewer": "string",
  "date": "YYYY-MM-DD"
}
```

---

### 3. Appendix C – Data Extraction Schema
Modelo para extrair informações de estudos incluídos.

```json
{
  "study_id": "string",
  "citation": "APA format string",
  "country": "string",
  "methodology": "string",
  "findings": "string",
  "limitations": "string",
  "tags": ["string"]
}
```

---

### 4. Appendix D – Audit Log Schema
Rastreamento das ações do agente.

```json
{
  "log_id": "string",
  "action": "search | screen | extract | review",
  "user_or_agent": "string",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "details": "string"
}
```

---

### 5. Appendix E – Thematic Codebook Schema
Estrutura para códigos temáticos e categorias.

```json
{
  "code_id": "string",
  "theme": "string",
  "definition": "string",
  "examples": ["string"],
  "created_by": "string",
  "last_updated": "YYYY-MM-DD"
}
```

---

### 6. Appendix F – AI Agent Logs Schema
Formato para registrar o comportamento do agente.

```json
{
  "session_id": "string",
  "agent_version": "string",
  "input": "string",
  "output": "string",
  "feedback": "string",
  "timestamp": "YYYY-MM-DD HH:MM:SS"
}
```

---

## Notas Finais

- Todos os schemas devem ser salvos em formato **JSON/JSONL**.  
- Validação automática será aplicada antes de qualquer uso pelo ELIS SLR Agent.  
- Versão: **1.0 (17/08/2025)**  
