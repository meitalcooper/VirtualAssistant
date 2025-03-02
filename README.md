# VirtualAssistant

## 📌 Overview
VirtualAssistant is an interactive **voice-based assistant** designed to handle user authentication and troubleshooting via **Twilio IVR (Interactive Voice Response)**. It integrates **OpenAI Whisper** for speech-to-text transcription, processes encrypted call recordings, and interacts with a structured **Flask API**.

## 🚀 Features
- **IVR System with Twilio:** Handles voice calls, authentication, and troubleshooting.
- **Whisper Speech Recognition:** Converts voice recordings to text for verification.
- **User Authentication:** Verifies identity using usernames, manager names, and hire dates.
- **Secure Encrypted Recordings:** Decrypts and processes Twilio call recordings.
- **Dynamic Response Flow:** Uses fuzzy matching to handle variations in responses.
- **Flask API Backend:** Manages requests, authentication, and transcriptions.

## 📂 Project Structure
```
VirtualAssistant/
│── app.py                    # Flask application setup
│── models.py                 # Database models
│── twilio_routes.py          # Twilio IVR handling
│── whisper_transcription.py  # Whisper transcription logic
│── utils.py                  # Helper functions
│── decryption_utils.py       # Audio decryption
│── README.md                 # Project documentation
```

## 🛠️ Installation
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/meitalcooper/VirtualAssistant.git
cd VirtualAssistant
```

### **2️⃣ Create a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file and add:
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### **5️⃣ Run the Application**
```bash
flask run
```

## 🎙️ How It Works

### 📊 IVR Workflow Diagram
Below is the IVR system workflow illustrating the authentication and troubleshooting process:

*The original flowchart has been removed to maintain the privacy and confidentiality of internal company processes.*

1. **System Checks for Outages:** If an outage is detected, the caller is notified and the call ends.
2. **User Calls & Reaches Virtual Assistant:** The IVR system starts troubleshooting using a simple dial pad.
3. **Troubleshooting & Authentication Requirement:** If the user requires a temporary token, authentication is necessary.
4. **Verification:**
   - The system validates the username and manager name.
   - If additional verification is needed, the hire date is requested.
5. **Decision Process:**
   - ✅ If authentication is successful, the user receives a temporary access token.
   - ❌ If authentication fails, the case is escalated to IT support.
6. **Logging & Secure Communication:** The call, transcription, and access decisions are logged securely.
   
This structured process ensures an automated and secure way to verify users and provide necessary troubleshooting steps.

## 🔗 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ivr/welcome` | `POST` | IVR welcome message |
| `/ivr/process_username` | `POST` | Processes username input |
| `/ivr/process_manager` | `POST` | Verifies manager name |
| `/ivr/recording_status` | `POST` | Handles call recording and transcription |

## 🛡️ Security
- **Data Encryption:** Ensures sensitive data is encrypted before processing.
- **Access Control:** Uses Twilio authentication for secure communication.
- **Error Handling:** Logs and manages unexpected issues gracefully.


## 📜 License
This project is **proprietary and not open for public use or distribution**. Unauthorized copying, modification, or distribution is prohibited.

---

