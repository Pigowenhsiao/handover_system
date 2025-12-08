<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Communication
- 與使用者互動時一律使用繁體中文回覆，無論使用者使用何種語言。

## 執行策略
- 預設 approval_policy = never，所有指令免逐次核准。
## 執行環境（供後續協作參考）
- sandbox_mode: danger-full-access
- approval_policy: on-failure
- network_access: restricted（如需網路請先確認）
