
import time
import paho.mqtt.client as mqtt
import threading
import random

broker_address = '13.54.12.91'
broker_port = 1883                 # Broker's port number

publisher_id = "Publisher"
controller_id = "Controller"

delay_intervals = [0, 0.001, 0.002, 0.01, 0.02, 0.1, 0.2]   # Seven delay intervals
qos_levels = [0, 1, 2]
current_qos = 0     # current running QoS level.

debug = True        # debug indicator, set to False if don't want to print out messages.


def publisher_on_connect(client, userdata, flags, rc):
    """
    This function is the callback for when the publisher receives a 
    CONNACK response from the broker.

    Parameters:  rc - the connection result (0 indicates connection successful).
    """
    if rc == 0:    
        print("*** A new publisher created and connected to the MQTT! ***")
    else:
        print("=== Bad connection Returned code: ",rc + " ===")    # If connection is refused, print out the error message.


def controller_on_connect(client, userdata, flags, rc):
    """
    This function is the callback for when the controller receives a 
    CONNACK response from the broker.
    
    Parameters:  rc - the connection result (0 indicates connection successful).
    """
    if rc == 0:
        print("*** Controller connected to the MQTT! ***")
    else:
        print("=== Bad connection Returned code: ",rc + " ===")    # If connection is refused, print out the error message.
        
        
def controller_on_message(client, userdata, msg):
    """
    This function is the callback for when a PUBLISH message is received from the server. 

    Parameters
    ----------
    client   : the client instance
    userdata : the private user date as set.
    msg  : an instance of MQTTMessage (topic, payload, qos, retain)
    """
    global current_qos
    
    if debug:
        print("Message received from topic: " + msg.topic + " "+ str(msg.payload.decode())) 
        
    # If receives a qos, update the gloable qos and wait for delay.
    if msg.topic == 'request/qos':
        received_qos = int(msg.payload.decode())
        current_qos = received_qos
        
    # If receives a delay, create a new publisher thread and bind it to controller.
    elif msg.topic == 'request/delay':
        received_delay = int(msg.payload.decode())
        publisher_thread = threading.Thread(target=create_publisher, kwargs={'qos': current_qos, 'delay': received_delay})
        publisher_thread.start()
        publisher_thread.join()   
        
        
def create_publisher(qos, delay):
    """
    This function creates a new publisher and publishes messages to the counter topic.

    Parameters
    ----------
    qos : specified quality of service level.
    delay  :  specified delay interval.
    """
    id = str(random.randint(1, 100))   # randomly generate an unique ID for the publisher
    publisher = mqtt.Client(client_id=publisher_id + id, clean_session = True, protocol=mqtt.MQTTv311)   # create a publisher.

    publisher.on_connect = publisher_on_connect
    publisher.connect(broker_address, broker_port)
    
    publisher.loop_start()
    
    count = 0   # initialise counter to 0
    topic_name = "counter/" + str(qos) + "/" + str(delay)   # set up topic name
    start_time = time.time()    # record the loop start time. 
    
    # publish to counter topic for 120 seconds.
    while time.time() - start_time <= 120:
        published_msg = publisher.publish(topic = topic_name, payload = count, qos = qos)
        published_msg.wait_for_publish()  # block until message is published.
        count += 1
        time.sleep(delay/1000)  # delay between messages.
    
    print("Topic '" + topic_name + "' counter : " + str(count))
    publisher.loop_stop()   
    publisher.disconnect()  # disconnect the publisher once complete.
    
    
def controller():
    """
    This function subscribe to the topic "request/qos" and "request/delay" 
    and changes the behaviour of publisher.
    """
    
    # Create a controller. 
    controller = mqtt.Client(client_id = controller_id, clean_session=True, protocol=mqtt.MQTTv311)
    controller.on_connect = controller_on_connect
    controller.on_message = controller_on_message
    
    controller.connect(broker_address, broker_port, keepalive = 500)       # Connect the client to a broker
    
    # Subscribe to request/qos and request/delay topics. QoS is set to 2 to ensure delivery. 
    controller.subscribe(topic = 'request/#', qos = 2)
    controller.loop_forever()
    

if __name__ == "__main__":
    
    # Start to run the controller.
    controller()
