"""
Claude Provider - Anthropic Claude API integration for the LLM Agent Toolkit.
"""
from typing import List, Dict, Optional
import anthropic
import json
import logging

from agents.base_agent import BaseAgent, AgentConfig, AgentMessage

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAgent):
    """
    Agent implementation using Anthropic's Claude API.

    Supports: tool use, streaming, vision (claude-3+ models).
    """

    SUPPORTED_MODELS = [
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-haiku-3-5",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ]

    def __init__(self, config: AgentConfig, api_key: Optional[str] = None):
        super().__init__(config)
        import os
        self.client = anthropic.Anthropic(
                                                      api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
                                                  )
        logger.info(f"ClaudeProvider initialized: {config.model}")

    def _call_llm(self, messages: List[AgentMessage]) -> AgentMessage:
        """Convert messages to Claude format and call API."""
        system_prompt = ""
        claude_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            elif msg.role in ("user", "assistant"):
                claude_messages.append({
                                                           "role": msg.role,
                                                           "content": msg.content
                                                       })
            elif msg.role == "tool":
                # Tool results in Claude format
                claude_messages.append({
                                                           "role": "user",
                                                           "content": [{
                                                               "type": "tool_result",
                                                               "tool_use_id": msg.tool_call_id,
                                                               "content": msg.content
                                                           }]
                })

        # Build tools list for Claude
        tools = self._build_claude_tools()

        kwargs = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": claude_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        # Parse response
        tool_calls = []
        content_text = ""

        for block in response.content:
            if block.type == "text":
                content_text = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                                                      "id": block.id,
                                                      "function": {
                                                          "name": block.name,
                                                          "arguments": block.input
                                                      }
                                                  })

        return AgentMessage(
                                        role="assistant",
                                        content=content_text,
                                        tool_calls=tool_calls if tool_calls else None,
                                        metadata={"usage": response.usage.model_dump()}
                                    )

    def _build_claude_tools(self) -> List[Dict]:
        """Convert registered tools to Claude tool format."""
        if not self.tools:
            return []

        claude_tools = []
        for name, tool_info in self.tools.items():
            claude_tools.append({
                                                "name": name,
                                                "description": tool_info["description"],
                "input_schema": tool_info["schema"]
            })
        return claude_tools


def create_claude_agent(
                            model: str = "claude-sonnet-4-5",
                            system_prompt: str = "You are a helpful assistant.",
                            tools: Optional[Dict] = None,
    **kwargs
) -> ClaudeProvider:
    """Factory function to quickly create a Claude agent."""
    config = AgentConfig(
                                 model=model,
                                 provider="claude",
                                 system_prompt=system_prompt,
                                 **kwargs
                             )
    agent = ClaudeProvider(config)
    if tools:
        for name, tool_data in tools.items():
            agent.register_tool(
                                                name=name,
                                                func=tool_data["function"],
                description=tool_data["description"],
                schema=tool_data["schema"]
            )
    return agent
