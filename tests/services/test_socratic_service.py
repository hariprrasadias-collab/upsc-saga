import pytest
from unittest.mock import MagicMock
import json
import time

from app.services.socratic_service import generate_debate_turn, AGENTS

# Helper to create mock responses
class MockResponse:
    def __init__(self, text):
        self.text = text

@pytest.fixture
def mock_model_manager(mocker):
    # Patch the model_manager instance directly
    return mocker.patch('app.services.socratic_service.model_manager')

def test_generate_debate_turn_happy_path(mock_model_manager):
    # Setup mock responses
    moderator_json = json.dumps({
        "next_speaker_id": "skeptic",
        "strategy": "Question the definition of justice."
    })

    agent_json = json.dumps({
        "thought_process": "Ah, they rely on a weak premise.",
        "rhetorical_technique": "Socratic Irony",
        "detected_fallacies_in_prev_turn": ["Strawman"],
        "text": "But what is justice, really?",
        "type": "QUESTION"
    })

    # model_manager.generate_content is called twice: once for moderator, once for agent
    mock_model_manager.generate_content.side_effect = [
        MockResponse(moderator_json),
        MockResponse(agent_json)
    ]

    topic = "Justice"
    history = [{"speakerId": "idealist", "text": "Justice is the harmony of the soul."}]

    result = generate_debate_turn(topic, history)

    assert result['speakerId'] == "skeptic"
    assert result['text'] == "But what is justice, really?"
    assert result['type'] == "QUESTION"
    assert result['thoughts'] == "Ah, they rely on a weak premise."
    assert result['technique'] == "Socratic Irony"
    assert result['fallacies'] == ["Strawman"]
    assert 'timestamp' in result

def test_generate_debate_turn_moderator_json_failure(mock_model_manager):
    # Moderator returns invalid JSON
    moderator_text = "I think the skeptic should speak next and use Socratic Irony."

    agent_json = json.dumps({
        "text": "I will proceed with the default strategy.",
        "type": "ARGUMENT"
    })

    mock_model_manager.generate_content.side_effect = [
        MockResponse(moderator_text),
        MockResponse(agent_json)
    ]

    topic = "Ethics"
    history = []

    result = generate_debate_turn(topic, history)

    # Due to random choice on failure, we just verify it picks a valid agent
    assert result['speakerId'] in AGENTS
    assert result['text'] == "I will proceed with the default strategy."
    assert result['type'] == "ARGUMENT"

def test_generate_debate_turn_agent_json_failure(mock_model_manager):
    moderator_json = json.dumps({"next_speaker_id": "realist"})

    # Agent returns raw text, no JSON
    agent_text = "This is a direct assertion without JSON formatting."

    mock_model_manager.generate_content.side_effect = [
        MockResponse(moderator_json),
        MockResponse(agent_text)
    ]

    result = generate_debate_turn("Reality", [])

    assert result['speakerId'] == "realist"
    assert result['text'] == agent_text
    assert result['type'] == "ARGUMENT"
    assert result['thoughts'] in ["Decode Error", "Raw Output"]
    assert result['technique'] == "Direct Assertion"

def test_generate_debate_turn_oracle_is_silent(mock_model_manager):
    moderator_json = json.dumps({"next_speaker_id": "sage"})
    agent_text = "The Oracle is silent."

    mock_model_manager.generate_content.side_effect = [
        MockResponse(moderator_json),
        MockResponse(agent_text)
    ]

    result = generate_debate_turn("Wisdom", [])

    assert result['speakerId'] == "sage"
    assert "(The philosopher is silent" in result['text']
    assert result['type'] == "error"
    assert result['technique'] == "Silence"

def test_generate_debate_turn_moderator_api_exception(mock_model_manager):
    # Moderator raises an exception
    mock_model_manager.generate_content.side_effect = [
        Exception("API Timeout"),
        MockResponse(json.dumps({"text": "I recovered.", "type": "ARGUMENT"}))
    ]

    result = generate_debate_turn("Resilience", [])

    # Should fall back to a random agent and continue
    assert result['speakerId'] in AGENTS
    assert result['text'] == "I recovered."
    assert result['type'] == "ARGUMENT"

def test_generate_debate_turn_agent_api_exception(mock_model_manager):
    moderator_json = json.dumps({"next_speaker_id": "strategist"})

    # First call succeeds (moderator), second fails (agent)
    mock_model_manager.generate_content.side_effect = [
        MockResponse(moderator_json),
        Exception("Agent API Timeout")
    ]

    result = generate_debate_turn("Power", [])

    assert result['speakerId'] == "strategist"
    assert "Error: Agent API Timeout" in result['text']
    assert result['type'] == "error"
    assert result['technique'] == "System Failure"
