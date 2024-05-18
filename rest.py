from google.cloud import pubsub_v1
from auth import get_current_user

message = "okayeg"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('united-crane-423621-t9', 'verification-response')

message = message.encode('utf-8')
future = publisher.publish(topic_path, data=message)
future.result()  

print('Enviado')
