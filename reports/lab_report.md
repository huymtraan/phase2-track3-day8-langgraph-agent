# Day 08 Lab Report

## 1. Team / student

- Name: Trần Thái Huy
- Date: 2026-05-11

## 2. Architecture

The workflow is a LangGraph support-ticket agent. Each run starts at `intake`, normalizes
the query, classifies it into a route, then follows conditional edges to the correct
handling path. Simple requests are answered directly. Tool requests call the mock tool,
evaluate the result, and answer. Missing-information requests ask a clarification
question. Risky requests prepare an action, require mock human approval, then continue
through the tool/evaluate/answer path. Error requests enter a bounded retry loop and
move to `dead_letter` when `max_attempts` is exhausted.

## 3. State schema

| Field | Reducer | Why |
|---|---|---|
| thread_id, scenario_id, query | overwrite | identify and normalize one run |
| route, risk_level | overwrite | keep the current routing decision |
| attempt, max_attempts | overwrite | control bounded retry behavior |
| final_answer, pending_question | overwrite | expose the terminal response |
| proposed_action, approval | overwrite | store risky-action approval state |
| evaluation_result | overwrite | gate retry versus answer after tool execution |
| messages, tool_results, errors, events | append | preserve audit history for metrics/debugging |

## 4. Scenario results

| Scenario | Expected route | Actual route | Success | Retries | Interrupts |
|---|---|---|---:|---:|---:|
| S01_simple | simple | simple | yes | 0 | 0 |
| S02_tool | tool | tool | yes | 0 | 0 |
| S03_missing | missing_info | missing_info | yes | 0 | 0 |
| S04_risky | risky | risky | yes | 0 | 1 |
| S05_error | error | error | yes | 2 | 0 |
| S06_delete | risky | risky | yes | 0 | 1 |
| S07_dead_letter | error | error | yes | 1 | 0 |

## 5. Metrics summary

- Total scenarios: 7
- Success rate: 100.00%
- Average nodes visited: 6.43
- Total retries: 3
- Total interrupts: 2

## 6. Failure analysis

1. Retry or tool failure: the mock tool emits `ERROR` for the error route until the
   retry count reaches the success threshold or `max_attempts` is exhausted. The
   evaluator sets `evaluation_result=needs_retry`, and routing sends the run to
   `retry` or `dead_letter`.
2. Risky action without approval: risky keywords such as refund, delete, send, cancel,
   remove, or revoke route to `risky_action` first. The approval node must complete
   before the graph can continue to tool execution.

## 7. Persistence / recovery evidence

The baseline configuration uses the LangGraph `MemorySaver` checkpointer and passes a
unique `thread_id` for every scenario run. This keeps per-run state isolated and enables
checkpointed execution during the scenario runner.

## 8. Extension work

No bonus extension was implemented for this submission. The scope is the required
baseline workflow, scenario metrics, and report.

## 9. Improvement plan

With more time, the first production improvement would be replacing keyword routing
with structured intent classification and stronger validation around tool outputs,
while keeping the same graph-level retry, approval, and dead-letter controls.
