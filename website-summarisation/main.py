import requests
from website import Website

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize_with_ollama_chat(websiteUrl):
    url = "http://localhost:11434/api/chat"
    website = Website(websiteUrl);

    response = requests.post(url, json={
        "model": "llama3",
        "messages":  messages_for(website),
        "stream": False
    })

    return response.json()["message"]["content"]

def display_summary(url):
    summary = summarize_with_ollama_chat(url)
    print(summary)

if __name__ == "__main__":
    display_summary("https://www.geeksforgeeks.org/artificial-intelligence/large-language-model-llm/")

