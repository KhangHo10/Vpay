# 🎙️ VPay – Voice-Activated Payment System

A revolutionary **“cardless” payment method** that allows users to make purchases using only their **voice**.  
Built at **ShellHacks 2024** in just 36 hours!

---

## 🎯 Overview

**VPay** enables customers to walk into any store and complete transactions by simply **speaking to a payment terminal**.  
No phone, no card, just your voice.  

This innovative approach not only helps people who’ve forgotten their wallet or phone but also makes payments more accessible for individuals with **disabilities**.

---

## 💡 Inspiration

The idea for VPay came from a conversation with one of our teammate’s parents about how inconvenient it can be to forget your payment methods.  
While researching, we found that a university in China had implemented a **facial payment system**, which inspired us to take the concept even further by using **voice authentication** instead.

---

## ✨ Features

- 🎤 **Voice-Only Payments** – Complete transactions using natural voice commands  
- 🔐 **Secure Authentication** – Custom voice embedding system for user verification (Not fully implemented)
- 🧏 **Accessibility-Focused** – Designed to make payments more inclusive  
- ⚡ **Real-Time Processing** – Fast audio capture and backend processing  
- 💳 **Payment Simulation** – Integrated **Stripe API** to emulate real transactions  

---

## 🛠️ Tech Stack

### **Backend**
- Python  
- FastAPI – Web framework for backend routes  
- Uvicorn – ASGI server to run FastAPI  

### **AI & Voice System**
- Google ADK (Agent Development Kit) – For agent orchestration  
- Gemini 2.5 Flash – Large Language Model (LLM) used for natural language understanding  
- Speech Recognition – Converts audio to text  

### **Authentication & Payments**
- SQLite3 – Stores custom voice embeddings for authentication  
- Stripe API – Handles simulated payments  

### **Frontend**
- React – User interface framework  
- Tailwind CSS – Styling  
- JavaScript – Interactivity and logic  

### **Browser APIs**
- MediaRecorder – Captures voice input  
- getUserMedia – Accesses the user’s microphone  

---

## 🧠 Architecture Overview

1. **User speaks** a command like “Pay 20 dollars to Target.”  
2. **Frontend** captures the voice using MediaRecorder + getUserMedia.  
3. Audio is sent to the **backend (FastAPI)** via RESTful API.  
4. **Speech Recognition** converts it to text.  
5. **Google ADK** and **Gemini 2.5 Flash** parse the intent (amount, payee).  
6. The backend triggers **Stripe API** to simulate payment.  
7. Result is returned to the frontend and displayed in real-time.  

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+  
- Node.js and npm  
- Stripe API key  
- Google Cloud account with ADK access  

### **Installation**

```bash
# Clone the repository
git clone https://github.com/KhangHo10/Vpay.git
cd Vpay

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Create a .env file in the root directory
STRIPE_API_KEY=your_stripe_key
GOOGLE_ADK_KEY=your_google_adk_key

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Run the backend
uvicorn main:app --reload

# Run the frontend
npm start
```

## 👥 Team

- **Khang Ho**  
- **Zara Maraj**  
- **Haruki Horiuchi**  
- **Miguel Ávila**

---

## 🏆 Hackathon

Built in **36+ hours** at **ShellHacks 2024** — Florida’s largest hackathon!  
We learned, built, and collaborated through sleepless nights (and probably too much caffeine).  

