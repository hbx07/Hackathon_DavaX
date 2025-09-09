import openai
import pyttsx3
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re
import tempfile
from pathlib import Path
import mimetypes
from openai import OpenAI

app = FastAPI()

# Allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_slots(message):
    slots = {}
    # Simple regex-based extraction for demo purposes
    # Card number
    card_match = re.search(r'(\d{4}[\s-]?){4}', message)
    if card_match:
        slots['card'] = card_match.group().replace('-', ' ').strip()
    # Expiry
    exp_match = re.search(r'(0[1-9]|1[0-2])[\/\-](\d{2,4})', message)
    if exp_match:
        slots['exp'] = exp_match.group()
    # CVV
    cvv_match = re.search(r'\b\d{3,4}\b', message)
    if cvv_match:
        slots['cvv'] = cvv_match.group()
    # Amount (RON/lei)
    amount_match = re.search(r'(\d+[.,]?\d*)\s*(RON|lei)', message, re.IGNORECASE)
    if amount_match:
        slots['amount'] = amount_match.group(1)
    # Receiver (company names, e.g. Electrica, Digi, E.ON)
    receiver_match = re.search(r'(Electrica|Digi|E\.ON|Enel|Orange|Vodafone)', message, re.IGNORECASE)
    if receiver_match:
        slots['receiver'] = receiver_match.group(1)
    return slots


def ask_gpt(prompt, form=None):
    system_message = "You are a helpful assistant for filling out payment forms. If the user provides payment details, extract them and return as slot values (card, exp, cvv, amount, receiver)."
    if form:
        system_message += f" Here is the current payment form state: Receiver: {form.get('receiver', '')}, Amount: {form.get('amount', '')}, Card: {form.get('card', '')}, Expiry: {form.get('exp', '')}, CVV: {form.get('cvv', '')}. Use this information to guide the user and help them complete the form."
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": prompt}]
    )
    reply = response.choices[0].message.content
    slots = extract_slots(prompt)
    return reply, slots


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

@app.post('/chat')
async def chat(request: Request):
    data = await request.json()
    prompt = data.get('message', '')
    form = data.get('form', None)
    if not prompt:
        return JSONResponse({'error': 'No message provided'}, status_code=400)
    try:
        reply, slots = ask_gpt(prompt, form)
        return {'reply': reply, 'slots': slots}
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

@app.post('/speech')
async def speech(audio: UploadFile = File(...)):
    try:
        # Save uploaded audio to a temp file with .wav extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(await audio.read())
            tmp.flush()
            tmp.seek(0)
            tmp_path = Path(tmp.name)
        # Detect MIME type
        mime, _ = mimetypes.guess_type(str(tmp_path))
        if not mime:
            mime = 'audio/wav'
        # Use OpenAI client for transcription
        client = OpenAI()
        with open(tmp_path, 'rb') as f:
            resp = client.audio.transcriptions.create(
                model='whisper-1',
                file=(tmp_path.name, f, mime),
                response_format='text'
            )
        text = getattr(resp, 'text', None)
        if isinstance(resp, str) and not text:
            text = resp
        return {"transcript": text.strip() if text else ""}
    except Exception as e:
        import traceback
        print("Whisper transcription error:", e)
        traceback.print_exc()
        return JSONResponse({'error': str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("chatbot:app", host="0.0.0.0", port=5000, reload=True)
