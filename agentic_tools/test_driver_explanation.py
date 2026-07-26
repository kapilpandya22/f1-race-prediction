# test_driver_explanation.py

from openai import OpenAI
from driver_tool import DriverTool

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

tool = DriverTool()

summary = tool.get_driver_summary(
    race_name="Australian Grand Prix",
    driver="RUS",
    model="logistic"
)

prompt = f"""
You are RaceIQ, an F1 prediction analyst.

Driver Summary:
{summary}

Rules:
- Use ONLY the information provided.
- Do NOT guess driver identities.
- Do NOT invent statistics.
- Explain why this driver is highly ranked.
- Keep the answer under 120 words.
"""

response = client.chat.completions.create(
    model="qwen2.5-3b-instruct.gguf",
    messages=[
        {
            "role": "system",
            "content": "You are an F1 race prediction analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.1
)

print(response.choices[0].message.content)