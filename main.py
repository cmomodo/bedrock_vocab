import json
import boto3

client = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    prompt = "\n\nHuman: whats the population of lisbon\n\nAssistant:"

    # Create a request syntax - get details from console and body should be a JSON object
    response = client.invoke_model(
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 300,  # Corrected key
            "temperature": 1.0,
            "top_p": 0.9,
            "top_k": 50,
            "stop_sequences": []
        }),
        contentType='application/json',
        accept='application/json',
        modelId='anthropic.claude-v2'
    )

    print(response['body'])
#convert Streaming body to byte and then byte to string
    data = response['body'].read().decode('utf-8')
    response_string = json.loads(data)

#save the response to a file in s3 bucket
    s3 = boto3.resource('s3')
    s3.Bucket('cee-cee27').put_object(Key='response.txt', Body=json.dumps(response_string))

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(response_string)
    }
