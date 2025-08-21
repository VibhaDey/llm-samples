import json
import gradio as gr
import requests

system_message = "You are a helpful assistant"

def chat(message, history):
    relevant_system_message = system_message
    if 'belt' in message:
        relevant_system_message += " The store does not sell belts; if you are asked for belts, be sure to point out other items on sale."
    
    print("History is:")
    print(history)
    print("And messages is:")
    print(message)

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3",
        "messages": [{"role": "system", "content":relevant_system_message}]
                   + history 
                   + [{"role": "user", "content": message}],
        "stream": True
    }
    response = requests.post(url, json=payload,stream=True)
    
    full_response = ""
 
    for line in response.iter_lines():
       if line:
          data = json.loads(line.decode("utf-8"))
          if "message" in data and "content" in data["message"]:
           full_response += data["message"]["content"]
           yield full_response  # streaming style like OpenAI

    # Ollama sends a final {"done": true}
    return full_response

system_message += "\nIf the customer asks for shoes, you should respond that shoes are not on sale today, \
but remind the customer to look at hats!"

gr.ChatInterface(fn=chat, type="messages").launch()
