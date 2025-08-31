import speech_recognition as SR
from langdetect import detect_langs
from gtts import gTTS
import os
from tkinter import Tk, filedialog, simpledialog


# ------------------ Saver ------------------
def speech_saver(script):
    """Save given text as MP3 or TXT file depending on user dialog."""
    saved_file = get_save_path_gui_file()
    if not saved_file:
        return False

    if saved_file.endswith(".mp3"):
        speech = gTTS(text=script)
        speech.save(saved_file)
    elif saved_file.endswith(".txt"):
        with open(saved_file, "w", encoding="utf-8") as f:
            f.write(script)
    else:
        return False

    return True


# ------------------ Microphone ------------------
def mic_user():
    """Capture audio from mic and return recognized text."""
    recognizer = SR.Recognizer()
    try:
        with SR.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

            print("🔄 Processing...")
            text = recognizer.recognize_google(audio)
            return text
    except SR.UnknownValueError:
        print("❌ Could not understand the audio")
    except SR.RequestError as e:
        print(f"❌ API request error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
    return None


# ------------------ STS ------------------
def speech_to_speech():
    """Convert speech input directly into speech output (mic → mp3)."""
    print("🎙 Speak now...")
    text = mic_user()
    if not text:
        return False
    print("✅ You said:", text)
    print("🌍 Language detected:", detect_langs(text))
    return speech_saver(text)


# ------------------ File dialog ------------------
def get_save_path_gui_file(default_name="output"):
    """GUI save dialog for choosing mp3/txt output file."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_type = simpledialog.askstring(
        "Choose file type",
        "Enter file type (mp3 or txt):"
    )
    if not file_type:
        return None

    file_type = file_type.strip().lower()
    if file_type == "mp3":
        def_ext = ".mp3"
        types = [("MP3 files", "*.mp3")]
        title = "Save audio as..."
    elif file_type == "txt":
        def_ext = ".txt"
        types = [("Text files", "*.txt")]
        title = "Save text as..."
    else:
        return None

    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=def_ext,
        filetypes=types,
        initialfile=default_name + def_ext
    )
    if not file_path:
        return None

    return os.path.abspath(file_path)


# ------------------ TTS ------------------
def text_to_speech():
    """Convert a text file to speech (txt → mp3)."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    txt_file = filedialog.askopenfilename(
        title="Select text file",
        filetypes=[("Text files", "*.txt")]
    )
    if not txt_file or not os.path.exists(txt_file):
        print("❌ No file selected or file does not exist")
        return False

    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            script = f.read().strip()
        if not script:
            print("⚠️ The file is empty")
            return False

        return speech_saver(script)

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


# ------------------ STT ------------------
def speech_to_text():
    """Convert speech input to text and optionally save as txt."""
    print("🎙 Speak now...")
    text = mic_user()
    if not text:
        return None
    print("✅ You said:", text)
    print("🌍 Language detected:", detect_langs(text))

    # Ask user if they want to save transcript
    if speech_saver(text):
        print("✅ Transcript saved successfully")
    else:
        print("⚠️ Transcript not saved")

    return text


# ------------------ Main ------------------
def main():
    while True:
        print("\n🎙️ Voice/Text Converter Menu")
        print("1. Speech → Text (STT)")
        print("2. Text → Speech (TTS)")
        print("3. Speech → Speech (STS)")
        print("4. Exit")

        choice = input("Enter your choice (1–4): ").strip()

        if choice == "1":
            speech_to_text()
        elif choice == "2":
            text_to_speech()
        elif choice == "3":
            speech_to_speech()
        elif choice == "4":
            print("\n👋 Exiting...")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 