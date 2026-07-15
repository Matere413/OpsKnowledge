# Supersession Index — Reposition RAG as OpsKnowledge

This index is the immutable fallback mapping required by design decision
"Historical record". It records that the OpsKnowledge SDD artifacts supersede
the prior dental-domain SDD artifacts, while the prior artifacts remain
reachable as audit history and are never deleted.

Supersession is one-directional: the OpsKnowledge artifact supersedes the
dental-domain artifact. The prior artifact is NOT modified and MUST stay
available as the prior audit baseline.

## Supersession relations

| Successor (OpsKnowledge) | Supersedes (dental-domain) | Relation | Reason |
|--------------------------|-----------------------------|----------|--------|
| proposal #3226 (topic `sdd/reposition-rag-as-portfolio-platform/proposal`) | proposal #3122 (topic `sdd/define-dental-guidance-domain-and-corpus/proposal`) | supersedes | Repositions the product from dental-guidance RAG to OpsKnowledge; preserves audit trail. |
| spec #3227 (topic `sdd/reposition-rag-as-portfolio-platform/spec`) | spec #3125 (topic `sdd/define-dental-guidance-domain-and-corpus/spec`) | supersedes | Replaces the dental-domain contract with the OpsKnowledge domain contract. |
| design #3228 (topic `sdd/reposition-rag-as-portfolio-platform/design`) | design #3133 (topic `sdd/define-dental-guidance-domain-and-corpus/design`) | supersedes | Replaces the dental-domain technical design with the OpsKnowledge repositioning design. |
| tasks #3229 (topic `sdd/reposition-rag-as-portfolio-platform/tasks`) | tasks #3134 (topic `sdd/define-dental-guidance-domain-and-corpus/tasks`) | supersedes | Replaces the dental-domain task plan with the OpsKnowledge repositioning task plan. |

## Relation persistence result

Each relation above is persisted via `engram_mem_compare` with
`relation: supersedes`. If a `mem_compare` call returns an error or an empty
`sync_id` indicating the relation could not be stored, this file remains the
authoritative immutable index and the relation is recorded here as fallback.

| Pair | `mem_compare` outcome | Stored? |
|------|------------------------|---------|
| #3226 supersedes #3122 | sync_id `rel-0bd3231f878ad881` | Yes |
| #3227 supersedes #3125 | sync_id `rel-66b6f2f6e5496faf` | Yes |
| #3228 supersedes #3133 | sync_id `rel-a7fa4ba265245ba5` | Yes |
| #3229 supersedes #3134 | sync_id `rel-d0003fa60ebb7edd` | Yes |

## Audit invariants

- Historical dental-domain artifacts (#3122, #3125, #3133, #3134) are NEVER
  deleted or modified.
- They remain reachable in Engram under their original topics.
- They are linked from `RAG_ROADMAP.md`, `docs/architecture/platform-architecture.md`,
  and `AGENTS.md` as superseded references where applicable.
- This index is immutable once the change is archived.