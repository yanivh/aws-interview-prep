# Bedrock Agent Setup Guide

This guide explains how to set up a Bedrock Agent for enhanced answer evaluation (optional).

## Prerequisites

- AWS Bedrock access enabled in eu-central-1
- Appropriate IAM permissions to create Bedrock Agents
- (Optional) Knowledge Base with AWS documentation

## Setup Steps

### Option 1: Using AWS Console

1. Go to AWS Bedrock Console → Agents
2. Click "Create Agent"
3. Configure agent:
   - Name: `aws-interview-prep-answer-evaluator`
   - Description: "Evaluates AWS Systems Engineer interview answers"
   - Foundation Model: Claude 3 Sonnet
   - Instructions: Use content from `infrastructure/agent-config.json`
4. Create Agent Alias (e.g., `TSTALIASID`)
5. Note the Agent ID and Alias ID

### Option 2: Using AWS CLI

```bash
# Create agent
aws bedrock-agent create-agent \
    --agent-name aws-interview-prep-answer-evaluator \
    --description "Evaluates AWS Systems Engineer interview answers" \
    --foundation-model anthropic.claude-3-sonnet-20240229-v1:0 \
    --instruction "$(cat infrastructure/agent-config.json | jq -r '.instruction')" \
    --region eu-central-1

# Note the agent ID from response
AGENT_ID="your-agent-id"

# Create agent alias
aws bedrock-agent create-agent-alias \
    --agent-id $AGENT_ID \
    --agent-alias-name TSTALIASID \
    --region eu-central-1
```

### Optional: Knowledge Base Integration

1. Create Bedrock Knowledge Base with AWS documentation
2. Connect agent to knowledge base
3. This allows agent to reference AWS docs when evaluating answers

## Configuration

After creating the agent, set environment variables:

```bash
export BEDROCK_AGENT_ID="your-agent-id"
export BEDROCK_AGENT_ALIAS_ID="TSTALIASID"
```

Update Lambda function environment variables with these values.

## Testing

Test the agent by invoking it directly:

```bash
aws bedrock-agent-runtime invoke-agent \
    --agent-id $BEDROCK_AGENT_ID \
    --agent-alias-id $BEDROCK_AGENT_ALIAS_ID \
    --session-id test-session \
    --input-text "Evaluate this answer: [test answer]" \
    --region eu-central-1
```

## Note

If you don't set up an agent, the system will fall back to direct Bedrock model calls for answer evaluation, which still works but may be less sophisticated.
