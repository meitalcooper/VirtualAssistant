import os
from twilio.rest import Client
from time import sleep

print("Starting test...")

account_sid = os.environ.get("TWILIOS_ACCOUNT_SID")
auth_token = os.environ.get("TWILIOS_AUTH_TOKEN")


print(f"Account SID: {account_sid}")
print(f"Auth Token present: {'Yes' if auth_token else 'No'}")

client = Client(account_sid, auth_token)



try:
    print("Initiating call...")
    # Simplified call creation matching the successful call configuration
    call = client.calls.create(
        to="{YOUR_NUMBER}",
        from_="+16205091768",
        url="https://4243-89-138-72-52.ngrok-free.app/ivr/vpn_access_menu"
    )
    print(f"Call initiated with SID: {call.sid}")
    

    # Monitor call status
    print("Monitoring call status...")
    for _ in range(10):
        current_call = client.calls(call.sid).fetch()
        print(f"Call status: {current_call.status}")
        if current_call.status in ['completed', 'failed', 'busy', 'no-answer']:
            print(f"Final call status: {current_call.status}")
            break
        sleep(2)
    
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {str(e)}")
    
