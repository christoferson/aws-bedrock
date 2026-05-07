import logging
from anthropic import AnthropicBedrockMantle
import json
from statistics import mean

client = AnthropicBedrockMantle()

eval_json = """
[
    {
        "task": "Write a Python function that takes an S3 bucket name and a prefix as arguments, and returns a list of all object keys in that bucket matching the prefix using the boto3 library."
    },
    {
        "task": "Write an IAM policy JSON object that allows read-only access to a specific S3 bucket named 'my-company-data', including the ability to list objects and retrieve object contents, but explicitly denies the ability to delete or upload objects."
    },
    {
        "task": "Write a regular expression that validates an Amazon Resource Name (ARN) string, ensuring it follows the standard AWS ARN format: arn:partition:service:region:account-id:resource."
    }
]
"""

# Helper function to create messages
def create_chat(messages, stop_sequences=None, model="anthropic.claude-opus-4-7"):
    """Wrapper around client.messages.create"""
    params = {
        "model": model,
        "max_tokens": 2048,
        "messages": messages
    }
    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)
    return response.content[0].text

# Function to extract JSON from response
def extract_json(text):
    """Extract JSON from markdown code blocks or raw text"""
    # Try to find JSON in code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        json_text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        json_text = text[start:end].strip()
    else:
        json_text = text.strip()

    return json.loads(json_text)

# Function to grade a test case + output using a model
def grade_by_model(test_case, output):
    eval_prompt = f"""
You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

IMPORTANT: Respond ONLY with valid JSON. You may wrap it in ```json code blocks if you prefer.
Keep your response concise and direct.

Example response shape:
{{
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "reasoning": "Brief explanation",
    "score": 8
}}
    """

    messages = [
        {"role": "user", "content": eval_prompt}
    ]

    # Use Haiku for evaluation (without prefill)
    eval_text = create_chat(messages, model="anthropic.claude-haiku-4-5")

    # Extract and parse JSON from response
    try:
        return extract_json(eval_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from evaluation response: {e}")
        print(f"Raw response: {eval_text}")
        # Return a default structure if parsing fails
        return {
            "strengths": ["Unable to parse evaluation"],
            "weaknesses": ["JSON parsing error"],
            "reasoning": "Evaluation response was not valid JSON",
            "score": 5
        }

# Passes a test case into Claude
def run_prompt(test_case):
    prompt = f"""
Please solve the following task:

{test_case["task"]}
"""

    messages = [{"role": "user", "content": prompt}]
    # Use Opus for generating solutions
    output = create_chat(messages, model="anthropic.claude-opus-4-7")
    return output

# Function to execute a single test case and grade the output
def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    print(f"\n{'='*60}")
    print(f"Running test case: {test_case['task'][:80]}...")
    print(f"{'='*60}")

    output = run_prompt(test_case)
    print(f"\nGenerated Output (using claude-opus-4-7):\n{output[:200]}...")

    print(f"\nEvaluating with claude-haiku-4-5...")
    model_grade = grade_by_model(test_case, output)
    score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    print(f"\nScore: {score}/10")
    print(f"Reasoning: {reasoning}")
    print(f"Strengths: {model_grade['strengths']}")
    print(f"Weaknesses: {model_grade['weaknesses']}")

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning,
        "strengths": model_grade["strengths"],
        "weaknesses": model_grade["weaknesses"]
    }

def run_eval(dataset):
    """Loads the dataset and calls run_test_case with each case"""
    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([result["score"] for result in results])

    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Model for solutions: anthropic.claude-opus-4-7")
    print(f"Model for evaluation: anthropic.claude-haiku-4-5")
    print(f"Average score: {average_score:.2f}/10")
    print(f"Total test cases: {len(results)}")
    print(f"{'='*60}\n")

    return results

# Load dataset and run evaluation
dataset = json.loads(eval_json)
results = run_eval(dataset)

# Optional: Save results to file
with open("eval_results.json", "w") as f:
    json.dump(results, f, indent=2)
    print("Results saved to eval_results.json")