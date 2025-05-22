from google import genai

def generate(prompt):
    print("prompt", prompt)
    client = genai.Client(api_key="AIzaSyD_MIEzwaPI--g1MXrxHbzQw_CBUqPYy-E")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text




