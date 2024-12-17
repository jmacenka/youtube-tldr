# YT-TL;DR

YT-TL;DR is a web application that allows users to quickly generate summaries of YouTube videos. By leveraging YouTube's transcript data and the powerful Ollama language models, YT-TL;DR provides concise summaries, saving users time and enhancing their viewing experience.

The project assumes that you already have a running ollama instance with exposed port 11434 exposed on the local host you deploy this app onto.

## Features

- **Video Metadata Fetching:** Retrieve video titles, thumbnails, and available transcript languages.
- **Transcript Retrieval:** Obtain transcripts in supported languages.
- **Model Selection:** Choose from available Ollama models for summary generation.
- **Customizable Prompts:** Edit and customize the default prompt sent to the language model.
- **User-Friendly Interface:** Intuitive frontend built with Dash and styled with Bootstrap.
- **Settings Management:** Easily configure Ollama API URLs and other settings through a modal.

## Table of Contents

- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Demo

## Prerequisites

Before setting up YT-TL;DR, ensure you have the following installed on your system:

- Docker
- Docker Compose
- [Python 3.8+](https://www.python.org/downloads/) (if running without Docker)

## Installation

YT-TL;DR can be easily set up using Docker Compose. Follow the steps below to get started.

### Using Docker Compose

1. **Clone the Repository**
    
    ```bash 
    git clone https://github.com/jmacenka/yt-tldr.git
	cd yt-tldr 
	```
    
2. **Configure Environment Variables**
    
    Create a `.env` file in the project root to specify necessary environment variables.
    
    ```bash
    # .env
    BACKEND_PORT=8000 FRONTEND_PORT=8050 OLLAMA_API_URL=http://ollama:11434
	```
    
3. **Build and Run the Services**
    
    ```bash 
    docker-compose up -d --build 
    ```
    
    This command builds the Docker images and starts the backend and frontend services in detached mode.
    
4. **Verify the Services**
    
    - **Backend:** Accessible at `http://localhost:8000`
    - **Frontend:** Accessible at `http://localhost:8050`

### Running Locally Without Docker

If you prefer running the application without Docker, follow these steps:

1. **Clone the Repository**
    
    ```bash 
    git clone https://github.com/jmacenka/yt-tldr.git
    cd yt-tldr 
    ```
    
2. **Set Up a Virtual Environment**
    
    ```bash 
    python3 -m venv venv source venv/bin/activate 
    ```
    
3. **Install Dependencies**
    
    ```bash 
    pip install -r requirements.txt 
    ```
    
4. **Start the Backend**
    
    ```bash 
    cd backend uvicorn main:app --host 0.0.0.0 --port 8000 
    ```
    
5. **Start the Frontend**
    
    Open a new terminal window/tab, activate the virtual environment, and run:
    
    ```bash 
    cd frontend python app.py 
    ```
    
6. **Access the Application**
    
    - **Backend:** Accessible at `http://localhost:8000`
    - **Frontend:** Accessible at `http://localhost:8050`

## Configuration

### Ollama API URL

- **Default Value:** `http://ollama:11434`
- **Description:** The URL where your Ollama instance is running. Update this in the settings modal of the frontend if your Ollama API is hosted elsewhere.

### Default Summary Prompt

- **Location:** Settings Modal in the frontend
- **Description:** Customize the prompt that will be sent to the language model for generating summaries. Use placeholders `{transcript}` and `{language}` to dynamically insert the video's transcript and selected language.

## Usage

1. **Access the Frontend**
    
    Open your browser and navigate to `http://localhost:8050`.
    
2. **Search for a YouTube Video**
    
    - Enter a YouTube URL or Video ID in the input field.
    - Click on **Search for Video**.
    - The application will display the video's metadata, including the title and thumbnail.
3. **Select Language and Model**
    
    - Choose a language from the **Select Language** dropdown.
    - Select a model from the **Select Model** dropdown. The first available model is selected by default.
4. **Generate Summary**
    
    - Click on **Generate Summary**.
    - The summary will be displayed in the result area below in Markdown format.
5. **Customize Settings**
    
    - Click on **Settings** in the navbar.
    - Update the **Ollama API URL** if necessary.
    - Edit the **Default Summary Prompt** to customize how summaries are generated.
    - Click on **Check Connectivity** to verify the Ollama API connection.
    - Click **Close** to save and exit the settings modal.

## Project Structure
```
yt-tldr/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md

```

- **backend/**: Contains the FastAPI backend application.
- **frontend/**: Contains the Dash frontend application.
- **docker-compose.yml**: Defines the Docker services for the backend and frontend.
- **README.md**: Project documentation.
- **screenshot.png**: Screenshot of the application interface.

## Troubleshooting

### Common Issues

1. **Backend Not Accessible**
    
    - **Solution:** Ensure that the backend service is running and accessible at the specified `BACKEND_API_URL`. Check Docker logs if using Docker.
    
	```bash 
	docker-compose logs -f backend 
	```
    
2. **Ollama API Connectivity Errors**
    
    - **Solution:** Verify that the Ollama instance is running and the `Ollama API URL` is correctly configured in the settings. Use the **Check Connectivity** button in the settings modal to test the connection.
3. **No Available Models**
    
    - **Solution:** Ensure that the Ollama instance has models installed. Use the `/available_models` endpoint to verify available models.
    
    ```bash 
    curl http://localhost:8000/available_models
	```
    
4. **Invalid YouTube Video ID**
    
    - **Solution:** Ensure that the entered YouTube URL or Video ID is correct and that the video has transcripts available in the selected language.

### Additional Support

If you encounter issues not covered in this section, please refer to the project logs or open an issue in the repository.

## Contributing

Contributions are welcome! Please follow the steps below to contribute to YT-TL;DR.

1. **Fork the Repository**
    
    Click on the **Fork** button at the top right of the repository page.
    
2. **Clone Your Fork**
    
    ```bash 
    git clone https://github.com/jmacenka/yt-tldr.git
    cd yt-tldr
    ```
    
3. **Create a New Branch**
    
    ```bash
	git checkout -b feature/your-feature-name
	```
    
4. **Make Your Changes**
    
    Implement your feature or bug fix.
    
5. **Commit Your Changes**
    
    ```bash 
    git add . 
    git commit -m "Add feature: Your feature description" 
    ```
    
6. **Push to Your Fork**
    
    ```bash 
    git push origin feature/your-feature-name 
    ```
    
7. **Open a Pull Request**
    
    Navigate to the original repository and open a pull request detailing your changes.
    

## License

This project is licensed under the MIT License.

## Contact

For any questions or suggestions, please contact [yt-tldr@macenka.de](mailto:yt-tldr@macenka.de)

> Dec 2024