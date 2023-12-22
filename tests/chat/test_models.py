"""Tests for mirascope chat API model classes."""
from unittest.mock import MagicMock, patch

import pytest

from mirascope.chat.models import MirascopeChatOpenAI
from mirascope.chat.types import MirascopeChatCompletion, MirascopeChatCompletionChunk
from mirascope.chat.utils import get_messages


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize("prompt", ["fixture_foobar_prompt", "fixture_messages_prompt"])
def test_mirascope_chat_openai(
    mock_create,
    fixture_chat_completion,
    prompt,
    request,
):
    """Tests that `MirascopeChatOpenAI` returns the expected response when called."""
    prompt = request.getfixturevalue(prompt)
    mock_create.return_value = fixture_chat_completion

    model = "gpt-3.5-turbo-16k"
    chat = MirascopeChatOpenAI(model, api_key="test")
    assert chat.model == model

    completion = chat(prompt, temperature=0.3)
    assert isinstance(completion, MirascopeChatCompletion)

    mock_create.assert_called_once_with(
        model=model,
        messages=get_messages(prompt),
        temperature=0.3,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_mirascope_chat_openai_error(mock_create, fixture_foobar_prompt):
    """Tests that `MirascopeChatOpenAI` handles openai errors thrown during __call__."""
    chat = MirascopeChatOpenAI("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        chat(fixture_foobar_prompt)


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
)
@pytest.mark.parametrize("prompt", ["fixture_foobar_prompt", "fixture_messages_prompt"])
def test_mirascope_chat_openai_stream(
    mock_create,
    fixture_chat_completion_chunk,
    prompt,
    request,
):
    """Tests that `MirascopeChatOpenAI` returns the expected response when streaming."""
    prompt = request.getfixturevalue(prompt)
    mock_create.return_value = [fixture_chat_completion_chunk] * 3

    model = "gpt-3.5-turbo-16k"
    chat = MirascopeChatOpenAI(model, api_key="test")
    stream = chat.stream(prompt, temperature=0.3)

    for chunk in stream:
        assert isinstance(chunk, MirascopeChatCompletionChunk)
        assert chunk.chunk == fixture_chat_completion_chunk
        for i, choice in enumerate(chunk.choices):
            assert choice == fixture_chat_completion_chunk.choices[i]

    mock_create.assert_called_once_with(
        model=model,
        messages=get_messages(prompt),
        temperature=0.3,
        stream=True,
    )


@patch(
    "openai.resources.chat.completions.Completions.create",
    new_callable=MagicMock,
    side_effect=Exception("base exception"),
)
def test_mirascope_chat_openai_stream_error(mock_create, fixture_foobar_prompt):
    """Tests that `MirascopeChatOpenAI` handles openai errors thrown during stream."""
    chat = MirascopeChatOpenAI("gpt-3.5-turbo", api_key="test")
    with pytest.raises(Exception):
        stream = chat.stream(fixture_foobar_prompt)
        for chunk in stream:
            pass