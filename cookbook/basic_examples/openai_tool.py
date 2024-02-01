"""An example demonstrating how to use `OpenAITool`s as tools."""
import os
from typing import Literal

from pydantic import Field

from mirascope import OpenAIChat, OpenAITool, Prompt, openai_tool_fn

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class CurrentWeatherPrompt(Prompt):
    """What's the weather like in San Francisco, Tokyo, and Paris?"""


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
) -> str:
    """Returns the current weather in a given location."""
    return f"{location} is 65 degrees {unit}."


@openai_tool_fn(get_current_weather)
class GetCurrentWeather(OpenAITool):
    """Get the current weather in a given location."""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = "fahrenheit"


chat = OpenAIChat(model="gpt-3.5-turbo-1106")
completion = chat.create(
    CurrentWeatherPrompt(),
    tools=[GetCurrentWeather],  # pass in the function itself for automatic conversion
)

if tools := completion.tools:
    for tool in tools:
        if tool.fn:
            print(tool.fn(**tool.__dict__))
        else:
            print("No function found.")