def speech2text(recognizer, source):
    # recognize speech using Google Speech Recognition
    audio = recognizer.listen(source)
    return recognizer.recognize_google(audio)
