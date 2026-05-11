from app.services import analyze_document, evaluate_prompt, plan_assistant_reply


def test_prompt_evaluation_rewards_specific_context() -> None:
    result = evaluate_prompt(
        "Goal: reduce manual supplier review. Use Oracle Fusion and a REST API. "
        "Return JSON with risks, assumptions, validation steps, and confidence. "
        "The workflow should support finance users, avoid production access, flag missing "
        "supplier fields, and explain any fallback action for incomplete AI output."
    )

    assert result.score >= 80
    assert not result.gaps


def test_document_analysis_extracts_actions_and_risks() -> None:
    result = analyze_document(
        "Supplier intake notes",
        "The supplier record is missing tax fields. Finance needs to validate the "
        "approval route before the ERP update. Manual email follow up caused delay.",
    )

    assert "Oracle Fusion" in result.detected_systems
    assert result.action_items
    assert len(result.risks) >= 2
    assert result.automation_opportunities


def test_assistant_confidence_uses_context_and_systems() -> None:
    result = plan_assistant_reply(
        "We need a proof of concept for Oracle Fusion supplier updates through a REST API. "
        "The goal is to validate missing fields, generate review notes, and document fallback "
        "steps before the workflow is shown to stakeholders.",
        workflow_id="supplier-onboarding",
    )

    assert "Supplier Onboarding" in result.answer
    assert result.confidence == "high"
    assert len(result.suggested_steps) >= 5
