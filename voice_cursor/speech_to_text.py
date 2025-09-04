import speech_recognition as sr

r = sr.Recognizer()

def speech_to_text():
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source, timeout=10)
        print("Processing audio...")

    converted_text = ""
    try:
        converted_text = r.recognize_google(audio)
        print("You said: " + converted_text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return converted_text

# speech_to_text()