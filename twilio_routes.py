"""
Twilio IVR Call Handling System

This module manages the Twilio-powered Interactive Voice Response (IVR) system for the Voice Assistant.
It is responsible for handling incoming calls, verifying user identity, and guiding users through troubleshooting
and authentication processes. The system supports:

- **User Verification**: Extracts, cleans, and validates usernames, managers, and hire dates.
- **Voice Command Processing**: Collects user input via voice and converts it into text for validation.
- **Authentication Flow**: Implements multi-step authentication including username, manager verification,
  and hire date confirmation to ensure security.
- **Twilio Call Management**: Handles call recordings, transcriptions, and interactions with Twilio services.
- **Error Handling & Support Escalation**: Detects authentication failures and escalates cases by generating
  support tickets for IT intervention.
- **Dynamic Menu Navigation**: Guides users through troubleshooting options for SSO and token synchronization.

The module relies on Twilio’s TwiML for call responses and interacts with external services for decryption,
transcription, and verification.
"""

# === Import Section ===
import json
from twilio.twiml.voice_response import VoiceResponse
from flask import request, redirect, Response, jsonify
from models import User
import requests
from environment_variables import account_sid, auth_token
from decryption_utils import decrypt_recording
from whisper_transcription import transcribe_audio_content
from utils import linfo, generate_password_hasshed, get_usernames_by_country, clean_name, is_name_match, normalize_date_string, extract_username
from fuzzywuzzy import fuzz
from datetime import datetime

# Documentation URL for reference
DOC_URL = "https://docs.google.com/document/d/1d0pHqhfGcqEXIxVyAEIRGTWtFgOR3oUG7Ejx8Y3lrHw/edit?tab=t.j2t51v7h3lin"

# Global Variables
transcription_storage = {} # Store transcription by call_sid
verification_storage = {}  # Store verification info by call_sid


# === Helper Functions ===

def twiml(resp):
    """Wrap response in proper Twilio XML format"""
    resp = Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

def verify_user(username):
    print("\n=== Process user verification ===")
    print(f"Username received for verification: {username}")

    user_info = linfo(username)

    if user_info:
        print(f"Verification successful for username: {username}")
        print(f"Retrieved User Info: {user_info}")

        return {
            'status': 'success',
            'username': username,
            'user_info': user_info
        }
    else:
        country = request.values.get("FromCountry")
        print(f"calling from: {country}")
        username_list = get_usernames_by_country(country)
        print(f"username list: {username_list}")

        best_ratio = 0
        best_match = None

        for user in username_list:
            ratio = fuzz.ratio(username, user) 
            print(f"{username} vs {user} is: {ratio}")
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = user
                print( f" current best match is: {best_match}")
        print(f"Best fuzzy match: {best_match} with score: {best_ratio}")
        if best_ratio >= 85:
            user_info = linfo(best_match)
            return {
                'status': 'success',
                'username': best_match,
                'user_info': user_info
            }
        return {'status': 'fail'}
    
def verify_manager(user_answer, user_info):
    """Verifies if the manager's name matches the stored manager in the database.
    - First, it checks for an exact match.
    - If the names don't match exactly, it applies fuzzy matching.
    - Fuzzy matching allows small variations in spelling or minor differences (e.g., missing accents, slight typos).
    - If the similarity score is 90 or above, the verification is considered successful.
    """
    print("\n=== Process manager verification ===")
    name_in_ldap = user_info['manager'].lower()
    print(f"manager's name  received for verification: {user_answer}")
    print(f"manager's name  in LDAP: {name_in_ldap}")

    

    if user_answer != name_in_ldap:
        print("\n Transcription failed, start fuzzy matching ")

        if is_name_match(user_answer, name_in_ldap):
            print(f"Verification successful for : {user_answer}")
            return {'status': 'success'}    
        else:
            print(f"Verification failed: {user_answer} was not found in LDAP.")
            return {'status': 'fail'}     
    print(f"Verification successful for : {user_answer}")
    return {'status': 'success'}

    
def verify_hire_date(user_answer, user_info):
    print("\n=== Process user's hire date verification ===")
    hire_date_in_ldap = user_info['hire_date']
    print(f"Hire date received for verification: {user_answer}")
    print(f"Hire date in LDAP: {hire_date_in_ldap}")

    parsed_date_str = normalize_date_string(user_answer)
    print(f"Parsed date from user input: {parsed_date_str}")

    if not parsed_date_str:
        print("Date parsing failed.")
        return {'status': 'fail'}

    # Convert both to date objects
    parsed_date = datetime.strptime(parsed_date_str, "%Y-%m-%d").date()
    actual_date = datetime.strptime(hire_date_in_ldap, "%Y-%m-%d").date()

    # Allow ±2 days differences
    delta = abs((parsed_date - actual_date).days)
    if delta <= 2:
        print(f"Verification successful (delta {delta} days): {parsed_date_str}")
        return {'status': 'success'}
    else:
        print(f"Verification failed: {parsed_date_str} differs by {delta} days from LDAP.")
        return {'status': 'fail'}


outage = False

# === Twilio IVR Routes ===
def register_twilio_routes(app):
    """Registers all Twilio IVR routes in the Flask application"""

    @app.route('/ivr')
    def index():
        """Initial IVR entry point.
        - If there is an outage, the user hears a message about known service issues.
        - Otherwise, they are redirected to the welcome menu to begin troubleshooting.
        """
        response = VoiceResponse()
        if outage:
            response.say("Hello,Global Red Hatters,Welcome to the SSO Virtual Assistant." +
                         " Red Hat IT has confirmed an outage known to impact the following services:")
            response.pause(length=2)
            response.say("Internal Single Sign On (SSO) authentication")
            response.pause(length=2)
            response.say("All Red Hat Applications that utilize Internal SSO" +
                         "EST: {}. Thank you!")
        else:
            response.redirect('/ivr/welcome')


    @app.route("/ivr/welcome", methods=['GET', 'POST'])
    def welcome():
        """Provides an initial welcome message and instructions for troubleshooting."""
        response = VoiceResponse()
        with response.gather(num_digits=1, action='/ivr/welcome_menu', timeout=3, trimming="trim_silence", method="POST") as g:
           # g.say("Welcome to the SSO Troubleshooting Voice Assistant.")
           # g.pause(length=1)
           # g.say("Before we begin resolving the issue, here's a quick reminder:")
           # g.pause(length=1)
           # g.say("Kerberos Password: " +
            #    "It is at least 14 characters long and is the password you use when logging into your desktop for the first time after opening your laptop")
            #g.pause(length=1)    
            #g.say("PIN + Token: A 6-digit PIN combined with a one-time password generated by your OTP app")
            #g.pause(length=1)  
            #g.say("For logging into your desktop, please enter your Kerberos password")
            #g.pause(length=1)
            #g.say(" For logging into Red Hat applications (like your Red Hat email account or Rover), please enter your PIN + token")
            #g.pause(length=1)
            g.say("If this resolves your issue, press 0")
            g.pause(length=1)
            g.say("If not, press 1 to continue")
            

        return twiml(response)

    @app.route("/ivr/welcome_menu", methods=['POST'])
    def welcome_menu():
        """Handles menu selection from the welcome message."""
        selected_option = request.form.get('Digits')
        print(f"selected option: {selected_option}")
        response = VoiceResponse() #Create response object

        if core_ivr_responses(selected_option, response):
            return twiml(response)
    
        option_action = {"0": end_call,
                         "1": continue_ts}
        if selected_option in option_action.keys():          
            option_action[selected_option](response) #use the response object
        else:
            response.redirect('/ivr/welcome') # If no valid option selected, redirect to welcome
        
        return twiml(response)

        
    @app.route('/ivr/main_menu', methods=['POST'])
    def main_menu():
        selected_option = request.form.get('Digits')
        print(f"selected option: {selected_option}")
        response = VoiceResponse()
        option_actions = {"1": out_of_sync,
                          "4": otp_app_issue}
        if selected_option in option_actions.keys(): 
            option_actions[selected_option](response)
        else:
            continue_ts(response)

        return twiml(response)

    @app.route("/ivr/sync_menu", methods=['POST'])
    def sync_menu():
        selected_option = request.form.get('Digits')
        print(f"selected option: {selected_option}")
        response = VoiceResponse()

        if core_ivr_responses(selected_option, response, resync_token):
            return twiml(response)

        option_action = {'4': resync_token,
                        '5':send_kb,
                        '9':temporary_token}
        if selected_option in option_action:         
            option_action[selected_option](response)
        else:
            # No digits received, repeat out-of-sync steps
            out_of_sync(response)

        return twiml(response)
    
    @app.route("/ivr/vpn_access_menu", methods=["POST"])
    def vpn_access_menu():
        selected_option = request.form.get('Digits')
        print(f"selected option: {selected_option}")
        response = VoiceResponse()

        if selected_option:
            option_action = {'4': login_steps,
                            '9':temporary_token}
            if selected_option in option_action:         
                option_action[selected_option](response)
            elif core_ivr_responses(selected_option, response, login_steps):
                return twiml(response)

        else:
            response.say("No input detected. Let's try again.")
            otp_app_issue(response)# No digits received, repeat out-of-sync steps
      
        return twiml(response)
    

        
    @app.route('/ivr/recording_status', methods=['POST'])
    def recording_status():
        """Handle recording status callbacks from Twilio"""
        global transcription_storage

        print("\n=== Recording Status Called ===")
       # print("Full request:", dict(request.values))

        recording_sid = request.values.get('RecordingSid')
        recording_status = request.values.get('RecordingStatus')
        recording_url = request.values.get('RecordingUrl')
        encryption_details = request.values.get('EncryptionDetails')
        call_sid = request.values.get('CallSid')

        #print(f"Recording Status: {recording_status}")
        #print(f"Recording SID: {recording_sid}")
        #print(f"Call SID: {call_sid}")
        #print(f"Recording URL: {recording_url}")

        if not recording_status:
            print("No recording status received")
            return jsonify({'status': 'no-status'}), 200

        if recording_status == 'in-progress':
            print("Recording in progress...")
            return jsonify({'status': 'in-progress'}), 200

        if recording_status == 'completed':
            try:
                print("Processing completed recording...")
                
                if not recording_url:
                    raise ValueError("Missing recording URL")
                
                # Parse encryption details
                if encryption_details:
                    encryption_json = json.loads(encryption_details)
                    encrypted_cek = encryption_json.get('encrypted_cek')
                    iv = encryption_json.get('iv')
                else:
                    print("No encryption details provided.")
                    encryption_json = {}
            

                # Download recording
                auth = (account_sid, auth_token)
                print(f"Downloading recording from {recording_url}")
                recording_response = requests.get(recording_url, auth=auth)

                if recording_response.status_code != 200:
                    raise Exception(f"Failed to download recording: {recording_response.status_code}")

                audio_content = recording_response.content
                print(f"Downloaded audio size: {len(audio_content)} bytes")
                
                encrypted_audio = recording_response.content
                decrypted_content = decrypt_recording(encrypted_audio, encrypted_cek, iv)

                try:
                    # First try actual transcription                  
                    transcribed_text = transcribe_audio_content(decrypted_content)
                    print(f"Whisper transcription result: {transcribed_text}")
                    
                    if transcribed_text and len(transcribed_text.strip()) > 0:
                        # Use the real transcription
                        final_text = transcribed_text
                    else:
                        # Fallback to test value if transcription fails
                        print("Transcription failed or empty, using fallback value")
                        final_text = "sleving"      
                except Exception as trans_error:
                    # If transcription fails, log it and use fallback
                    print(f"Transcription error: {str(trans_error)}")
                    print("Using fallback value")
                    final_text = "sleving"
                # Store the result
                transcription_storage[call_sid] = final_text
                print(f"Stored in transcription_storage for CallSid: {call_sid}")
                print(f"Current transcription_storage: {transcription_storage}")

                return jsonify({
                    'status': 'success',
                    'transcription': final_text
                }), 200
            except Exception as e:
                print(f"Error in recording status: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        if recording_status == 'failed':
            error_code = request.values.get('ErrorCode')
            print(f"Recording failed with error code: {error_code}")
            return jsonify({
                'status': 'error',
                'message': f'Recording failed with error code: {error_code}'
            }), 400

        return jsonify({
            'status': recording_status
        }), 200
    

    # === Authentication Flow Routes ===

    @app.route('/ivr/process_username', methods=['POST'])
    def process_username():
        """Process the username after recording and verify user"""
        print("\n=== Process the username ===")

        global verification_storage
        response = VoiceResponse()
        call_sid = request.values.get('CallSid')

        print(f"Call SID from request: {call_sid}")
        print(f"All stored Call SIDs: {list(transcription_storage.keys())}")

        
        # Get transcription and verify user
        transcribed_text = transcription_storage.get(call_sid)
        extracted_username = extract_username(transcribed_text)
        cleaned_username = clean_name(extracted_username)
        print(f"cleaned username is: {cleaned_username}")
        if cleaned_username:
            result = verify_user(cleaned_username)
            if result['status'] == 'success':
                verification_storage[call_sid] = {
                    'username': result['username'],
                    'user_info': result['user_info']
                }

                # Proceed to manager verification
                response.say(f"Thank you {result['user_info']['first_name']}, for second authentication, please tell me your manager's name and press # when finish")
                response.record(
                    action='/ivr/process_manager',
                    finishOnKey='#',
                    recordingStatusCallback='/ivr/recording_status',
                    recordingStatusCallbackEvent='completed',
                    timeout=10,
                    playBeep=True,
                    trim='trim-silence'
                )
            else:
                response.say("Username not found. Please try spelling it out.")
                temporary_token(response)
        else:
            response.say("Thank you. Please hold while I process your answer.")
            # Add small delay and redirect once
            response.pause(length=10)
            response.redirect('/ivr/process_username')

        transcription_storage.pop(call_sid, None)
        return twiml(response)
    
    @app.route('/ivr/process_manager', methods=['POST'])
    def process_manager():
        call_sid = request.values.get('CallSid')
        user_data = verification_storage.get(call_sid)
        response = VoiceResponse()

        print("\n=== Process Manager's name ===")
        print(f"Call SID from request: {call_sid}")
        print(f"Verification Storage: {verification_storage}")

        # Get transcription using same CallSid
        transcribed_text = transcription_storage.get(call_sid)
        print(f"Retrieved transcription: {transcribed_text}")  

        cleaned_manager_name = clean_name(transcribed_text, remove_spaces=False)

        if cleaned_manager_name:
            result = verify_manager(cleaned_manager_name, user_data['user_info'])
            if result['status'] == 'success':
                print("Manager verification successful.")
                with response.gather(num_digits=1, action='/ivr/receive_token', timeout=10, trimming="trim_silence", method="POST") as g:
                    g.say("That is correct")
                    g.pause(length=1)
                    #g.say("To receive a temporary token via a 'Bitwarden' link, which can only be viewed once " + 
                    #   ", sent to your private email account, please press 1 ")
                    g.pause(length=1)
                    g.say("To receive the temporary token immediately, by voice, press 4")
                    g.pause(length=1)
                    g.say("To hear your options again, press 3")

                return twiml(response) 
            else:
                print("Manager verification failed. Asking for hire date.")
                response.say("I'm sorry, that is incorrect. Let's try one more step.")
                response.pause(length= 1)
                response.say("Please say your hiring date clearly. For example: February 1st, 2022. Then press '#' when finished.")
                response.record(
                    action='/ivr/process_hire_date',  
                    finishOnKey='#',
                    recordingStatusCallback='/ivr/recording_status',  
                    recordingStatusCallbackEvent='completed',
                    timeout=10,
                    playBeep=True,
                    trim='trim-silence'
                )
                transcription_storage.pop(call_sid, None)   
                return twiml(response)
        else:
            response.say("Please hold while I process your answer.")
            # Add small delay and redirect once
            response.pause(length=10)
            response.redirect('/ivr/process_manager')

        transcription_storage.pop(call_sid, None)
        return twiml(response)

    @app.route('/ivr/process_hire_date', methods=['POST'])
    def process_hire_date():
        call_sid = request.values.get('CallSid')
        user_data = verification_storage.get(call_sid)
        response = VoiceResponse()

        print("\n=== Process hire date ===")
        print(f"Call SID from request: {call_sid}")
        print(f"Verification Storage: {verification_storage}")

        transcribed_text = transcription_storage.get(call_sid)
        print(f"Retrieved transcription: {transcribed_text}")

        if transcribed_text:
            result = verify_hire_date(transcribed_text, user_data['user_info'])

            if result['status'] == 'success':
                with response.gather(num_digits=1, action='/receive_token', timeout=3, trimming="trim_silence", method="POST") as g:
                    g.say("That is correct")
                    g.pause(length=1)
                    g.say("To receive a temporary token via a 'Bitwarden' link, which can only be clicked once, sent to your private email account, please press 1")
                    g.pause(length=1)
                    g.say("To receive the temporary token immediately, by voice, press 4") 
                    g.pause(length=1)
                    g.say("To hear your options again, press 3.")  
                return twiml(response)                
            else:
                response.say("That is incorrect. Authentication failed. A ticket has been opened and an IT agent will contact you in the next 20 minutes.")
                open_ticket(response)
                transcription_storage.pop(call_sid, None) 
                return twiml(response) 
        else:
            response.say("Thank you. Please hold while I process your answer.")
            print("Transcription not ready yet. Pausing and retrying...")
            response.pause(length=10)
            response.redirect('/ivr/process_hire_date')
            return twiml(response)     
        

    @app.route('/ivr/receive_token', methods=['POST'])
    def receive_token():
        selected_option = request.form.get('Digits')
        response = VoiceResponse() 

        if core_ivr_responses(selected_option, response, say_temptoken):
            return twiml(response)
    
        option_action = {"1": temptoken_bitwarden,
                         "4": say_temptoken                      
                        }
        if selected_option in option_action.keys():          
            option_action[selected_option](response) 
        else:
            say_temptoken # If no valid option selected
        
        return twiml(response)

        # Test routes for verification flow


    return app


# Common actions that can be called from any menu
def core_ivr_responses(option, response,current_menu=None):
    actions = {
        "0": end_call,        # End call
        "2": open_ticket,     # Open support ticket
        "3": repeat_steps
    }
    if option in actions:
        return actions[option](response,current_menu)
    return False

# Helper function to end the call
def end_call(response):
    response.say("Thank you for calling the SSO login Virtual Assistant")
    response.hangup()
    return response

# Helper function to open a support ticket
def open_ticket(response):
    caller_data =dict(request.values)
    phone_number = caller_data['']
    response.say("ticket: [INC*****] created. an agent will contact you soon")
    response.pause(length=2)
    # creating a ticket at servicenow
    response.hangup()
    return response

# Helper function to repeat current steps
def repeat_steps(response, menu_function):
    response.say("I'll repeat the instructions.")
    menu_function(response)
    return response
    
#welcome_menu methods    

def continue_ts(response):
    with response.gather(num_digits=1, action='/ivr/main_menu', timeout=3, trimming="trim_silence", method="POST") as g:
        g.say("If you haven't logged in to your redhat account for over 4 days, and your usual token isn't working," +
              " it might be out of sync.")
        g.pause(length=1)
        g.say("to resync it please Press 2.")
        g.pause(length=2)
        g.say("If you've gotten a new phone, or reinstalled your OTP app, or don't have access to your Kerberos password, press 4.")
    return response

# main_menu methods
def out_of_sync(response):
    with response.gather(num_digits=1, action='/ivr/sync_menu', timeout=5, trimming="trim_silence", method="POST") as g:
        g.say("Lets resync your token!" +
              "from your browser, navigate to token.redhat.com." +
              "Log in using your Red Hat username and Kerberos password. ")
        g.pause(length=5)
        g.say("If you've successfully logged into token.redhat.com website, press 4 to proceed with the token resync." +
              "if you'd like to get this instruction sent to this phone number, press 5" +
              "If you've forgotten your Kerberos password and are unable to log in to token.redhat.com," +
               " press 9 to receive a temporary token."+
               " To repeat the steps, press 1.")

    return response
    
    

# sync_menu methods
def resync_token(response):
    with response.gather(num_digits=1, action='/ivr/sync_menu', timeout=5, trimming="trim_silence", method="POST") as g:
        g.say("at token.redhat.com:" + 
              " From the list of tokens, click the serial number of the token you want to resync." + 
              " In your OTP app, press the button on your token to display the next token code." + 
              " Enter the generated token in the field labeled Enter first OTP value." + 
              " Press the button again and enter the next code in the Enter second OTP value field." + 
              " Click Resync Token.")
        g.pause(length=5)
        g.say("If resyncing the token does not resolve the issue," +
              " try setting the PIN using the option beneath Resync Token at token.redhat.com.")
        g.pause(length=3)
        g.say(" If this resolves your issue, press 0." +
              " To repeat the steps, press 1." + 
              " For assistance from a live IT agent and to open a support ticket, press 3.")
    return twiml(response)
 
        
def otp_app_issue(response):
    with response.gather(num_digits=1, action='/ivr/vpn_access_menu', timeout=5, trimming="trim_silence", method="POST") as g:
        g.say("If you've got a new phone, but still have access to your old phone and the VPN, press 4." )
        g.pause(length=1)
        g.say( " If you're locked out of the VPN and no longer have access to your current token, press 9, to receive a temporary token.")
        g.pause(length=1)
        g.say("To repeat the steps, press 1.")
    return response


def send_kb(response):
    pass



def login_steps(response):
        with response.gather(num_digits=1, action='/ivr/vpn_access_menu', timeout=5, trimming="trim_silence", method="POST") as g:
            g.say("Please connect to the VPN using your PIN + Token (using your old phone).")
            g.pause(length=2)
            g.say("To set up a new PIN + Token, go to help.redhat.com and search for: 'Set up a FreeOTP Soft Token at token.redhat.com.' Follow the guide to set up a new PIN + Token. ")
            g.pause(length=1)
            g.say("If this resolves your issue, press 0.") 
            g.pause(length=1)
            g.say(" To repeat the steps press 3 ")
            g.pause(length=1)
            g.say("For assistance from a live IT agent, please open a ticket at redhat.help.com.")
        return response

def temporary_token(response):
    
    response.say("please provide your username and press # when finish.")
    response.record(
        action="/ivr/process_username",
        finishOnKey='#',
        recordingStatusCallback="/ivr/recording_status",
        recordingStatusCallbackMethod='POST',
        recordingStatusCallbackEvent='completed',  
        timeout=10,
        playBeep=True,
        trim='trim-silence'
    )
    return response



def temptoken_bitwarden():
    pass

def say_temptoken(response):
    print("\n=== say_temptoken called ===")
    call_sid = request.values.get('CallSid')
    user_data = verification_storage.get(call_sid)

    if not user_data:
        response.say("We couldn't verify your session. Please try again.")
        return twiml(response)

    
    uid = User.query.get(user_data['user_info']["uid"])
    print(f"start generating temporary token for {uid}")


    # Generate token if not present
    if 'temp_token' not in verification_storage[call_sid]:
        temp_token = generate_password_hasshed(uid)
        print(f"temporary token is: {temp_token}")
        verification_storage[call_sid]['temp_token'] = temp_token
    else:
        temp_token = verification_storage[call_sid]['temp_token']

    response.say("Please write down your temporary token. It will be read slowly.")
    response.pause(length=2)

    for char in temp_token:
        response.say(char)
        response.pause(length=1.5)  # slower pace for clarity

    with response.gather(num_digits=1, action='/ivr/receive_token', timeout=10, trimming="trim_silence", method="POST") as g:
        g.say("This temporary token is valid for 3 hours.")
        g.pause(length=1)
        g.say("If you managed to log in using this token, press 0.")
        g.pause(length=1)
        g.say("To hear the token again, press 3.")
        g.pause(length=1)
        g.say("To speak to an IT agent, press 2.")

    return twiml(response)

