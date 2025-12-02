# iching_system/divination/__init__.py
"""
起卦模組
========

包含四種起卦方式：
- A1: 隨機起卦
- A2: 報數起卦
- A3: 問卷起卦
- A4: Agent 起卦
"""

from .a1_random import (
    random_divination,
    quick_random,
    interactive_random_divination
)

from .a2_number import (
    number_divination,
    time_divination,
    name_divination,
    interactive_number_divination
)

from .a3_questionnaire import (
    questionnaire_divination,
    quick_questionnaire,
    interactive_questionnaire_divination,
    classify_question,
    get_aspects_for_question,
    DEFAULT_ASPECTS
)

from .a4_agent import (
    agent_divination_a4_1,
    quick_agent_divination
)

__all__ = [
    # A1
    'random_divination',
    'quick_random',
    'interactive_random_divination',
    
    # A2
    'number_divination',
    'time_divination',
    'name_divination',
    'interactive_number_divination',
    
    # A3
    'questionnaire_divination',
    'quick_questionnaire',
    'interactive_questionnaire_divination',
    'classify_question',
    'get_aspects_for_question',
    'DEFAULT_ASPECTS',
    
    # A4
    'agent_divination_a4_1',
    'quick_agent_divination'
]
