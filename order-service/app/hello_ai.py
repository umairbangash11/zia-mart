from openai import OpenAI
from app import settings

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=str(settings.OPENAI_API_KEY))

def chat_completion(prompt: str) -> str:
    # Call the OpenAI API with the GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4",  # Specify the GPT-4 model
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    
    # Return the response content from the first choice
    return response.choices[0].message['content']



