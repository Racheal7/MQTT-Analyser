"""
Part of the code referenced the paho-mqtt 1.6.1 documentation:
    https://pypi.org/project/paho-mqtt/#
"""
import paho.mqtt.client as mqtt
import time
import pandas as pd


broker_address = '35.178.41.84'
broker_port = 1883                 # Broker's port number

client_id = "Analyser"

received_msg = []
delay_intervals = [0, 0.001, 0.002, 0.01, 0.02, 0.1, 0.2]   # specify required delay intervals. 
qos_levels = [0, 1, 2]

debug = False

def on_connect(client, userdata, flags, rc):
    """
    This function is the callback for when the analyser receives a 
    CONNACK response from the broker.

    Parameters
    ----------
    client   : the client instance
    userdata : the private user date as set.
    flags    : response flags sent by the broker.
    rc       : the connection result (0 indicates connection successful).
    """    
    if rc == 0:    
        print("*** Analyser connected to the MQTT broker! ***")
    else:
        print("=== Bad connection Returned code: ",rc + " ===")    # If connection is refused, print out the error message.


def on_message(client, userdata, message):
    """
    This function is the callback for when a PUBLISH message is received from the server. 

    Parameters
    ----------
    message  : an instance of MQTTMessage (topic, payload, qos, retain)
    """
    global received_msg
    
    msg_timestamp = time.time()     # Get the message timestamp 
    
    # Get the delay interval of the message
    if 'counter' in message.topic:
        delay = int(message.topic.split('/')[2])
    else:
        delay = 0
        
    # Store the received data in an array for analysis.
    received_msg.append([msg_timestamp, message.topic, str(message.payload.decode()), message.qos, delay])
    
    if debug:
        print("Received message '" + str(message.payload.decode()) + "' on topic '"
              + message.topic + "' with QoS " + str(message.qos))
    
def on_publish(client, obj, mid):
    """
    This function is the callback for after a message is published. 
    """
    print("Published '" + str(mid) + "'")


def publish_to_broker(analyser):
    """
    This function pulishes to the request/qos and request/delay topics.
    
    Parameters
    ----------
    analyser   : the MQTT client instance
    """
    for qos in qos_levels:
        for delay in delay_intervals:
            qos_msg = analyser.publish(topic = "request/qos", payload = qos, qos = 2)
            qos_msg.wait_for_publish()      # Block the call until the message is published.
            delay_info = analyser.publish(topic = "request/delay", payload = int(delay*1000), qos = 2)
            delay_info.wait_for_publish()
            time.sleep(1)       # Stop for 2 second and wait for publish to finish.
            
            time.sleep(120)     # Listen for 120s.

            analyser.unsubscribe(topic = "counter/" + str(qos) + '/' + str(int(delay*1000)))      # Stop listen and unsubscribe the topic.
            print('Unsubscribe from counter/' + str(qos) + '/' + str(int(delay*1000)))
    
    
    analyser.unsubscribe(topic = "$SYS/#")
    print('Unsubscribe from $SYS')
    
    time.sleep(2)
    analyser.disconnect()   # Disconnect the analyser.

if __name__ == '__main__':
    
    # Create a MQTT client as analyser.
    analyser = mqtt.Client(client_id = client_id, clean_session=False, protocol=mqtt.MQTTv311)
    analyser.on_connect = on_connect
    analyser.on_message = on_message
    if True:
        analyser.on_publish = on_publish
    
    # Connect the analyser to the remote broker.
    analyser.connect(broker_address, broker_port)

    # Subscribe to the 'counter' topic using different qos levels. 
    for qos in qos_levels:
        topic_name = "counter/" + str(qos) + "/#"
        analyser.subscribe(topic_name, qos = qos)
    
    # Subscribe to the "$SYS/#" topic
    analyser.subscribe("$SYS/#")

    analyser.loop_start()
    publish_to_broker(analyser)
    analyser.loop_stop()
    
    # Store the analysis data into CSV file. 
    df = pd.DataFrame(received_msg, columns=['Time', 'Topic', 'Payload', 'QoS', 'Delay'])
    df.to_csv('analysis_data.csv', index=False)
    
