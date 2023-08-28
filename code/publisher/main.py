import json
from google.cloud import pubsub_v1

def start_script(request):
    print("Running cloud function...")
    data = request.get_json()  # Get the JSON data from the payload
    project_id = data.get('project_id')
    topic_name = data.get('topic_name')
    my_msg = data.get('my_msg')


    if project_id is None:
        return 'Missing required parameters: "project_id" is required.'
    else:    
        # Publish a message to the Pub/Sub topic
        publisher = pubsub_v1.PublisherClient()
        topic_path = f'projects/{project_id}/topics/{topic_name}'
        data = {"my_msg": my_msg}
        data_str = json.dumps(data).encode('utf-8')  # Convert dictionary to JSON-encoded bytestring
        publisher.publish(topic_path, data=data_str)
        print(f"Printing json message being published to topic ({topic_name}): {data}")
        return "Run successfull."