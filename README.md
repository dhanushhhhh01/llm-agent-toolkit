# 🧠 LLM Agent Toolkit

> Modular Python framework for building LLM-powered agents with tool use, RAG, memory, and multi-provider support. Designed for industrial & IIoT applications.
>
> [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
> [![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge)](https://langchain.com)
> [![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
> [![Claude](https://img.shields.io/badge/Claude-D97757?style=for-the-badge)](https://anthropic.com)
> [![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge)](https://ollama.ai)
>
> ---
>
> ## 🏗️ Architecture
>
> ```
> llm-agent-toolkit/
> ├── agents/
> │   ├── base_agent.py          # Abstract base class
> │   ├── rag_agent.py           # RAG-enabled agent
> │   └── tool_agent.py          # Tool-use agent
> ├── providers/
> │   ├── openai_provider.py     # OpenAI GPT integration
> │   ├── claude_provider.py     # Anthropic Claude integration
> │   └── ollama_provider.py     # Local Ollama integration
> ├── tools/
> │   ├── web_search.py          # DuckDuckGo/Tavily search
> │   ├── mqtt_reader.py         # IIoT MQTT data reader
> │   └── database_query.py      # SQL/InfluxDB query tool
> ├── memory/
> │   └── conversation_memory.py # Chat history management
> ├── rag/
> │   └── vector_store.py        # ChromaDB vector store
> ├── examples/
> │   ├── equipment_qa_bot.py    # IIoT equipment Q&A bot
> │   └── anomaly_explainer.py   # ML anomaly explanation agent
> ├── requirements.txt
> └── docker-compose.yml
> ```
>
> ---
>
> ## ⚡ Quick Start
>
> ```bash
> git clone https://github.com/dhanushhhhh01/llm-agent-toolkit.git
> cd llm-agent-toolkit
> pip install -r requirements.txt
> cp .env.example .env
> ```
>
> ### Basic Usage
>
> ```python
> from providers.claude_provider import create_claude_agent
> from tools.mqtt_reader import MQTTReaderTool
>
> # Create agent
> agent = create_claude_agent(
>     model="claude-sonnet-4-5",
>     system_prompt="You are an IIoT expert analyst.",
>     verbose=True
> )
>
> # Register MQTT tool
> mqtt_tool = MQTTReaderTool(broker_url="localhost")
> mqtt_tool.connect()
> mqtt_tool.subscribe("sensors/#")
>
> agent.register_tool(
>     name="read_sensor",
>     func=mqtt_tool.get_latest,
>     description="Read latest value from an MQTT sensor topic",
>     schema=MQTTReaderTool.get_tool_schema()
> )
>
> # Chat with tool use
> response = agent.chat(
>     "What is the current temperature reading from sensors/temperature/motor_01?"
> )
> print(response)
> ```
>
> ---
>
> ## 🔌 Supported Providers
>
> | Provider | Models | Tool Use | Streaming |
> |----------|--------|----------|-----------|
> | OpenAI | GPT-4o, GPT-4o-mini | ✅ | ✅ |
> | Anthropic Claude | claude-sonnet-4-5, claude-haiku | ✅ | ✅ |
> | Ollama (Local) | llama3, mistral, codellama | ✅ | ✅ |
>
> ---
>
> ## 🛠️ Available Tools
>
> | Tool | Description | Use Case |
> |------|-------------|----------|
> | `mqtt_reader.py` | Read from MQTT topics | IIoT sensor data |
> | `database_query.py` | Query SQL/InfluxDB | Historical analytics |
> | `web_search.py` | Web search via Tavily | Research & lookups |
>
> ---
>
> ## 💡 Example: Equipment QA Bot
>
> ```python
> from examples.equipment_qa_bot import EquipmentQABot
>
> bot = EquipmentQABot(
>     mqtt_broker="localhost",
>     topics=["factory/+/temperature", "factory/+/vibration"]
> )
> bot.start()
> answer = bot.ask("Is motor M-01 running above normal temperature?")
> ```
>
> ---
>
> ## 📬 Author
>
> **Dhanush Ramesh Babu** | [LinkedIn](https://linkedin.com/in/dhanushrameshbabu16) | MSc. Industry 4.0 @ SRH Berlin | 🟢 Open to Werkstudent/Internship
