import json
from anthropic import Anthropic

def run_demo(session):

    bedrock = session.client('bedrock')

    bedrock_runtime = session.client('bedrock-runtime', region_name="us-east-1")

    #model_id = "amazon.titan-embed-text-v1"
    model_id = "anthropic.claude-v1"
    model_id = "anthropic.claude-v2"
    model_id = "anthropic.claude-instant-v1"

    demo_zero_shot(bedrock_runtime, model_id, "What is the diammeter of the sun?")


def demo_zero_shot(bedrock_runtime, model_id, text):

    print("call demo_zero_shot")

    prompt = f"\n\nHuman: {text}\n\nAssistant:"

    request = {
        "prompt": prompt,
        "temperature": 0.0,
        "top_p": 0.5,
        "top_k": 300,
        "max_tokens_to_sample": 2048,
        "stop_sequences": []
    }

    response = bedrock_runtime.invoke_model(modelId = model_id, body = json.dumps(request))

    response_body_json = json.loads(response["body"].read())
    completion = response_body_json['completion']

    print(f"Answer: {completion}")

    ###

    anthropic_client = Anthropic()
    prompt_tokens = anthropic_client.count_tokens(prompt)
    completion_tokens = anthropic_client.count_tokens(completion)

    print(f'prompt_tokens: {prompt_tokens:,}, completion_tokens: {completion_tokens:,}')