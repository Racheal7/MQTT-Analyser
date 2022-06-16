# MQTT Analyser
MQTT is the most common open IoT protocol being deployed today, which is designed to provide high-performance communication mechanisms, with minimal delays and excellent scaling performance. This project explores MQTT functionality in subscribing/publishing to a broker and the quality-of-service (QoS) levels.

## Broker Setup

You can choose to use a public broker or set up your own broker on AWS. Please note that the broker used in the code is the private broker that I set up on the AWS and it has been terminated. 

## Coding Environment

The code is written in Python3 and tested on the Windows 10 OS system. An external library paho-mqtt is used. To install paho-mqtt, please use the below command: "**pip install paho-mqtt**". If you are using Python in Anaconda environment, please open Anaconda Prompt and type in the command: "**pip install paho-mqtt**". When running the program, please start the Controller.py first and then start the Analyser.py. The result are stored in the analysis_data.csv file for analysis later. 

## Analyser.py

The **Analyser** creates a MQTT client that publishes to the ‘*request/qos*’ and ‘*request/delay*’ topics with three QoS levels (0, 1, 2) and seven delay intervals (0ms, 1ms, 2ms, 10ms, 20ms, 100ms, 200ms). The analyser will listen to each *counter/\** topic for two minutes and report statistics on the performance of all (7 delay * 3 qos) measurements sequentially in one run.

## Controller.py

This file creats two MQTT clients: one controller and one publisher. 
1. The **Controller** will listen to the broker on two topics ‘*request/qos*’ and ‘*request/delay*’. Whenever it gets a message on either of them it creates a new publisher with the new QoS level and delay interval. 
2. The **Publisher** publishes an incrementing counter (0, 1, 2, 3, …) at a specific QoS level (0, 1 or 2), and with a specific delay between messages (0ms, 1ms, 2ms, 10ms, 20ms, 100ms, 200ms) to the topic ‘*counter/qos/delay*’ (e.g. ‘counter/1/100’ implies qos=1 and delay=100). It publishes one stream at any given time, based on input from the Controller.

### Note
Please reference to this repository when using the code.
