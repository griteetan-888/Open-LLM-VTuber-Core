from typing import (
    AsyncIterator,
    List,
    Dict,
    Any,
    Callable,
    Literal,
    Union,
    Optional,
)
import re
import asyncio
from loguru import logger
from .agent_interface import AgentInterface
from ..output_types import SentenceOutput, DisplayText
from ..stateless_llm.stateless_llm_interface import StatelessLLMInterface
from ..stateless_llm.claude_llm import AsyncLLM as ClaudeAsyncLLM
from ..stateless_llm.openai_compatible_llm import AsyncLLM as OpenAICompatibleAsyncLLM
from ...chat_history_manager import get_history
from ..transformers import (
    sentence_divider,
    actions_extractor,
    tts_filter,
    display_processor,
)
from ...config_manager import TTSPreprocessorConfig
from ..input_types import BatchInput, TextSource
from prompts import prompt_loader
from ...mcpp.tool_manager import ToolManager
from ...mcpp.json_detector import StreamJSONDetector
from ...mcpp.types import ToolCallObject
from ...mcpp.tool_executor import ToolExecutor


class ResponseQualityChecker:
    """检查响应质量的类"""
    
    def __init__(self, character_prompt: str, min_length: int = 5, max_length: int = 800):
        self.character_prompt = character_prompt
        self.min_length = min_length
        self.max_length = max_length
        
        # 从角色提示中提取关键特征
        self.character_keywords = self._extract_character_keywords()
        self.personality_traits = self._extract_personality_traits()
    
    def _extract_character_keywords(self) -> List[str]:
        """从角色提示中提取关键词"""
        keywords = []
        
        # 提取角色名称
        name_match = re.search(r'You are \*\*(\w+)\*\*', self.character_prompt)
        if name_match:
            keywords.append(name_match.group(1).lower())
        
        # 提取其他关键词
        keyword_patterns = [
            r'(\w+)\s+and\s+(\w+)',  # "sassy and witty"
            r'(\w+)\s+but\s+(\w+)',  # "wise but naive"
            r'(\w+)\s+with\s+(\w+)', # "playful with care"
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, self.character_prompt.lower())
            for match in matches:
                keywords.extend(match)
        
        # 添加Kiyo特有的角色相关词汇
        keywords.extend(['babe', 'sweetie', 'darling', 'princess', 'alien', 'nota', 'sparkle', 'glitter', 'royal', 'tsundere'])
        
        return list(set(keywords))
    
    def _extract_personality_traits(self) -> List[str]:
        """提取性格特征"""
        traits = []
        
        # 常见的性格特征
        trait_patterns = [
            r'sassy', r'witty', r'tsundere', r'curious', r'wise', r'naive',
            r'playful', r'supportive', r'royal', r'alien', r'princess'
        ]
        
        for pattern in trait_patterns:
            if re.search(pattern, self.character_prompt.lower()):
                traits.append(pattern)
        
        return traits
    
    def check_response_quality(self, response: str) -> Dict[str, Any]:
        """检查响应质量"""
        if not response or not response.strip():
            return {
                'is_good': False,
                'reason': 'empty_response',
                'score': 0.0
            }
        
        response_lower = response.lower().strip()
        
        # 检查长度
        if len(response_lower) < self.min_length:
            return {
                'is_good': False,
                'reason': 'too_short',
                'score': 0.2
            }
        
        if len(response_lower) > self.max_length:
            return {
                'is_good': False,
                'reason': 'too_long',
                'score': 0.3
            }
        
        # 检查是否包含角色关键词
        keyword_score = 0.0
        for keyword in self.character_keywords:
            if keyword in response_lower:
                keyword_score += 0.15  # 降低关键词权重，更宽松
        
        # 检查是否包含性格特征
        trait_score = 0.0
        for trait in self.personality_traits:
            if trait in response_lower:
                trait_score += 0.2  # 降低特征权重，更宽松
        
        # 检查是否过于通用
        generic_phrases = [
            'i understand', 'that\'s interesting', 'i see', 'okay',
            'sure', 'yes', 'no', 'maybe', 'i think', 'i believe'
        ]
        
        generic_score = 0.0
        for phrase in generic_phrases:
            if phrase in response_lower:
                generic_score += 0.1
        
        # 计算总分 - 更宽松的评分标准
        total_score = min(1.0, keyword_score + trait_score - generic_score * 0.3)
        
        # 检查是否包含情感表达
        emotion_indicators = ['!', '?', '...', 'haha', 'lol', 'omg', 'wow', '[', ']']
        emotion_score = sum(0.05 for indicator in emotion_indicators if indicator in response_lower)
        total_score += emotion_score
        
        # 降低质量阈值，让更多响应通过
        is_good = total_score >= 0.2
        
        return {
            'is_good': is_good,
            'reason': 'quality_check' if is_good else 'low_quality',
            'score': total_score,
            'details': {
                'keyword_score': keyword_score,
                'trait_score': trait_score,
                'generic_score': generic_score,
                'emotion_score': emotion_score
            }
        }


class DualModelAgent(AgentInterface):
    """支持双模型回退的Agent：小模型快速响应，大模型高质量补全"""

    _system: str = "You are a helpful assistant."

    def __init__(
        self,
        primary_llm: StatelessLLMInterface,  # 小模型 (如Ollama)
        fallback_llm: StatelessLLMInterface,  # 大模型 (如OpenAI)
        system: str,
        live2d_model,
        tts_preprocessor_config: TTSPreprocessorConfig = None,
        faster_first_response: bool = True,
        segment_method: str = "pysbd",
        use_mcpp: bool = False,
        interrupt_method: Literal["system", "user"] = "user",
        tool_prompts: Dict[str, str] = None,
        tool_manager: Optional[ToolManager] = None,
        tool_executor: Optional[ToolExecutor] = None,
        mcp_prompt_string: str = "",
        quality_threshold: float = 0.2,  # 质量阈值 - 更宽松
        enable_fallback: bool = True,  # 是否启用回退
    ):
        """Initialize dual model agent with primary and fallback LLMs."""
        super().__init__()
        self._memory = []
        self._live2d_model = live2d_model
        self._tts_preprocessor_config = tts_preprocessor_config
        self._faster_first_response = faster_first_response
        self._segment_method = segment_method
        self._use_mcpp = use_mcpp
        self.interrupt_method = interrupt_method
        self._tool_prompts = tool_prompts or {}
        self._interrupt_handled = False
        self.prompt_mode_flag = False
        self.quality_threshold = quality_threshold
        self.enable_fallback = enable_fallback

        # 双模型设置
        self._primary_llm = primary_llm
        self._fallback_llm = fallback_llm
        
        # 质量检查器
        self._quality_checker = ResponseQualityChecker(system)

        self._tool_manager = tool_manager
        self._tool_executor = tool_executor
        self._mcp_prompt_string = mcp_prompt_string
        self._json_detector = StreamJSONDetector()

        self._formatted_tools_openai = []
        self._formatted_tools_claude = []
        if self._tool_manager:
            self._formatted_tools_openai = self._tool_manager.get_formatted_tools("OpenAI")
            self._formatted_tools_claude = self._tool_manager.get_formatted_tools("Claude")
            logger.debug(
                f"DualModelAgent received pre-formatted tools - OpenAI: {len(self._formatted_tools_openai)}, Claude: {len(self._formatted_tools_claude)}"
            )

        self._set_llm(primary_llm)  # 默认使用主模型
        self.set_system(system if system else self._system)

        logger.info("DualModelAgent initialized with primary and fallback LLMs.")

    def _set_llm(self, llm: StatelessLLMInterface):
        """Set the current LLM for chat completion."""
        self._llm = llm
        self.chat = self._chat_function_factory()

    def set_system(self, system: str):
        """Set the system prompt."""
        logger.debug(f"DualModelAgent: Setting system prompt: '''{system}'''")

        if self.interrupt_method == "user":
            system = f"{system}\n\nIf you received `[interrupted by user]` signal, you were interrupted."

        self._system = system
        # 更新质量检查器
        self._quality_checker = ResponseQualityChecker(system)

    def _add_message(
        self,
        message: Union[str, List[Dict[str, Any]]],
        role: str,
        display_text: DisplayText | None = None,
        skip_memory: bool = False,
    ):
        """Add message to memory."""
        if skip_memory:
            return

        text_content = ""
        if isinstance(message, list):
            for item in message:
                if item.get("type") == "text":
                    text_content += item["text"] + " "
            text_content = text_content.strip()
        elif isinstance(message, str):
            text_content = message
        else:
            logger.warning(
                f"_add_message received unexpected message type: {type(message)}"
            )
            text_content = str(message)

        if not text_content and role == "assistant":
            return

        message_data = {
            "role": role,
            "content": text_content,
        }

        if display_text:
            if display_text.name:
                message_data["name"] = display_text.name
            if display_text.avatar:
                message_data["avatar"] = display_text.avatar

        if (
            self._memory
            and self._memory[-1]["role"] == role
            and self._memory[-1]["content"] == text_content
        ):
            return

        self._memory.append(message_data)

    def set_memory_from_history(self, conf_uid: str, history_uid: str) -> None:
        """Load memory from chat history."""
        messages = get_history(conf_uid, history_uid)

        self._memory = []
        for msg in messages:
            role = "user" if msg["role"] == "human" else "assistant"
            content = msg["content"]
            if isinstance(content, str) and content:
                self._memory.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )
            else:
                logger.warning(f"Skipping invalid message from history: {msg}")
        logger.info(f"Loaded {len(self._memory)} messages from history.")

    def handle_interrupt(self, heard_response: str) -> None:
        """Handle user interruption."""
        if self._interrupt_handled:
            return

        self._interrupt_handled = True

        if self._memory and self._memory[-1]["role"] == "assistant":
            if not self._memory[-1]["content"].endswith("..."):
                self._memory[-1]["content"] = heard_response + "..."
            else:
                self._memory[-1]["content"] = heard_response + "..."
        else:
            if heard_response:
                self._memory.append(
                    {
                        "role": "assistant",
                        "content": heard_response + "...",
                    }
                )

        interrupt_role = "system" if self.interrupt_method == "system" else "user"
        self._memory.append(
            {
                "role": interrupt_role,
                "content": "[Interrupted by user]",
            }
        )
        logger.info(f"Handled interrupt with role '{interrupt_role}'.")

    def _to_text_prompt(self, input_data: BatchInput) -> str:
        """Format input data to text prompt."""
        message_parts = []

        for text_data in input_data.texts:
            if text_data.source == TextSource.INPUT:
                message_parts.append(text_data.content)
            elif text_data.source == TextSource.CLIPBOARD:
                message_parts.append(
                    f"[User shared content from clipboard: {text_data.content}]"
                )

        if input_data.images:
            message_parts.append("\n[User has also provided images]")

        return "\n".join(message_parts).strip()

    def _to_messages(self, input_data: BatchInput) -> List[Dict[str, Any]]:
        """Prepare messages for LLM API call."""
        messages = self._memory.copy()
        user_content = []
        text_prompt = self._to_text_prompt(input_data)
        if text_prompt:
            user_content.append({"type": "text", "text": text_prompt})

        if input_data.images:
            image_added = False
            for img_data in input_data.images:
                if isinstance(img_data.data, str) and img_data.data.startswith(
                    "data:image"
                ):
                    user_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": img_data.data, "detail": "auto"},
                        }
                    )
                    image_added = True
                else:
                    logger.error(
                        f"Invalid image data format: {type(img_data.data)}. Skipping image."
                    )

            if not image_added and not text_prompt:
                logger.warning(
                    "User input contains images but none could be processed."
                )

        if user_content:
            user_message = {"role": "user", "content": user_content}
            messages.append(user_message)

            skip_memory = False
            if input_data.metadata and input_data.metadata.get("skip_memory", False):
                skip_memory = True

            if not skip_memory:
                self._add_message(
                    text_prompt if text_prompt else "[User provided image(s)]", "user"
                )
        else:
            logger.warning("No content generated for user message.")

        return messages

    async def _generate_with_fallback(
        self, 
        messages: List[Dict[str, Any]], 
        system: str
    ) -> AsyncIterator[str]:
        """使用双模型生成响应，支持回退机制"""
        
        # 首先尝试主模型（小模型）
        logger.info("🔄 Trying primary LLM (small model) first...")
        primary_response = ""
        
        try:
            token_stream = self._primary_llm.chat_completion(messages, system)
            async for event in token_stream:
                if isinstance(event, dict) and event.get("type") == "text_delta":
                    text_chunk = event.get("text", "")
                elif isinstance(event, str):
                    text_chunk = event
                else:
                    continue
                if text_chunk:
                    primary_response += text_chunk
                    yield text_chunk
            
            # 检查主模型响应质量
            if self.enable_fallback and primary_response.strip():
                quality_result = self._quality_checker.check_response_quality(primary_response)
                logger.info(f"📊 Primary model quality score: {quality_result['score']:.2f}")
                
                if not quality_result['is_good']:
                    logger.warning(f"⚠️ Primary model response quality low: {quality_result['reason']}")
                    logger.info("🔄 Falling back to OpenAI for better response...")
                    
                    # 使用大模型重新生成
                    try:
                        fallback_response = await self._generate_with_openai(messages, system, primary_response)
                        if fallback_response and fallback_response != primary_response and not fallback_response.startswith("Error"):
                            logger.info("✅ Fallback successful, using OpenAI response")
                            # 清空之前的响应，返回新的响应
                            yield f"\n\n[Enhanced by OpenAI] {fallback_response}"
                            return
                        else:
                            logger.warning("❌ Fallback failed or returned error, keeping primary response")
                    except Exception as fallback_error:
                        logger.warning(f"❌ Fallback failed with error: {fallback_error}, keeping primary response")
                else:
                    logger.info("✅ Primary model response quality good")
            
        except Exception as e:
            logger.error(f"❌ Primary model failed: {e}")
            if self.enable_fallback:
                logger.info("🔄 Falling back to OpenAI due to primary model error...")
                try:
                    fallback_response = await self._generate_with_openai(messages, system, "")
                    if fallback_response:
                        yield f"[Fallback response from OpenAI] {fallback_response}"
                        return
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error}")
                    yield f"[Error: Both models failed. Primary: {e}, Fallback: {fallback_error}]"
            else:
                yield f"[Error: Primary model failed: {e}]"

    async def _generate_with_openai(
        self, 
        messages: List[Dict[str, Any]], 
        system: str,
        context_response: str = ""
    ) -> str:
        """使用OpenAI生成高质量响应"""
        
        # 构建增强的上下文
        enhanced_messages = messages.copy()
        
        # 如果主模型已经生成了部分响应，将其作为上下文
        if context_response:
            enhanced_messages.append({
                "role": "assistant", 
                "content": f"[Previous response that needs improvement: {context_response}]"
            })
            enhanced_messages.append({
                "role": "user",
                "content": "Please provide a better, more character-appropriate response that matches the persona and is more engaging."
            })
        
        # 使用大模型生成
        response = ""
        try:
            token_stream = self._fallback_llm.chat_completion(enhanced_messages, system)
            async for event in token_stream:
                if isinstance(event, dict) and event.get("type") == "text_delta":
                    text_chunk = event.get("text", "")
                elif isinstance(event, str):
                    text_chunk = event
                else:
                    continue
                if text_chunk:
                    response += text_chunk
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return ""
        
        return response.strip()

    def _chat_function_factory(
        self,
    ) -> Callable[[BatchInput], AsyncIterator[Union[SentenceOutput, Dict[str, Any]]]]:
        """Create the chat pipeline function with dual model support."""

        @tts_filter(self._tts_preprocessor_config)
        @display_processor()
        @actions_extractor(self._live2d_model)
        @sentence_divider(
            faster_first_response=self._faster_first_response,
            segment_method=self._segment_method,
            valid_tags=["think"],
        )
        async def chat_with_dual_models(
            input_data: BatchInput,
        ) -> AsyncIterator[Union[str, Dict[str, Any]]]:
            """Process chat with dual model support."""
            self.reset_interrupt()
            self.prompt_mode_flag = False

            messages = self._to_messages(input_data)
            
            # 使用双模型生成响应
            complete_response = ""
            async for text_chunk in self._generate_with_fallback(messages, self._system):
                if text_chunk:
                    yield text_chunk
                    complete_response += text_chunk
            
            if complete_response:
                self._add_message(complete_response, "assistant")

        return chat_with_dual_models

    async def chat(
        self,
        input_data: BatchInput,
    ) -> AsyncIterator[Union[SentenceOutput, Dict[str, Any]]]:
        """Run chat pipeline with dual model support."""
        chat_func_decorated = self._chat_function_factory()
        async for output in chat_func_decorated(input_data):
            yield output

    def reset_interrupt(self) -> None:
        """Reset interrupt flag."""
        self._interrupt_handled = False

    def start_group_conversation(
        self, human_name: str, ai_participants: List[str]
    ) -> None:
        """Start a group conversation."""
        if not self._tool_prompts:
            logger.warning("Tool prompts dictionary is not set.")
            return

        other_ais = ", ".join(name for name in ai_participants)
        prompt_name = self._tool_prompts.get("group_conversation_prompt", "")

        if not prompt_name:
            logger.warning("No group conversation prompt name found.")
            return

        try:
            group_context = prompt_loader.load_util(prompt_name).format(
                human_name=human_name, other_ais=other_ais
            )
            self._memory.append({"role": "user", "content": group_context})
        except FileNotFoundError:
            logger.error(f"Group conversation prompt file not found: {prompt_name}")
        except KeyError as e:
            logger.error(f"Missing formatting key in group conversation prompt: {e}")
        except Exception as e:
            logger.error(f"Failed to load group conversation prompt: {e}")
