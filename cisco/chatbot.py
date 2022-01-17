from flask import Flask, request, json
from messenger1 import Messager
import requests
import Meraki
from pprint import ppr

app = Flask(__name__)
port = 5005

msg = Messager()

@app.route('/', methods=(['GET', 'POST'])
def index():
    """Receive a  notification from Webex Teams and handle it"""
    if request.method == 'GET':
        return f'Request received on local port {port}'
    elif request.method == 'POST':
        if 'application/json' in request.headers.get('Content-Type'):
            # Notification payload, received from Webex Teams webhook
            data = request.get_json()

            # Loop prevention, ignore messages which were posted by itself.
            #  The bot_id attribute is collected from the Webex Teams API
            # at object instatiation.
            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'
            else:
                # print the notification payload, received from the webhook
                print(json.dumps(data, indent=4))

                # Collect the roomID from the notification,
                # so you know where to post the response
                # Set the msg object attribute
                room_id = data.get('data').get('roomId')
                msg.room_id = room_id

                # Collect the message id from the notification,
                # so you can fetch the message content
                message_id = data.get('data').get('id')

                # Get the contents of the received message.
                msg.get_message(message_id)

                # if message starts with '/meraki',
                # make some API calls to the Meraki API server.
                # if not, just post a confirmation that a message was received.
                if msg.message_text.startswith('/meraki'):
                    # Default action is to list SSIDs of a predefined network.
                    try:
                        action = msg.message_text.split()[1]
                    except IndexError:
                        action = 'ssids'

                    # '/meraki networks' fetches all the networks,
                    # belonging to the organization, and prints them in the room
                    if action == 'networks':
                        network_list = meraki.get_networks()

                        msg_reply = f'Networks for organization {meraki.org_id}'
                        for network in network_list:
                            msg_reply += f"\n{network['name']} {network['id']}"

                        msg.post_message(msg.room_id, msg_reply)

                    # '/meraki ssids' fetches SSIDs on the specified network.
                    # If network_id is not provided, use the predefined value.
                    elif action == 'ssids':
                        try:
                            network_id = msg.message_text.split()[2]
                        except IndexError:
                            network_id = meraki.def_network_id

                        ssid_list = meraki.get_ssids(network_id)

                        msg_reply = f'SSIDs for network {network_id}'
                        for ssid in ssid_list:
                            msg_reply += f"\n{ssid['number']} {ssid['name']}\
                                Enabled: {ssid['enabled']}"

                        msg.post_message(msg.room_id, msg_reply)

                    # '/meraki location' prints the last received
                    # location data of some clients
                    elif action == 'location':
                        try:
                            subaction = msg.message_text.split()[2]
                        except IndexError:
                            subaction = 'startscan'

                        if subaction == 'startscan':
                            msg_reply = meraki.start_scanning()
                        elif subaction == 'get':
                            msg_reply = json.dumps(meraki.get_location(), indent=4)

                        msg.post_message(msg.room_id, msg_reply)

                else:
                    msg.reply = f'Bot received message "{msg.message_text}"'
                    msg.post_message(msg.room_id, msg.reply)

                return data
        else:
            return ('Wrong data format', 400)



############## USER DEFINED SETTINGS ###############
# MERAKI SETTINGS
validator = "EnterYourValidator"
secret = "EnterYourSecret"
version = "2.0"
locationdata = "Location Data Holder"
####################################################
app = Flask(__name__)

# Respond to Meraki with validator


@app.route("/", methods=["GET"])
def get_validator():
    print("validator sent to: ", request.environ["REMOTE_ADDR"])
    return validator


# Accept CMX JSON POST


@app.route("/", methods=["POST"])
def get_locationJSON():
    global locationdata

    if not request.json or not "data" in request.json:
        return ("invalid data", 400)

    locationdata = request.json
    pprint(locationdata, indent=1)
    print("Received POST from ", request.environ["REMOTE_ADDR"])

    # Verify secret
    if locationdata["secret"] != secret:
        print("secret invalid:", locationdata["secret"])
        return ("invalid secret", 403)

    else:
        print("secret verified: ", locationdata["secret"])

    # Verify version
    if locationdata["version"] != version:
        print("invalid version")
        return ("invalid version", 400)

    else:
        print("version verified: ", locationdata["version"])

    # Determine device type
    if locationdata["type"] == "DevicesSeen":
        print("WiFi Devices Seen")
    elif locationdata["type"] == "BluetoothDevicesSeen":
        print("Bluetooth Devices Seen")
    else:
        print("Unknown Device 'type'")
        return ("invalid device type", 403)

    # Return success message
    return "Location Scanning POST Received"


@app.route("/go", methods=["GET"])
def get_go():
    return render_template("index.html", **locals())


@app.route("/clients/", methods=["GET"])
def get_clients():
    global locationdata
    if locationdata != "Location Data Holder":
        # pprint(locationdata["data"]["observations"], indent=1)
        return json.dumps(locationdata["data"]["observations"])

    return ""


@app.route("/clients/<clientMac>", methods=["GET"])
def get_individualclients(clientMac):
    global locationdata
    for client in locationdata["data"]["observations"]:
        if client["clientMac"] == clientMac:
            return json.dumps(client)

    return ""


# Launch application with supplied arguments


def main(argv):
    global validator
    global secret

    try:
        opts, args = getopt.getopt(argv, "hv:s:", ["validator=", "secret="])
    except getopt.GetoptError:
        print("locationscanningreceiver.py -v <validator> -s <secret>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("locationscanningreceiver.py -v <validator> -s <secret>")
            sys.exit()
        elif opt in ("-v", "--validator"):
            validator = arg
        elif opt in ("-s", "--secret"):
            secret = arg

    print("validator: " + validator)
    print("secret: " + secret)


if __name__ == "__main__":
    main(sys.argv[1:])
    app.run(host="0.0.0.0", port=5002, debug=False)
