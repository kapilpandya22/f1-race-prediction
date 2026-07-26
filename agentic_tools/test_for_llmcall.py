from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

models = client.models.list()

for model in models.data:
    print(model.id)