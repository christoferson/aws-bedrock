import logging
from anthropic import AnthropicBedrockMantle
import json

client = AnthropicBedrockMantle()

# response = client.messages.create(
#     model="anthropic.claude-opus-4-7",
#     max_tokens=2048,
#     messages=[{"role": "user", "content": "Generate EvenBridge rule for CodeCommit. On Push to master branch."}]
# )

# text_response = response.content[0].text
# print(f"Response: {text_response}")

# Response: # EventBridge Rule for CodeCommit Push to Master Branch

# Here's how to create an EventBridge rule that triggers on pushes to the `master` branch of a CodeCommit repository.

# ## Event Pattern (JSON)

# ```json
# {
#   "source": ["aws.codecommit"],
#   "detail-type": ["CodeCommit Repository State Change"],
#   "resources": ["arn:aws:codecommit:us-east-1:123456789012:YourRepoName"],
#   "detail": {
#     "event": ["referenceCreated", "referenceUpdated"],
#     "referenceType": ["branch"],
#     "referenceName": ["master"]
#   }
# }
# ```

# > **Note:** Replace `us-east-1`, `123456789012`, and `YourRepoName` with your actual region, account ID, and repository name.

# ---

# ## Option 1: AWS CLI

# ```bash
# # Create the rule
# aws events put-rule \
#   --name "CodeCommit-Push-To-Master" \
#   --description "Triggers on push to master branch" \
#   --event-pattern '{
#     "source": ["aws.codecommit"],
#     "detail-type": ["CodeCommit Repository State Change"],
#     "resources": ["arn:aws:codecommit:us-east-1:123456789012:YourRepoName"],
#     "detail": {
#       "event": ["referenceCreated", "referenceUpdated"],
#       "referenceType": ["branch"],
#       "referenceName": ["master"]
#     }
#   }'

# # Add a target (e.g., Lambda function)
# aws events put-targets \
#   --rule "CodeCommit-Push-To-Master" \
#   --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:YourFunction"
# ```

# ---

# ## Option 2: CloudFormation (YAML)

# ```yaml
# Resources:
#   CodeCommitPushRule:
#     Type: AWS::Events::Rule
#     Properties:
#       Name: CodeCommit-Push-To-Master
#       Description: Triggers on push to master branch
#       EventPattern:
#         source:
#           - aws.codecommit
#         detail-type:
#           - CodeCommit Repository State Change
#         resources:
#           - !Sub arn:aws:codecommit:${AWS::Region}:${AWS::AccountId}:YourRepoName
#         detail:
#           event:
#             - referenceCreated
#             - referenceUpdated
#           referenceType:
#             - branch
#           referenceName:
#             - master
#       State: ENABLED
#       Targets:
#         - Arn: !GetAtt YourLambdaFunction.Arn
#           Id: LambdaTarget

#   LambdaInvokePermission:
#     Type: AWS::Lambda::Permission
#     Properties:
#       FunctionName: !Ref YourLambdaFunction
#       Action: lambda:InvokeFunction
#       Principal: events.amazonaws.com
#       SourceArn: !GetAtt CodeCommitPushRule.Arn
# ```

# ---

# ## Option 3: Terraform

# ```hcl
# resource "aws_cloudwatch_event_rule" "codecommit_push_master" {
#   name        = "CodeCommit-Push-To-Master"
#   description = "Triggers on push to master branch"

#   event_pattern = jsonencode({
#     source        = ["aws.codecommit"]
#     "detail-type" = ["CodeCommit Repository State Change"]
#     resources     = ["arn:aws:codecommit:us-east-1:123456789012:YourRepoName"]
#     detail = {
#       event         = ["referenceCreated", "referenceUpdated"]
#       referenceType = ["branch"]
#       referenceName = ["master"]
#     }
#   })
# }

# resource "aws_cloudwatch_event_target" "lambda_target" {
#   rule      = aws_cloudwatch_event_rule.codecommit_push_master.name
#   target_id = "LambdaTarget"
#   arn       = aws_lambda_function.your_function.arn
# }
# ```

# ---

# ## Key Event Pattern Fields

# | Field | Description |
# |-------|-------------|
# | `event` | `referenceCreated` (first push) or `referenceUpdated` (subsequent pushes) |
# | `referenceType` | `branch` or `tag` |
# | `referenceName` | Branch name (e.g., `master`, `main`) |
# | `resources` | ARN of the specific CodeCommit repo |

# 💡 **Tip:** For new repos, consider using `main` instead of `master` as the default branch. You can also include both: `"referenceName": ["master", "main"]`.




###

response = client.messages.create(
    model="anthropic.claude-opus-4-7",
    max_tokens=2048,
    messages=[
        {"role": "user", 
            "content": "Generate EvenBridge rule for CodeCommit. On Push to master branch. IMPORTANT: Your entire response must be valid JSON. Start immediately with { and end with }. No explanations, no markdown, just JSON."
            }
    ]
)

text_response = response.content[0].text
print(f"Response: {text_response}")

json = json.loads(text_response.strip())
print(f"JSON: {json}")