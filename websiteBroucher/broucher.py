import sys, os
from urllib import response

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import requests
import gradio as gr
from websiteSummarisation.website import Website
import json
from rich.console import Console
from rich.markdown import Markdown

# def get_links_system_prompt():
#     link_system_prompt = "You are provided with a list of links found on a webpage. \
# You are able to decide which of the links would be most relevant to include in a brochure about the company, \
# such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
   
#     link_system_prompt += "Respond ONLY with a valid JSON object following this schema: {\"links\": [{\"type\": string, \"url\": string}]}"
#     link_system_prompt += """
# {
#     "links": [
#         {"type": "about page", "url": "https://full.url/goes/here/about"},
#         {"type": "careers page", "url": "https://another.full.url/careers"}
#     ]
# }
# """
#     return link_system_prompt

# def get_links_system_prompt():
#     link_system_prompt = (
#         "You are provided with a list of links found on a webpage. "
#         "You are to decide which of the links are most relevant to include in a brochure about the company, "
#         "such as links to an About page, Company page, or Careers/Jobs page.\n"
#         "Respond ONLY with a valid JSON object in the following format:\n"
#         "{\n"
#         "  \"links\": [\n"
#         "    {\"type\": \"about page\", \"url\": \"https://full.url/goes/here/about\"},\n"
#         "    {\"type\": \"careers page\", \"url\": \"https://another.full.url/careers\"}\n"
#         "  ]\n"
#         "}\n"
#         "Do not include any text outside the JSON object."
#     )
#     return link_system_prompt

def get_links_system_prompt():
    link_system_prompt = "You are provided with a list of links found on a webpage. " \
    "You are able to decide which of the links would be most relevant to include in a brochure about the company, " \
    "such as links to an About page, or a Company page, or Careers/Jobs pages.\n"

    link_system_prompt += "Respond ONLY with a valid JSON object. Do not include any text before or after the JSON. " \
    "Follow this schema exactly: {\"links\": [{\"type\": string, \"url\": string}]}\n"

    link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""
    return link_system_prompt


def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

def get_links(websiteUrl):
    url = "http://localhost:11434/api/chat"
    website = Website(websiteUrl)
    response = requests.post(url, json={
    "model": "llama3",
    "messages":[
        {"role": "system", "content": get_links_system_prompt()},
        {"role": "user", "content": get_links_user_prompt(website)}
    ],
    "stream": False
    })
    # print("Status Code:", response.status_code)
    # print("Raw Response:", response.text)

    if response.status_code != 200:
        raise RuntimeError("Ollama API request failed")

    data = response.json()

    if "message" not in data or "content" not in data["message"]:
        raise ValueError("Unexpected API response format")

    result = data["message"]["content"]
    return json.loads(result)

# print(get_links("https://huggingface.co"))

# print(get_links_system_prompt())
# huggingface = Website("https://huggingface.co")
# print(huggingface.links)

# links_data = get_links("https://huggingface.co")
# print(links_data)

def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result
# print(get_all_details("https://huggingface.co"))

system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
      and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
 Include details of company culture, customers and careers/jobs if you have the information."


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5_00] # Truncate if more than 5,000 characters
    return user_prompt

# get_brochure_user_prompt("HuggingFace", "https://huggingface.co")

def create_brochure(company_name, websiteUrl):
    url = "http://localhost:11434/api/chat"
    response = requests.post(url, json={
    "model": "llama3",
    "messages":[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": get_brochure_user_prompt(company_name, websiteUrl)}
    ],
    "stream": False
    })
    return response.json()["message"]["content"]


print(create_brochure("ed","https://edwarddonner.com/"))