# VirtualAssistant

## 📌 Overview
VirtualAssistant is an interactive **voice-based assistant** designed to handle user authentication and troubleshooting via **Twilio IVR (Interactive Voice Response)**. It integrates **OpenAI Whisper** for speech-to-text transcription, processes encrypted call recordings, and interacts with a structured **Flask API**.

## 🚀 Features
- **IVR System with Twilio:** Handles voice calls, authentication, and troubleshooting flows.
- **Whisper Speech Recognition:** Converts voice recordings to text for verification.
- **User Authentication:** Verifies identity using usernames, manager names, and hire dates.
- **Soundex Phonetic & Fuzzy Matching:** New phonetic layer (`utils.is_name_match`) catches variations in spoken names.
- **Sentence Extraction Helper:** `extract_username()` strips fillers like *“my username is … uh …”* and returns a clean username before validation.
- **UID-Based Record Lookup:** Once verified, the user’s UID is cached so later steps fetch the DB record with `User.query.get(uid)` .
- **Secure Encrypted Recordings:** Decrypts Twilio AES-GCM recordings (RSA-OAEP unwrap of CEK) before transcription.
- **Dynamic Response Flow:** Uses fuzzy + phonetic matching to handle variations in caller responses.
- **Large Test Dataset:** `users_info_data.py` seeds > 700 culturally diverse users for realistic testing.
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
### **5️⃣ Initialize & Populate the Database**
flask db upgrade            # create tables
python users_info_data.py   # seed test users

### **6️⃣ Run the Application**
```bash
flask run
```

## 🎙️ How It Works

### 📊 IVR Workflow Diagram
Below is the IVR system workflow illustrating the authentication and troubleshooting process:

![IVR Workflow](IVR-workflow.png)

1. **System Checks for Outages:** If an outage is detected, the caller is notified and the call ends.
2. **User Calls & Reaches Virtual Assistant:** The IVR system starts troubleshooting using a simple dial pad.
3. **Troubleshooting & Authentication Requirement:** If the user requires a temporary token, authentication is necessary.
4. **Verification:**
   - **Username** → Whisper → extract_username → fuzzy check.
   - **Manager Name** → Soundex & fuzzy check.
   - **Hire Date** → Natural-language parsing with ±2-day tolerance.
5. **Decision Process:**
   - ✅ Successful → caller receives a one-time temporary token (voice or Bitwarden).
   - ❌  Failure → a ServiceNow ticket is opened and the call is routed to IT.
6. **Logging & Secure Communication:**  All calls, transcriptions, and authentication outcomes are logged securely.

## 🧪 Example Test Case
We have successfully tested the full authentication flow with diverse cultural datasets. [cite_start]The specific test case below demonstrates the system verifying user **Moshe Levin** (UID: 57)[cite: 45].

<details>
  <summary><strong>🔍 Click to expand: View a successful execution log</strong></summary>

  ### Test Scenario: Full Voice Authentication
  In this run, the system performs the following real-time operations:
  1. [cite_start]**Secure Decryption:** Decrypts the raw Twilio audio recording (`Starting Decryption Process`)[cite: 28].
  2. [cite_start]**Transcription:** Uses Whisper to transcribe the spoken username *"alevin"* and manager *"Michelle Cannon"*[cite: 35, 58].
  3. [cite_start]**Verification:** Matches the inputs against the database (fuzzy match: `alevin` ≈ `Moshe Levin`)[cite: 43, 44].
  4. [cite_start]**Success:** Retrieves user info and prepares the temporary token[cite: 45].

  ![Test Execution Logs](test-execution.jpg)

</details>

This structured process ensures an automated and secure way to verify users and provide necessary troubleshooting steps.

## 🔗 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ivr/welcome` | `POST` | IVR welcome message |
| `/ivr/process_username` | `POST` | Processes username input |
| `/ivr/process_manager` | `POST` | Verifies manager name |
| `/ivr/process_hire_date` | `POST` | Confirms hire date |
| `/ivr/recording_status` | `POST` | Handles encrypted recording → decrypt → Whisper |
| `/ivr/receive_token` | `POST` | Delivers temporary token; handles repeat/close/ticket |


## 🛡️ Security
- **AES-256-GCM Decryption:** Twilio media decrypted locally; CEK unwrapped with **RSA-OAEP-SHA-256**.
- **Bcrypt Password Hashing:** Temporary tokens hashed before DB commit
- **Access Control:** Twilio request validation + environment token checks.
- **Robust Error Handling:** Graceful fallback and logging for transcription or DB errors.


## 📜 License
This project is **proprietary and not open for public use or distribution**. Unauthorized copying, modification, or distribution is prohibited.

---

