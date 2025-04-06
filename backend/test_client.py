import requests

url = "http://127.0.0.1:8000/recommend"
payload = {
    "query": "Looking for an adaptive numerical reasoning test under 40 minutes"
}

print(f"📨 Sending request to: {url}")
print(f"🔍 Query: {payload['query']}")

try:
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("\n✅ AI Recommendation:")
        print(data.get("groq_suggestion", "No suggestion received from AI."))
    else:
        print(f"\n❌ Request failed with status code {response.status_code}")
        print("Error:", response.text)

except Exception as e:
    print(f"\n❌ Exception occurred while making request: {e}")
