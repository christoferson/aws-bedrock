import json
from anthropic import Anthropic

def run_demo(session):

    bedrock = session.client('bedrock')

    bedrock_runtime = session.client('bedrock-runtime', region_name="us-east-1")

    #model_id = "amazon.titan-embed-text-v1"
    model_id = "anthropic.claude-v1"
    model_id = "anthropic.claude-v2"
    model_id = "anthropic.claude-instant-v1"

    #demo_zero_shot(bedrock_runtime, model_id, "What is the diammeter of the sun?")

    text = """
    On a given week, the viewers for a TV channel were
    Monday: 6500 viewers
    Tuesday: 6400 viewers
    Wednesday: 6300 viewers


    Question: How many viewers can we expect on Friday?
    Answer: Based on the numbers given and without any more information, there is a daily decrease of 100 viewers. If we assume this trend will continue during the following days, we can expect 6200 viewers on the next day that would be Thursday, and therefore 6100 viewers on the next day that would be Friday.


    Question: How many viewers can we expect on Saturday? (Think Step-by-Step)
    Answer:
    """

    demo_chain_of_thought(bedrock_runtime, model_id, text)


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


def demo_chain_of_thought(bedrock_runtime, model_id, text):

    print("call demo_chain_of_thought")

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
