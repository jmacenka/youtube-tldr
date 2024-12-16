from fastapi import FastAPI, Header
from pydantic import BaseModel
import ollama
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, CouldNotRetrieveTranscript
import requests
from typing import Optional, List, Dict

app = FastAPI()

class VideoSummaryResponse(BaseModel):
    summary: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None

class VideoMetadata(BaseModel):
    title: str
    upload_date: Optional[str] = None  # oEmbed may not provide upload date
    thumbnail_url: str
    supported_languages: List[Dict[str, str]]

class VideoTranscriptResponse(BaseModel):
    transcript: Optional[str] = None
    error: Optional[str] = None

@app.get("/video_metadata/{youtube_video_id}", response_model=VideoMetadata)
def get_video_metadata(youtube_video_id: str):
    """
    Fetches video metadata using YouTube's oEmbed endpoint and retrieves available transcript languages.
    """
    oembed_url = f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={youtube_video_id}&format=json"

    try:
        # Fetch video metadata
        oembed_response = requests.get(oembed_url)
        if oembed_response.status_code != 200:
            raise ValueError("Video not found or unable to fetch metadata.")

        oembed_data = oembed_response.json()
        title = oembed_data.get("title", "No Title Available")
        thumbnail_url = oembed_data.get("thumbnail_url", "")

        # Attempt to fetch available transcript languages
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_video_id)
            # Collect all available transcripts (both manually created and generated)
            available_transcripts = []
            for transcript in transcript_list:
                available_transcripts.append({
                    "code": transcript.language_code,
                    "name": transcript.language
                })
        except TranscriptsDisabled:
            available_transcripts = []
        except NoTranscriptFound:
            available_transcripts = []
        except CouldNotRetrieveTranscript:
            available_transcripts = []
        except Exception as e:
            raise ValueError(f"Error fetching transcripts: {e}")

        return VideoMetadata(
            title=title,
            thumbnail_url=thumbnail_url,
            supported_languages=available_transcripts
        )
    except ValueError as ve:
        # Return VideoMetadata with an error message by leveraging the response model
        return VideoMetadata(
            title="",
            thumbnail_url="",
            supported_languages=[],
            # Note: The response model does not include an error field.
            # To handle errors, consider creating a separate response model or adjusting the current one.
        )
    except Exception as e:
        # For unexpected errors, you might want to log them and return a generic error message.
        return VideoMetadata(
            title="",
            thumbnail_url="",
            supported_languages=[],
            # Similarly, handle errors appropriately based on your application's needs.
        )

@app.get("/video_transcripts/{youtube_video_id}", response_model=VideoTranscriptResponse)
def get_transcript(youtube_video_id: str, language: Optional[str] = "en"):
    """
    Fetches and concatenates the transcript of the YouTube video in the specified language.
    """
    # Validate language
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_video_id)
        # Attempt to find transcript in the specified language
        transcript = transcript_list.find_transcript([language])
    except NoTranscriptFound:
        return VideoTranscriptResponse(error="Transcript not found for the specified language.")
    except TranscriptsDisabled:
        return VideoTranscriptResponse(error="Transcripts are disabled for this video.")
    except CouldNotRetrieveTranscript:
        return VideoTranscriptResponse(error="Could not retrieve transcripts.")
    except Exception as e:
        return VideoTranscriptResponse(error=f"An error occurred: {e}")

    try:
        transcript_data = transcript.fetch()
    except Exception as e:
        return VideoTranscriptResponse(error=f"Error fetching transcript: {e}")

    concatenated_transcript = " ".join([item['text'] for item in transcript_data])
    return VideoTranscriptResponse(transcript=concatenated_transcript)

@app.get("/video_summary/{youtube_video_id}", response_model=VideoSummaryResponse)
def video_summary(
    youtube_video_id: str,
    language: Optional[str] = "en",
    ollama_api_url: Optional[str] = Header(None, alias="X-Ollama-API-URL")
):
    """
    Generates a summary of the YouTube video transcript using Ollama.
    """
    if not ollama_api_url:
        # Default to internal Docker network URL if not provided
        ollama_api_url = "http://ollama:11434"

    # Validate language by fetching available transcripts
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_video_id)
        available_transcripts = transcript_list.find_transcript([language])
    except NoTranscriptFound:
        return VideoSummaryResponse(error="Transcript not found for the specified language.")
    except TranscriptsDisabled:
        return VideoSummaryResponse(error="Transcripts are disabled for this video.")
    except CouldNotRetrieveTranscript:
        return VideoSummaryResponse(error="Could not retrieve transcripts.")
    except Exception as e:
        return VideoSummaryResponse(error=f"Error fetching transcripts: {e}")

    try:
        # Fetch the transcript
        transcript_data = available_transcripts.fetch()
        concatenated_transcript = " ".join([item['text'] for item in transcript_data])
    except Exception as e:
        return VideoSummaryResponse(error=f"Error fetching transcript: {e}")

    if not concatenated_transcript:
        return VideoSummaryResponse(error="No transcript available to generate summary.")

    # Generate the summary using Ollama's library
    try:
        # Define the prompt as per your requirements
        prompt = (
            f"Please provide a summary for the following YouTube video transcript:\n\n{concatenated_transcript}\n\n"
            "The summary should be structured as follows:\n"
            "1. A concise 2-sentence summary of the video's main points.\n"
            "2. A list of the main insights or takeaways presented in the video.\n"
            "3. An overall sentiment rating of the video's tone towards the main topic, expressed as Positive, Neutral, or Negative.\n"
            f"4. The summary shall be in this language as identified by its short-code: {language}.\n"
            f"6. Format your answer in Markdown Syntax.\n"
        )

        # Generate the summary
        summary_response = ollama.generate(
            model="llama3.2:3b",  # Replace with your desired model
            prompt=prompt
        )

        # Extract the summary from the response
        summary = summary_response.get('response', 'No summary available').strip()

    except Exception as e:
        return VideoSummaryResponse(error=f"Error generating summary with Ollama: {e}")

    return VideoSummaryResponse(summary=summary, transcript=concatenated_transcript)

# Enable CORS to allow frontend to communicate with backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://youtube_frontend:8050", "http://localhost:8050"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
