from typing import Type, Literal
from loguru import logger

from .agents.agent_interface import AgentInterface
from .agents.basic_memory_agent import BasicMemoryAgent
from .agents.dual_model_agent import DualModelAgent
from .stateless_llm_factory import LLMFactory as StatelessLLMFactory
from .agents.hume_ai import HumeAIAgent
from .agents.letta_agent import LettaAgent

from ..mcpp.tool_manager import ToolManager
from ..mcpp.tool_executor import ToolExecutor
from typing import Optional


class AgentFactory:
    @staticmethod
    def create_agent(
        conversation_agent_choice: str,
        agent_settings: dict,
        llm_configs: dict,
        system_prompt: str,
        live2d_model=None,
        tts_preprocessor_config=None,
        **kwargs,
    ) -> Type[AgentInterface]:
        """Create an agent based on the configuration.

        Args:
            conversation_agent_choice: The type of agent to create
            agent_settings: Settings for different types of agents
            llm_configs: Pool of LLM configurations
            system_prompt: The system prompt to use
            live2d_model: Live2D model instance for expression extraction
            tts_preprocessor_config: Configuration for TTS preprocessing
            **kwargs: Additional arguments
        """
        logger.info(f"Initializing agent: {conversation_agent_choice}")

        if conversation_agent_choice == "basic_memory_agent":
            # Get the LLM provider choice from agent settings
            basic_memory_settings: dict = agent_settings.get("basic_memory_agent", {})
            llm_provider: str = basic_memory_settings.get("llm_provider")

            if not llm_provider:
                raise ValueError("LLM provider not specified for basic memory agent")

            # Get the LLM config for this provider
            llm_config: dict = llm_configs.get(llm_provider)
            interrupt_method: Literal["system", "user"] = llm_config.pop(
                "interrupt_method", "user"
            )

            if not llm_config:
                raise ValueError(
                    f"Configuration not found for LLM provider: {llm_provider}"
                )

            # 检查是否启用流式API
            if basic_memory_settings.get("enable_streaming", False) and llm_provider == "openai_llm":
                logger.info("🚀 启用流式OpenAI LLM")
                from .stateless_llm.streaming_openai_llm import StreamingOpenAILLM
                
                # 创建流式LLM
                llm = StreamingOpenAILLM(
                    model=llm_config.get("model", "gpt-3.5-turbo"),
                    base_url=llm_config.get("base_url", "https://api.openai.com/v1"),
                    llm_api_key=llm_config.get("llm_api_key", ""),
                    temperature=llm_config.get("temperature", 0.6),
                    max_tokens=llm_config.get("max_tokens", 500),
                    timeout=llm_config.get("timeout", 10),
                    retry_count=llm_config.get("retry_count", 1),
                    # 流式配置
                    stream=llm_config.get("stream", True),
                    stream_chunk_size=llm_config.get("stream_chunk_size", 8),
                    stream_buffer_size=llm_config.get("stream_buffer_size", 3),
                    first_response_timeout=llm_config.get("first_response_timeout", 200),
                    enable_streaming_tts=llm_config.get("enable_streaming_tts", True),
                    tts_stream_delay=llm_config.get("tts_stream_delay", 50),
                    # 流式优化
                    streaming_optimization=llm_config.get("streaming_optimization", True),
                    chunk_processing_parallel=llm_config.get("chunk_processing_parallel", True),
                    immediate_audio_playback=llm_config.get("immediate_audio_playback", True),
                    # 性能优化
                    max_wait_time=llm_config.get("max_wait_time", 3),
                    connection_pool_size=llm_config.get("connection_pool_size", 5),
                    keep_alive=llm_config.get("keep_alive", True),
                )
            else:
                # 使用标准LLM
                llm = StatelessLLMFactory.create_llm(
                    llm_provider=llm_provider, system_prompt=system_prompt, **llm_config
                )

            tool_prompts = kwargs.get("system_config", {}).get("tool_prompts", {})

            # Extract MCP components/data needed by BasicMemoryAgent from kwargs
            tool_manager: Optional[ToolManager] = kwargs.get("tool_manager")
            tool_executor: Optional[ToolExecutor] = kwargs.get("tool_executor")
            mcp_prompt_string: str = kwargs.get("mcp_prompt_string", "")

            # Create the agent with the LLM and live2d_model
            return BasicMemoryAgent(
                llm=llm,
                system=system_prompt,
                live2d_model=live2d_model,
                tts_preprocessor_config=tts_preprocessor_config,
                faster_first_response=basic_memory_settings.get(
                    "faster_first_response", True
                ),
                segment_method=basic_memory_settings.get("segment_method", "pysbd"),
                use_mcpp=basic_memory_settings.get("use_mcpp", False),
                interrupt_method=interrupt_method,
                tool_prompts=tool_prompts,
                tool_manager=tool_manager,
                tool_executor=tool_executor,
                mcp_prompt_string=mcp_prompt_string,
            )

        elif conversation_agent_choice == "mem0_agent":
            from .agents.mem0_llm import LLM as Mem0LLM

            mem0_settings = agent_settings.get("mem0_agent", {})
            if not mem0_settings:
                raise ValueError("Mem0 agent settings not found")

            # Validate required settings
            required_fields = ["base_url", "model", "mem0_config"]
            for field in required_fields:
                if field not in mem0_settings:
                    raise ValueError(
                        f"Missing required field '{field}' in mem0_agent settings"
                    )

            return Mem0LLM(
                user_id=kwargs.get("user_id", "default"),
                system=system_prompt,
                live2d_model=live2d_model,
                **mem0_settings,
            )

        elif conversation_agent_choice == "hume_ai_agent":
            settings = agent_settings.get("hume_ai_agent", {})
            return HumeAIAgent(
                api_key=settings.get("api_key"),
                host=settings.get("host", "api.hume.ai"),
                config_id=settings.get("config_id"),
                idle_timeout=settings.get("idle_timeout", 15),
            )

        elif conversation_agent_choice == "dual_model_agent":
            # Get the dual model settings
            dual_model_settings: dict = agent_settings.get("dual_model_agent", {})
            primary_llm_provider: str = dual_model_settings.get("primary_llm_provider")
            fallback_llm_provider: str = dual_model_settings.get("fallback_llm_provider")
            
            if not primary_llm_provider or not fallback_llm_provider:
                raise ValueError("Both primary_llm_provider and fallback_llm_provider must be specified for dual model agent")

            # Get the LLM configs for both providers
            primary_llm_config: dict = llm_configs.get(primary_llm_provider)
            fallback_llm_config: dict = llm_configs.get(fallback_llm_provider)
            
            if not primary_llm_config:
                raise ValueError(f"Configuration not found for primary LLM provider: {primary_llm_provider}")
            if not fallback_llm_config:
                raise ValueError(f"Configuration not found for fallback LLM provider: {fallback_llm_provider}")

            # Create both LLMs
            primary_llm = StatelessLLMFactory.create_llm(
                llm_provider=primary_llm_provider, system_prompt=system_prompt, **primary_llm_config
            )
            fallback_llm = StatelessLLMFactory.create_llm(
                llm_provider=fallback_llm_provider, system_prompt=system_prompt, **fallback_llm_config
            )

            tool_prompts = kwargs.get("system_config", {}).get("tool_prompts", {})
            tool_manager: Optional[ToolManager] = kwargs.get("tool_manager")
            tool_executor: Optional[ToolExecutor] = kwargs.get("tool_executor")
            mcp_prompt_string: str = kwargs.get("mcp_prompt_string", "")

            # Create the dual model agent
            return DualModelAgent(
                primary_llm=primary_llm,
                fallback_llm=fallback_llm,
                system=system_prompt,
                live2d_model=live2d_model,
                tts_preprocessor_config=tts_preprocessor_config,
                faster_first_response=dual_model_settings.get("faster_first_response", True),
                segment_method=dual_model_settings.get("segment_method", "pysbd"),
                use_mcpp=dual_model_settings.get("use_mcpp", False),
                interrupt_method=dual_model_settings.get("interrupt_method", "user"),
                tool_prompts=tool_prompts,
                tool_manager=tool_manager,
                tool_executor=tool_executor,
                mcp_prompt_string=mcp_prompt_string,
                quality_threshold=dual_model_settings.get("quality_threshold", 0.4),
                enable_fallback=dual_model_settings.get("enable_fallback", True),
            )

        elif conversation_agent_choice == "letta_agent":
            settings = agent_settings.get("letta_agent", {})
            return LettaAgent(
                live2d_model=live2d_model,
                id=settings.get("id"),
                tts_preprocessor_config=tts_preprocessor_config,
                faster_first_response=settings.get("faster_first_response"),
                segment_method=settings.get("segment_method"),
                host=settings.get("host"),
                port=settings.get("port"),
            )

        else:
            raise ValueError(f"Unsupported agent type: {conversation_agent_choice}")
