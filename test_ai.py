import google.generativeai as genai

# 1. Apni Gemini API Key yahan dhyan se paste karein
API_KEY = "AIzaSyD483-YLCG5lF1Bntkiow147HyDHcUjTAY" 

genai.configure(api_key=API_KEY)

# 2. Model setup
model = genai.GenerativeModel('gemini-1.5-flash')

def test_chat():
    try:
        print("AI se connect ho raha hoon...")
        # Ek simple sawaal puch kar check karte hain
        response = model.generate_content("Hello, kya tum kaam kar rahe ho?")
        
        if response.text:
            print("✅ Success! AI ka jawab hai:")
            print(response.text)
        else:
            print("⚠️ AI ne koi text nahi bheja.")
            
    except Exception as e:
        print(f"❌ Error mila: {e}")

if __name__ == "__main__":
    test_chat()
