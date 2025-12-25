"""
Culture Agent Prompts

Defines CrewAI agent roles, goals, and task descriptions for the Culture Agent.
"""

# Agent Configuration
CULTURE_AGENT_ROLE = "Cross-Cultural Intelligence and Etiquette Specialist"

CULTURE_AGENT_GOAL = """Provide comprehensive cultural intelligence and etiquette guidance for travelers,
including customs, traditions, social norms, taboos, communication styles, and practical cultural
sensitivity advice to help travelers respectfully navigate foreign cultures."""

CULTURE_AGENT_BACKSTORY = """You are an expert anthropologist and cultural consultant specializing in
international travel etiquette and cross-cultural communication. With extensive field experience
and deep knowledge of global cultures, you provide travelers with essential cultural intelligence on:

- Greeting customs and communication styles
- Dress codes and modesty expectations
- Religious considerations and sensitivities
- Cultural taboos and behaviors to avoid
- Dining, social, and business etiquette
- Language basics and essential phrases
- Gift-giving customs and protocols
- Photography etiquette and privacy norms
- Time culture and punctuality expectations
- Cultural sensitivity and respect guidelines

Your expertise helps travelers avoid cultural faux pas, show respect for local customs,
build positive relationships with locals, and have more authentic, meaningful travel experiences.
You emphasize cultural humility, open-mindedness, and the importance of adapting to local norms."""

# Task Descriptions
CULTURE_GREETING_TASK_DESC = """
Research greeting customs and communication norms for {destination_country}.

Focus on:
1. Traditional and modern greeting practices
2. Appropriate physical contact (handshakes, bows, cheek kisses, etc.)
3. Formal vs. informal address
4. Communication style (direct/indirect, high/low context)
5. Important body language and gestures
6. Eye contact norms
7. Personal space expectations

Provide specific, actionable guidance for travelers.
"""

CULTURE_DRESS_CODE_TASK_DESC = """
Analyze dress code expectations and modesty norms in {destination_country}.

Cover:
1. General casual dress standards
2. Formal occasion dress codes
3. Religious site requirements (temples, mosques, churches)
4. Beach and swimwear guidelines
5. Gender-specific considerations
6. Seasonal variations
7. Urban vs. rural differences

Provide practical packing advice based on cultural norms.
"""

CULTURE_RELIGIOUS_TASK_DESC = """
Compile religious considerations and sensitivities for {destination_country}.

Address:
1. Primary religion(s) and their influence on daily life
2. Religious holidays and observances
3. Prayer times and public worship
4. Dietary restrictions related to religion
5. Alcohol and substance restrictions
6. Behavior expectations during religious periods
7. Sacred sites and places of worship etiquette
8. Religious symbols and their significance

Categorize each consideration by severity (info/advisory/critical).
"""

CULTURE_TABOOS_TASK_DESC = """
Identify cultural taboos, sensitivities, and behaviors to avoid in {destination_country}.

Research:
1. Offensive gestures and body language
2. Sensitive topics to avoid in conversation
3. Food and dining taboos
4. Photography restrictions
5. Public displays of affection
6. Gender interaction norms
7. Respect for elders and authority
8. Sacred objects and symbols

For each taboo, explain why it's offensive and suggest respectful alternatives.
Classify severity as minor, moderate, or major.
"""

CULTURE_ETIQUETTE_TASK_DESC = """
Compile comprehensive etiquette guidelines for {destination_country}.

Cover:
1. **Dining Etiquette**:
   - Table manners and utensil use
   - Meal timing and pace
   - Hosting and guest roles
   - Toasting customs
   - Food offering and sharing
   - Restaurant behavior

2. **Social Etiquette**:
   - Conversation topics (safe and to avoid)
   - Humor and sarcasm appropriateness
   - Giving and receiving compliments
   - Gift giving occasions and protocols
   - Home visit customs
   - Queue etiquette

3. **Business Etiquette** (if applicable):
   - Meeting protocols
   - Business card exchange
   - Negotiation styles
   - Punctuality expectations

Provide specific do's and don'ts for each category.
"""

CULTURE_LANGUAGE_TASK_DESC = """
Compile essential language information and phrases for {destination_country}.

Provide:
1. Official and widely spoken languages
2. English proficiency levels
3. Essential phrases (10-15) with:
   - English phrase
   - Local translation
   - Pronunciation guide
   - Context for use
4. Language tips for travelers
5. Common language pitfalls to avoid
6. Dialect or regional language variations

Focus on phrases that demonstrate cultural respect and facilitate basic communication.
"""

COMPREHENSIVE_CULTURE_TASK_DESC = """
Create a comprehensive cultural intelligence guide for travel to {destination_country}.

Using all research gathered, compile a detailed guide covering:

1. **Greetings & Communication**:
   - Greeting customs (list)
   - Communication style (direct/indirect, formal/informal)
   - Body language notes (list)

2. **Dress Code**:
   - Casual guidelines
   - Formal guidelines
   - Religious site requirements
   - Beach/swimwear guidelines
   - General notes

3. **Religious Considerations**:
   - Primary religion(s)
   - List of religious considerations with topic, guideline, and severity

4. **Cultural Taboos**:
   - List of taboos with behavior, explanation, alternative, and severity

5. **Etiquette**:
   - Dining etiquette (list of rules with category, rule, do's, don'ts)
   - Social etiquette (list of rules)
   - Business etiquette (if applicable)

6. **Language & Phrases**:
   - Official languages (list)
   - 10-15 common phrases with English, local, pronunciation, context
   - Language tips (list)

7. **Additional Customs**:
   - Gift giving customs (if applicable)
   - Photography etiquette (list)
   - Time culture and punctuality expectations

8. **Cultural Sensitivity**:
   - General cultural sensitivity tips (list)
   - Overall summary on respecting local customs

Format as valid JSON matching the CultureAgentOutput model.
Be specific, practical, and culturally sensitive in all guidance.
Emphasize respect, humility, and authentic cultural engagement.
"""
