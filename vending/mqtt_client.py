# importing the library
import paho.mqtt.client as mqtt
# defining the variables
broker_address = "localhost"
broker_port = 1883
username = 'test_topic'
password = 'test'
topic = 'test'


# function to handle messages being posted
def on_message(client, userdata, message):
    from .models import Machine, Transaction
    msg = message.payload.decode('utf-8')
    print(msg)
    if not msg == '':
        try:
            serial = msg['serial_no']
            amount = msg['amount']
            volume = msg['volume']
            total_amount = msg['total_amount']
            total_volume = msg['total_volume']
            machine = Machine.objects.get(serial_number = serial)
            if machine.exists() and machine.remaining_tokens > 1:
                transaction = Transaction(machine = machine, amount = amount, volume = volume, total_amount = total_amount, total_volume = total_volume)
                transaction.save()
                transaction.remaining_tokens()
        except Exception as e:
            print(e)


# creating an instance of the mqtt client
client = mqtt.Client()
# client embedded functions like on_message which calls back the preddfined function
client.on_message = on_message

# authentication if necessary
# client.username_pw_set(username, password)

# connecting to the broker
# using a nested function for multi threading to prevent disrupting the main thread
def start_mqtt_client():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(topic)
            client.publish(topic)
        else:
            print(f"Failed to connect with result code {rc}")
    try:
      client.on_connect = on_connect
      client.connect(broker_address, broker_port, 60)

      try:
          client.loop_start()
      except Exception as e:
          print(f"Error starting MQTT loop: {e}")
          client.loop_stop()
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
