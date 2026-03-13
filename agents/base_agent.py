"""
Base Agent - Abstract base class for all LLM agents.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
      role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
      model: str = "gpt-4o-mini"
      provider: str = "openai"  # openai | claude | ollama
    temperature: float = 0.1
    max_tokens: int = 2048
    max_iterations: int = 10
    system_prompt: str = "You are a helpful AI assistant."
    memory_enabled: bool = True
    verbose: bool = False


class BaseAgent(ABC):
      """
          Abstract base class for all agents in the LLM Agent Toolkit.

                  Provides common interface for: chat, tool use, memory management.
                      """

    def __init__(self, config: AgentConfig):
              self.config = config
              self.conversation_history: List[AgentMessage] = []
              self.tools: Dict[str, Any] = {}
              self._iteration_count = 0
              self._total_tokens = 0

        if config.system_prompt:
                      self.conversation_history.append(
                                        AgentMessage(role="system", content=config.system_prompt)
                      )
                  logger.info(f"Initialized {self.__class__.__name__} with model={config.model}")

    @abstractmethod
    def _call_llm(self, messages: List[AgentMessage]) -> AgentMessage:
              """Call the LLM provider and return response message."""
              pass

    def register_tool(self, name: str, func: Any, description: str, schema: Dict):
              """Register a callable tool that the agent can use."""
              self.tools[name] = {
                  "function": func,
                  "description": description,
                  "schema": schema
              }
              logger.debug(f"Registered tool: {name}")

    def chat(self, user_message: str) -> str:
              """Send a message and get a response."""
              self.conversation_history.append(
                  AgentMessage(role="user", content=user_message)
              )
              response = self._run_agent_loop()
              return response.content

    def _run_agent_loop(self) -> AgentMessage:
              """Main agent loop — handles tool calls iteratively."""
              self._iteration_count = 0

        while self._iteration_count < self.config.max_iterations:
                      self._iteration_count += 1

            if self.config.verbose:
                              logger.info(f"Agent iteration {self._iteration_count}")

            response = self._call_llm(self.conversation_history)
            self.conversation_history.append(response)

            # If no tool calls, return final response
            if not response.tool_calls:
                              return response

            # Execute tool calls
            for tool_call in response.tool_calls:
                              tool_result = self._execute_tool(tool_call)
                              self.conversation_history.append(tool_result)

        logger.warning(f"Max iterations ({self.config.max_iterations}) reached")
        return self.conversation_history[-1]

    def _execute_tool(self, tool_call: Dict) -> AgentMessage:
              """Execute a tool call and return the result."""
              tool_name = tool_call.get("function", {}).get("name")
              tool_args = tool_call.get("function", {}).get("arguments", {})

        if isinstance(tool_args, str):
                      import json
                      tool_args = json.loads(tool_args)

        if tool_name not in self.tools:
                      return AgentMessage(
                                        role="tool",
                                        content=f"Error: Tool '{tool_name}' not found",
                                        tool_call_id=tool_call.get("id")
                      )

        try:
                      start_time = time.time()
                      result = self.tools[tool_name]["function"](**tool_args)
                      elapsed = time.time() - start_time
                      logger.debug(f"Tool {tool_name} executed in {elapsed:.2f}s")
                      return AgentMessage(
                          role="tool",
                          content=str(result),
                          tool_call_id=tool_call.get("id")
                      )
except Exception as e:
              logger.error(f"Tool {tool_name} failed: {e}")
              return AgentMessage(
                  role="tool",
                  content=f"Error executing {tool_name}: {str(e)}",
                  tool_call_id=tool_call.get("id")
              )

    def reset(self):
              """Reset conversation history."""
              self.conversation_history = []
              if self.config.system_prompt:
                            self.conversation_history.append(
                                              AgentMessage(role="system", content=self.config.system_prompt)
                            )
                        self._iteration_count = 0

    def get_stats(self) -> Dict:
              """Return agent usage statistics."""
        return {
                      "iterations": self._iteration_count,
                      "total_messages": len(self.conversation_history),
                      "tools_registered": len(self.tools),
                      "model": self.config.model
        }
