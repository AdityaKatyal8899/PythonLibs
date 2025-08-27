import speech_recognition as SR
from langdetect import detect, detect_langs
from gtts import gTTS

def take_voice_note():
    recognizer = SR.Recognizer()
    print("🎙 Speak now...")

    try:
        with SR.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

        print("🔄 Processing...")
        text = recognizer.recognize_google(audio)

        print("✅ You said:", text)
        print("🌍 Language detected:", detect_langs(text))

        speech = gTTS(text=text)
        speech.save("output.mp3")

    except SR.UnknownValueError:
        print("❌ Could not understand the audio")
    except SR.RequestError as e:
        print(f"❌ API request error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")


if __name__ == "__main__":
    while True:
        take_voice_note()
        a = input("\nRun again? (Y/N): ").strip().lower()
        if a == "y":
            continue
        elif a == "n":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid input, exiting...")
            break
