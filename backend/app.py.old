from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import ollama

app = FastAPI()

@app.get("/video_summary/{youtube_video_id}")
def video_summary(youtube_video_id: str):
    concatenated_transcript = get_transcript(youtube_video_id)

    if not concatenated_transcript:
        return {"error":"No transcript recieved"}

    # Step 5: Generate the summary using Ollama library
    try:
        summary_response = ollama.generate(
            model='llama3:8b',
            prompt=(
                f"Please provide a summary for the following YouTube video transcript:\n\n{concatenated_transcript}\n\n"
                "The summary should be structured as follows:\n"
                "1. A concise 2-sentence summary of the video's main points.\n"
                "2. A list of the main insights or takeaways presented in the video.\n"
                "3. An overall sentiment rating of the video's tone towards the main topic, expressed as Positive, Neutral, or Negative.\n"
            )
        )
        summary = summary_response.get('response', 'No summary available')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary with Ollama: {e}")

    # Step 6: Return the summary to the user/application
    return {"summary": summary, "transcript": concatenated_transcript}

@app.get("/video_transcripts/{youtube_video_id}")
def get_transcript(youtube_video_id: str):
    # Remove 'v=' prefix if present
    if youtube_video_id.startswith("v="):
        youtube_video_id = youtube_video_id[2:]

    # Step 3: Fetch the available transcripts for the YouTube video
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_video_id)
        # Get the first available transcript
        transcript = transcript_list.find_transcript(['en','de'])
        transcript_data = transcript.fetch()
    except NoTranscriptFound as e:
        raise HTTPException(status_code=404, detail=f"Could not find any transcripts: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    # Step 4: Concatenate the transcript
    concatenated_transcript = " ".join([item['text'] for item in transcript_data])
    return concatenated_transcript

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
