# Setup Instructions

## Environment Variables

Create a `.env` file in the `backend` directory with the following content:

```
MISTRAL_API_KEY=your_api_key_here
GROQ_API_KEY=gyour_api_key_here
GOOGLE_API_KEY=your_api_key_here
```

## Hugging Face Token

To get a free Hugging Face token:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Replace `your_huggingface_token_here` in the `.env` file

## Running the Server

```bash
cd backend
python main.py
```

The server will start on http://localhost:8000

