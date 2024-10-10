import os
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import openai
import requests

pip install google-cloud-speech

from google.cloud import speech_v1p1beta1 as speech
import io

# Set up your API keys
openai.api_key = 'your_openai_api_key'
twilio_account_sid = 'your_twilio_account_sid'
twilio_auth_token = 'your_twilio_auth_token'
client = Client(twilio_account_sid, twilio_auth_token)

# List of tenant phone numbers
tenant_numbers = ['+1234567890', '+0987654321']

def transcribe_audio(audio_url):
    response = requests.get(audio_url)
    audio_data = response.content
    # Use a speech-to-text API to transcribe the audio
    # Example: Google Speech-to-Text or AssemblyAI
    transcript = "Transcribed text from audio"
    return transcript

def transcribe_audio_google(audio_url):
    client = speech.SpeechClient()
    
    response = requests.get(audio_url)
    audio_data = response.content
    
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    
    transcript = ""
    for result in response.results:
        transcript += result.alternatives.transcript
    
    return transcript

def analyze_intent(transcript):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Determine the intent of this call: {transcript}",
        max_tokens=50
    )
    intent = response.choices.text.strip()
    return intent

def handle_call(call_sid, from_number):
    call = client.calls(call_sid).fetch()
    audio_url = call.recordings.list().uri
    transcript = transcribe_audio(audio_url)
   #transcript = transcribe_audio_google(audio_url)
    intent = analyze_intent(transcript)
    
    response = VoiceResponse()
    if "urgent" in intent:
        response.say("Please hold while I connect you to the landlord.")
        response.dial("+1234567890")  # Your phone number
    else:
        response.say("Thank you for your call. We will get back to you soon.")
    
    return str(response)

# Example Twilio webhook endpoint
from flask import Flask, request

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def voice():
    call_sid = request.form['CallSid']
    from_number = request.form['From']
    
    if from_number in tenant_numbers:
        response = handle_call(call_sid, from_number)
    else:
        response = VoiceResponse()
        response.say("This number is not recognized. Please contact the landlord directly.")
    
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
