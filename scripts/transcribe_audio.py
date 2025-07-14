import sys
import os
import argparse
import json
from google import genai

# --- Argument Parsing ---
# Setup the command-line argument parser.
parser = argparse.ArgumentParser(description="Transcribe an audio file using the Gemini API.")
parser.add_argument(
    '--file-path',
    required=True,  # Make this argument mandatory
    help="The file path to upload to the Gemini API."
)
parser.add_argument(
    '--mime-type',
    required=True,  # Make this argument mandatory
    help="The MIME type of the audio file (e.g., 'audio/ogg', 'audio/mpeg')."
)

args = parser.parse_args()

# --- Configuration ---
# Get the API key from an environment variable for security.
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

# Initialize Google API Client
client=genai.Client(api_key=API_KEY)


def transcribe_audio(file_path, mime_type):

    try:
        file_response  = client.files.upload(file=open(file_path, "rb"), config={ "mime_type": mime_type,  }) # We can also add "display_name": display_name

        prompt = """
# Transcription Task

## 1. Primary Goal
Your primary goal is to transcribe the provided audio into a clean, accurate, and well-formatted text. The transcription language must match the speaker's language (Polish or English).

## 2. Output Format: Clean Transcript
This is a **clean** transcript. Adhere strictly to the following rules:
- **Character Encoding**: The final output MUST be a valid UTF-8 encoded string. You are strictly forbidden from using Unicode escape sequences (e.g., \u015b, \u0142). All special characters must be rendered directly in the text (e.g., ś, ł).
- **Remove Filler Words:** Do not transcribe any filler words.
    - **English fillers to remove:** um, uh, ah, er, like, you know, I mean.
    - **Polish fillers to remove:** yyy, eee, hmm, ten, no, wiesz, po prostu, jakby.
- **Remove Non-Speech Sounds:** Omit coughs, throat clearing, and other non-speech sounds.
- **Correct Errors:** Do not transcribe stutters, false starts, or self-corrections. Transcribe the final, intended word or phrase.
    - **Example:** If the speaker says "I want to, uh, I need to connect to the data- the database," transcribe it as "I need to connect to the database."

## 3. Punctuation and Formatting
- **Punctuation:** Add appropriate punctuation (periods, commas, question marks, exclamation points) to reflect the speaker's intonation and create grammatically correct sentences.
- **Line Breaks:** Start a new line for each new sentence or distinct utterance. Do not break a single sentence across multiple lines.

## 4. Language-Specific Rules

### For Polish (`pl-PL`)
- **Diacritics:** It is **absolutely crucial** to use correct Polish diacritical marks (ą, ę, ć, ł, ń, ó, ś, ź, ż) consistently and accurately, ensuring they are rendered as direct UTF-8 characters per the rule above. This is a top priority.
- **Mixed Language:** When an English word or phrase is used within a Polish sentence, transcribe it in English and apply the English capitalization rules below.

### For English (`en-US` / `en-GB`)
- **Capitalization Rules:**
    - **Common Nouns:** Use lowercase (e.g., `oscillator`, `pipeline`, `server`).
    - **Proper Nouns:** Capitalize all proper nouns, including brands, products, technologies, and people's names (e.g., `Google Chrome`, `JavaScript`, `Marcin`, `AWS`).
    - **Code & API Identifiers:** Use verbatim, case-sensitive capitalization (e.g., `getElementById`, `useState`, `torch.Tensor`).

## 5. Handling Technical Terminology
- In general, use the English term for technical concepts, especially in computing and software development.
- **Examples:** Transcribe as `canvas`, not `płótno`; `vertex`, not `wierzchołek`; `scene`, not `scena`, when used in a technical context.
"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, file_response ]
        )

        print(json.dumps({"transcript": response.text}, indent=2), file=sys.stdout)
        
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Call the main function with the MIME type from the parsed arguments.
    transcribe_audio(args.file_path, args.mime_type)

# Usage: 
# python /usr/src/app/scripts/transcribe_audio.py --file-path /tmp/file_1.oga --mime-type "audio/ogg"
# For a list of supported mime types, refer to: https://ai.google.dev/gemini-api/docs/audio#supported-formats
