refine_prompt="""
Your goal is to improve the prompt given below for {task} :
--------------------

Prompt: {lazy_prompt}

--------------------

Here are several tips on writing great prompts:

-------

Start the prompt by stating that it is an expert in the subject.

Put instructions at the beginning of the prompt and use ### or to separate the instruction and context 

Be specific, descriptive and as detailed as possible about the desired context, outcome, length, format, style, etc 

---------

Here's an example of a great prompt:

As a master YouTube content creator, develop an engaging script that revolves around the theme of "Exploring Ancient Ruins."

Your script should encompass exciting discoveries, historical insights, and a sense of adventure.

Include a mix of on-screen narration, engaging visuals, and possibly interactions with co-hosts or experts.

The script should ideally result in a video of around 10-15 minutes, providing viewers with a captivating journey through the secrets of the past.

Example:

"Welcome back, fellow history enthusiasts, to our channel! Today, we embark on a thrilling expedition..."

-----

Now, improve the prompt.

IMPROVED PROMPT:
"""

make_prompt="""
Your goal is to improve the prompt given below for {task} :
--------------------

Prompt: {lazy_prompt}

--------------------

Here are several tips on writing great prompts:

-------

Start the prompt by stating that it is an expert in the subject.

Put instructions at the beginning of the prompt and use ### or to separate the instruction and context 

Be specific, descriptive and as detailed as possible about the desired context, outcome, length, format, style, etc 

---------

Here's an example of a great prompt:

As a master YouTube content creator, develop an engaging script that revolves around the theme of "Exploring Ancient Ruins."

Your script should encompass exciting discoveries, historical insights, and a sense of adventure.

Include a mix of on-screen narration, engaging visuals, and possibly interactions with co-hosts or experts.

The script should ideally result in a video of around 10-15 minutes, providing viewers with a captivating journey through the secrets of the past.

Example:

"Welcome back, fellow history enthusiasts, to our channel! Today, we embark on a thrilling expedition..."

-----

Now, improve the prompt.

IMPROVED PROMPT:
"""

make_prompt_v2="""
Your goal is to improve the prompt given below for {task}, using structured task decomposition instead of prose:
--------------------

Prompt: {lazy_prompt}

--------------------

Rewrite it by filling in each of these sections based on the original prompt's intent — do not skip a section, even a short one:

<role>The specific expertise or persona the AI should adopt.</role>
<context>Background information needed to understand the task.</context>
<instructions>
1. Step-by-step breakdown of what the AI must do.
2. Any sub-tasks implied by the original prompt.
</instructions>
<constraints>Length, format, tone, or scope limits that must be respected.</constraints>
<output_format>Exactly how the final answer should be structured (e.g. bullet list, JSON, prose).</output_format>

Now, improve the prompt using this structure.

IMPROVED PROMPT:

"""

prompt_improver = """
You are an expert Prompt Writer for Large Language Models.

Your goal is to improve the prompt given below:
--------------------

{text}

--------------------

Here are several tips on writing great prompts:

-------

Start the prompt by stating that it is an expert in the subject.

Put instructions at the beginning of the prompt and use ### or to separate the instruction and context 

Be specific, descriptive and as detailed as possible about the desired context, outcome, length, format, style, etc 
---------
Here's an example of a great prompt:

As a certified nutritionist, create a 7-day meal plan for a vegan athlete. 

The meal plan should provide all necessary nutrients, including protein, carbohydrates, fats, vitamins, and minerals. 

Each day should include breakfast, lunch, dinner, and two snacks. 

Please include a brief description of each meal and its nutritional benefits. 

The output should be in a daily format, with each meal detailed. 

Example:

Day 1:
Breakfast: Tofu scramble with vegetables (Provides protein and fiber)
Snack 1: A handful of mixed nuts (Provides healthy fats and protein)
...


Now, improve the prompt below:

IMPROVE PROMPT:

"""