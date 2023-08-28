import json
import base64

def pubsub_handler(event, context):
    print("Running cloud function...")
    # Retrieve the JSON payload from the Pub/Sub message
    pubsub_message = event['data']
    decoded_message = base64.b64decode(pubsub_message).decode('utf-8')  # Decode and convert to string
    print(f"Printing pubsub message received: {decoded_message}")
    # data_dict = json.loads(decoded_message)  # optional
    # my_msg = data_dict["my_msg"]  # optional
    return "Run successfull."