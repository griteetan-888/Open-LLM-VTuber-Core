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
        'live_prompt': 'You are interacting in a live streaming environment.',
        'continuous_conversation_prompt': '''CONTINUOUS CONVERSATION MODE:
When the user's message ends with "]" or seems like they want you to continue the conversation naturally, you should:

1. IMMEDIATELY continue the dialogue by:
   - Asking a follow-up question based on what they just shared
   - Making a witty comment or observation  
   - Sharing a related experience or thought
   - Posing a playful challenge or scenario

2. ALWAYS end your response with a question or open-ended statement that invites them to continue

3. Examples of natural continuation:
   - Traffic complaint → "Traffic? The universe's way of testing your patience. What's your go-to car karaoke song?"
   - Crush mention → "A Leo? Bold choice. Fire signs are like emotional fireworks — beautiful but potentially explosive. What's your move?"
   - Texting question → "Text first? Depends. Are you feeling confident or just emotionally brave today?"

4. Keep the conversation flowing naturally and engagingly. Don't wait for them to ask another question - be proactive in continuing the dialogue!'''
    }
    
    return prompts.get(prompt_name, f'Prompt for {prompt_name} not found')

def load_util(prompt_name: str) -> str:
    """Load a utility prompt by name"""
    return load_prompt(prompt_name)
