# If you don't have BOLTIOT package TYPE the below code in your terminal
#
#
# pip3 install boltiot
#
#
# If you don't have KIVY package TYPE the below code in your terminal
#
#
# pip3 install kivy
#
#
import json
import time
from boltiot import Sms, Bolt, Email
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.widget import *

import conf  # Make sure conf.py is stored in the same folder.

# The below code is to store data from the conf.py file
# the credentials needed to connect to the {bolt Wi-Fi module, twilio account, mailgun account} in a local variable
my_bolt = Bolt(conf.bolt_api_key, conf.device_id)
sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
mailer = Email(conf.MAILGUN_API_KEY, conf.SANDBOX_URL, conf.SENDER_EMAIL, conf.RECIPIENT_EMAIL)

# The below code is to create the GUI of the kivy application that we are creating
Builder.load_string('''<MyGrid>
    name:"main"
    secret:secret
    lb:lb
    GridLayout:
        cols:1
        size:root.width-100,root.height-100
        pos:50,50
        Label:
            id:lb
            text:"MORSE CODE"
            size:100,10
        TextInput:
            multiline: True
            id:secret

        Button:
            text:"SEND"
            on_press:root.btn()
''')


# THE BELOW FUNCTION IS USED TO CONVERT THE USER INPUT TO MORSE CODE.
def to_morse(text):
    a = text.lower()
    morse_dict = {"a": ".- ", "b": "-... ", "c": "-.-. ", "d": "-.. ", "e": ". ", "f": "..-. ", "g": "--. ",
                  "h": ".... ", "i": ".. ", "j": ".--- ", "k": "-.- ", "l": ".-.. ", "m": "-- ", "n": "-. ",
                  "o": "--- ", "p": ".--. ", "q": "--.- ", "r": ".-. ", "s": "... ", "t": "- ", "u": "..- ",
                  "v": "...- ", "w": ".-- ", "x": "-..- ", "y": "-.-- ", "z": "--.. ", " ": "/ ", ",": "--..-- ",
                  ".": ".-.-.- ", "/": "-..-. ", ":": "---... ", "!": "-.-.-- ", "@": ".--.-. ", "1": ".---- ",
                  "2": "..--- ", "3": "...-- ", "4": "....- ", "5": "..... ", "6": "-.... ", "7": "--... ",
                  "8": "---.. ", "9": "----. ", "0": "----- ", "&": ".-... ", "(": "-.--. ", ")": "-.--.- ",
                  "+": ".-.-. ", "=": "-...- ", "?": "..--.. ", "-": "-....- ", "\n": "\n", "\t": "\t"}
    final = ""
    for i in a:
        final = final + morse_dict[i]
    return final


# THE BELOW CODE IS TO CREATE A WIDGET USING KIVY.


class MyGrid(Widget):
    secret = ObjectProperty(None)

    # The below code is called when the button in pressed.

    def btn(self):
        # Below code gets the text message and converts it to morse code.
        code = to_morse(self.secret.text)
        print(code)
        try:
            # The below code will send SMS to the receiver.
            response = sms.send_sms("The morse code will be transmitted in a minute")
            print("Response received from Twilio is: " + str(response))
            print("Status of SMS at Twilio is :" + str(response.status))
            # The below code will send EMAIL to the receiver.
            response = mailer.send_email("Alert", "The morse code will be transmitted in a minute")
            response_text = json.loads(response.text)
            print("Response received from Mailgun is: " + str(response_text['message']))
        except Exception as e:
            print("Error occurred: Below are the details")
            print(e)
        time.sleep(60)  # Wait for 60 seconds for the receiver to notice the morse code.
        response = 0
        # Transmits every character in the morse code to the bolt Wi-Fi module.
        for j in code:
            time.sleep(0.03)
            if j == ' ':
                time.sleep(0.2)  # The gap between letters is 1 unit tine.
            elif j == '/':
                time.sleep(1)  # The gap between words is 7 units time.
            else:
                if j == '-':
                    my_bolt.digitalWrite('0', 'HIGH')  # Turns on the buzzer and led.
                    time.sleep(0.3)  # dah lasts for 3 units time.
                    response = my_bolt.digitalWrite('0', 'LOW')  # Turns off the buzzer and led.

                elif j == '.':
                    my_bolt.analogWrite('0', 240)  # Turns on the buzzer and led and reduces its intensity..
                    # for further differentiation
                    time.sleep(0.001)  # dot lasts for 1 unit time.
                    response = my_bolt.digitalWrite('0', 'LOW')  # Turns off the buzzer and led.
        print("Message transmission is " + str(response))
        if response[-2] == 0:
            time.sleep(5)  # If message is ot transmitted it waits for 5 seconds and closes the kivy widget.
            exit()


class morse(App):
    def build(self):
        return MyGrid()  # This open/start the kivy App.


if __name__ == "__main__":
    morse().run()
