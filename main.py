import json
import boto3
import uuid
from datetime import datetime

client = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Vocabulary')

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        prompt = "\n\nHuman: Best team in england in your own opinion\n\nAssistant:"

        # Create request for Bedrock
        response = client.invoke_model(
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 300,
                "temperature": 1.0,
                "top_p": 0.9,
                "top_k": 50,
                "stop_sequences": []
            }),
            contentType='application/json',
            accept='application/json',
            modelId='anthropic.claude-v2'
        )

        # Parse response
        data = response['body'].read().decode('utf-8')
        response_string = json.loads(data)

        # Generate unique ID and timestamp
        item_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Extract the word from the prompt (assuming the word is "Malawi")
        word = "Best_team_in_england"

        # Save to DynamoDB with proper key structure
        table.put_item(Item={
            'word': word,  # Primary key
            'id': item_id,
            'timestamp': timestamp,
            'question': prompt,
            'answer': response_string.get('completion', ''),
            'model': 'anthropic.claude-v2'
        })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'id': item_id,
                'response': response_string
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
