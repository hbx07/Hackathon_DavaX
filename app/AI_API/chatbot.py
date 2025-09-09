import openai
import speech_recognition as sr
import pyttsx3

def ask_gpt(prompt):
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "system", "content": "You are a helpful assistant for filling out payment forms."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

if __name__ == "__main__":
    # Example usage
    user_input = "I want to pay my electricity bill."
    ai_response = ask_gpt(user_input)
    print("AI Response:", ai_response)