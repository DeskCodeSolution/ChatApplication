from google import genai

client = genai.Client(api_key="AIzaSyD_MIEzwaPI--g1MXrxHbzQw_CBUqPYy-E")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="hi",
)
print(response)
