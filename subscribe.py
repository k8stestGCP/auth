from google.cloud import pubsub_v1
from auth import get_current_user

subscriber = pubsub_v1.SubscriberClient()
project_id = 'united-crane-423621-t9'
subscription_id = 'verification'
subscription_path = subscriber.subscription_path(project_id, subscription_id)
publisher = pubsub_v1.PublisherClient()


def verify_user(token: str):
    return get_current_user(token)

async def subscribe_to_topic():

    def callback(message):
        token = message.data.decode('utf-8')
        user = verify_user(token)
        print("Received message: {}".format(token))
        response_message = "OK" if user else "ERROR"
        response_message = response_message.encode('utf-8')
        print("Sending response: {}".format(response_message))
        topic_path = publisher.topic_path('united-crane-423621-t9', 'verification-response')
        publisher.publish(topic_path, data=response_message)
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)
    print('Listening for verification requests on {}'.format(subscription_path))
