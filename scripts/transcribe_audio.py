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

        prompt = """Generate a transcript of the speech in its original language.

- For English words, if it is a common word, then spell it using lowercase (e.g. oscillator). If it is a proper noun, capitalize it properly (e.g. Google Chrome). If it's an API name or part of computer code, use verbatim capitalization (e.g. getElementById).
- For Thai text, do not add a space between words. Only add spaces between sentences or when there is obvious pausing.
- For technical terms, in general, spell it in English (e.g. canvas, vertex, scene).
- Remove filler words like "umm" and "ah". Also fix the transcript when the speaker corrects themselves or repeats themselves due to stuttering.${notes}

Remember, start a new line after each utterance or sentence, but do not break sentences into multiple lines."""

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
