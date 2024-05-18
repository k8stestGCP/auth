from google.cloud import pubsub_v1
from auth import get_current_user

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('united-crane-423621-t9', 'verification')

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('united-crane-423621-t9', 'verification-response-sub')


def verify_user(token: str):
    # Verify the token and return the result
    response = get_current_user(token)
    return response.user if response.user else None

def subscribe_to_topic():

    def callback(message):
        # Process the message (verify the user) and send the response
        token = message.data.decode('utf-8')
        user = verify_user(token)
                
        # Include a response identifier
        response_message += "OK" if user else "ERROR"
        
        # Send the response directly to the catalog microservice via a direct reply topic
        message = response_message.encode('utf-8')
        publisher.publish(topic_path, message)
        # Acknowledge the message
        message.ack()

    # Subscribe to the verification topic
    subscriber.subscribe(subscription_path, callback=callback)
    print('Listening for verification requests on {}'.format(subscription_path))

# Start message processing loop
if __name__ == '__main__':
    subscribe_to_topic()
