# API Endpoint Extractor

This script uses OpenAI's GPT-3.5-turbo model to generate chat-based responses and extracts information about API endpoints from the model's responses. The extracted data is then inserted into a MongoDB database.

## Prerequisites

1. **OpenAI API Key:**
   - Obtain an API key from OpenAI and replace `YOUR_API_KEY` in the script with your actual API key.
   - Instructions for obtaining an API key can usually be found on the OpenAI platform.


2. **Dependencies:**
   - Install the required Python packages using the following command:
     ```bash
     pip install openai pymongo
     ```

3. **Rancher:**
   - Ensure that Rancher is installed on your system. Rancher is a container orchestration platform that can be used to manage   Docker containers.

4. **MongoDB:**
   - 1.Pull the Docker Image of MongoDB.
     ```bash
      docker pull mongo:latest
      ```
   - 2.Run the MongoDB Image in Rancher.
     ```bash
      docker run -d --name mongodb -p 27017:27017 mongo
     ```
   - 3.Verify the Container is Running
     ```bash
      docker ps 
     ```
## Configuration

1. **OpenAI API Key:**
   - Replace the placeholder in the script (`openai.api_key = "YOUR_API_KEY"`) with your actual OpenAI API key.

2. **MongoDB Connection:**
   - Update the MongoDB connection string in the script if your MongoDB server is not running on `localhost:27017`.
