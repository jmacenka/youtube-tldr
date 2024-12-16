# YouTube Video Analyzer

A web application that allows users to input a YouTube video URL or Video ID, view the video's thumbnail and title, retrieve the transcript, and generate a summary using the Ollama model. The application consists of a FastAPI backend and a Plotly Dash frontend, both containerized using Docker.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **Video Metadata Retrieval**: Fetches the title and thumbnail of a YouTube video using the oEmbed endpoint.
- **Transcript Retrieval**: Retrieves the transcript of the video in English or German.
- **Summary Generation**: Generates a structured summary of the video's transcript using the Ollama model.
- **Interactive UI**: Provides a user-friendly web interface with input fields and buttons to perform actions.
- **Containerized Deployment**: Easily deployable using Docker and Docker Compose.

## Prerequisites

- **Docker**: Ensure Docker is installed on your system. You can download it from [Docker's official website](https://www.docker.com/get-started).
- **Docker Compose**: Typically bundled with Docker Desktop, but verify its installation.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/youtube_video_analyzer.git
   cd youtube_video_analyzer
    ```