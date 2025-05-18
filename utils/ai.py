import openai

def get_ai_plan(prompt):
    structured_prompt = (
        f"{prompt}\n\n"
        "Please return a clearly formatted longevity plan with the following sections:\n"
        "- Sleep\n- Exercise\n- Diet\n- Stress Management\n"
        "Also include 5 specific, practical daily habits in a separate section titled 'Daily Habits'."
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a longevity coach. Create personalized health plans with clear structure and formatting."},
            {"role": "user", "content": structured_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_habits(plan_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extract exactly 5 clear, specific daily habits from this plan (no headers)."},
            {"role": "user", "content": plan_text}
        ]
    )
    habits = [line.strip("•-• ").strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]
    return habits[:5]

def calculate_scores(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Score the user’s health habits (0-100) based on Sleep, Diet, Exercise, and Stress. Format each on a new line like: Sleep: 80"},
            {"role": "user", "content": prompt}
        ]
    )
    text = response.choices[0].message.content
    scores = {"Sleep": 0, "Diet": 0, "Exercise": 0, "Stress": 0}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            try:
                scores[key.strip()] = int(value.strip())
            except ValueError:
                continue
    return scores
