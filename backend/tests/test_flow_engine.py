"""Tests for the flow engine."""

import pytest
from v1.models import (
    Form,
    FormGraphEdge,
    FormGraphNode,
    FormVersion,
    Organization,
    RespondentSession,
)
from v1.services.flow_engine import process_user_message, start_session_prompt


@pytest.fixture
def form_with_graph(db_session):
    """Create a test form with a linear 3-question graph."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.flush()

    form = Form(
        org_id=org.id,
        title="Test Form",
        slug="test-form",
        mode="chat",
        persona="Friendly tester",
        status="published",
    )
    db_session.add(form)
    db_session.flush()

    version = FormVersion(form_id=form.id, version_number=1, status="published")
    db_session.add(version)
    db_session.flush()

    # Create nodes
    node1 = FormGraphNode(
        form_version_id=version.id,
        key="name",
        prompt="What is your name?",
        required=True,
    )
    db_session.add(node1)
    db_session.flush()

    node2 = FormGraphNode(
        form_version_id=version.id,
        key="email",
        prompt="What is your email?",
        required=True,
        validation_json={"regex": r"^[^@\s]+@[^@\s]+$"},
    )
    db_session.add(node2)
    db_session.flush()

    node3 = FormGraphNode(
        form_version_id=version.id,
        key="feedback",
        prompt="Any feedback?",
        required=False,
    )
    db_session.add(node3)
    db_session.flush()

    # Edges: name -> email -> feedback -> end
    db_session.add(FormGraphEdge(form_version_id=version.id, from_node_id=node1.id, to_node_id=node2.id))
    db_session.add(FormGraphEdge(form_version_id=version.id, from_node_id=node2.id, to_node_id=node3.id))
    db_session.add(FormGraphEdge(form_version_id=version.id, from_node_id=node3.id, to_node_id=None))

    version.start_node_id = node1.id
    form.published_version_id = version.id
    db_session.commit()

    return {
        "form": form,
        "version": version,
        "nodes": [node1, node2, node3],
    }


@pytest.fixture
def active_session(db_session, form_with_graph):
    """Create an active respondent session."""
    session = RespondentSession(
        form_id=form_with_graph["form"].id,
        form_version_id=form_with_graph["version"].id,
        channel="chat",
        status="active",
        current_node_id=form_with_graph["nodes"][0].id,
    )
    db_session.add(session)
    db_session.commit()
    return session


def test_start_session_prompt(db_session, active_session):
    prompt = start_session_prompt(db_session, active_session)
    assert "name" in prompt.lower()


def test_process_valid_answer_advances(db_session, active_session, form_with_graph):
    result = process_user_message(db_session, active_session, "John Doe")
    db_session.commit()

    assert result["accepted"] is True
    assert result["state"] == "active"
    assert "email" in result["assistant_message"].lower()
    assert active_session.current_node_id == form_with_graph["nodes"][1].id


def test_process_required_empty_rejected(db_session, active_session):
    result = process_user_message(db_session, active_session, "")
    db_session.commit()

    assert result["accepted"] is False
    assert "required" in result["assistant_message"].lower()


def test_validation_failure(db_session, active_session, form_with_graph):
    # Advance to email node
    process_user_message(db_session, active_session, "John")
    db_session.commit()

    # Send invalid email
    result = process_user_message(db_session, active_session, "not-an-email")
    db_session.commit()

    assert result["accepted"] is False
    assert "format" in result["assistant_message"].lower() or "valid" in result["assistant_message"].lower()


def test_complete_form(db_session, active_session):
    # Answer all three questions
    r1 = process_user_message(db_session, active_session, "John")
    db_session.commit()
    assert r1["accepted"] is True

    r2 = process_user_message(db_session, active_session, "john@test.com")
    db_session.commit()
    assert r2["accepted"] is True

    r3 = process_user_message(db_session, active_session, "Great form!")
    db_session.commit()
    assert r3["accepted"] is True
    assert r3["state"] == "completed"
    assert active_session.status == "completed"


def test_completed_session_rejects_messages(db_session, active_session):
    # Complete the form
    process_user_message(db_session, active_session, "John")
    db_session.commit()
    process_user_message(db_session, active_session, "j@t.com")
    db_session.commit()
    process_user_message(db_session, active_session, "Done")
    db_session.commit()

    # Try to send another message
    result = process_user_message(db_session, active_session, "Hello again")
    assert result["accepted"] is False
    assert "no longer active" in result["assistant_message"].lower()
