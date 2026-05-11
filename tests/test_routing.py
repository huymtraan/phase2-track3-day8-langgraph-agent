from langgraph_agent_lab.nodes import classify_node
from langgraph_agent_lab.routing import (
    route_after_approval,
    route_after_classify,
    route_after_evaluate,
    route_after_retry,
)
from langgraph_agent_lab.state import Route


def test_route_after_classify():
    assert route_after_classify({"route": Route.SIMPLE.value}) == "answer"
    assert route_after_classify({"route": Route.TOOL.value}) == "tool"
    assert route_after_classify({"route": Route.RISKY.value}) == "risky_action"


def test_route_after_approval():
    assert route_after_approval({"approval": {"approved": True}}) == "tool"
    assert route_after_approval({"approval": {"approved": False}}) == "clarify"


def test_route_after_retry_bound():
    assert route_after_retry({"attempt": 0, "max_attempts": 3}) == "tool"
    assert route_after_retry({"attempt": 3, "max_attempts": 3}) == "dead_letter"


def test_route_after_evaluate():
    assert route_after_evaluate({"evaluation_result": "success"}) == "answer"
    assert route_after_evaluate({"evaluation_result": "needs_retry"}) == "retry"


def test_classify_risky_priority_over_tool_words():
    result = classify_node({"query": "Please cancel and check order status"})
    assert result["route"] == Route.RISKY.value


def test_classify_missing_info_uses_whole_words():
    assert classify_node({"query": "Can you fix it?"})["route"] == Route.MISSING_INFO.value
    assert classify_node({"query": "iteration status"})["route"] == Route.TOOL.value


def test_classify_error_keywords():
    assert classify_node({"query": "Service unavailable after crash"})["route"] == Route.ERROR.value
