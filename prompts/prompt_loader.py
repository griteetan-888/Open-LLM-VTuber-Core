"""
Prompt loader for Open-LLM-VTuber Core
"""

def load_prompt(prompt_name: str) -> str:
    """Load a prompt by name"""
    # Simple prompt templates
    prompts = {
        'live2d_expression_prompt': 'Use facial expressions to convey emotions: [happy], [sad], [angry], [surprised], [neutral]',
        'think_tag_prompt': 'Use (thinking) tags for internal thoughts that should not be spoken aloud. Do not use [action] or [emotion] tags in your responses.',
        'group_conversation_prompt': 'You are participating in a group conversation. Be aware of other participants.',
        'mcp_prompt': 'You have access to various tools through MCP (Model Context Protocol).',
        'proactive_speak_prompt': 'You can speak proactively when appropriate.',
        'speakable_prompt': 'Make your responses suitable for text-to-speech synthesis.',
        'tool_guidance_prompt': 'Use available tools to help users effectively.',
        'live_prompt': 'You are interacting in a live streaming environment.'
    }
    
    return prompts.get(prompt_name, f'Prompt for {prompt_name} not found')

def load_util(prompt_name: str) -> str:
    """Load a utility prompt by name"""
    return load_prompt(prompt_name)
