import os
from dotenv import load_dotenv

load_dotenv()


def get_weather(location: str):
    """Returns weather"""
    return f"Weather in {location} is 25C"


def run_sample() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set. Skipping Gemini sample.")
        return

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            tools=[get_weather],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False, maximum_remote_calls=5),
        ),
    )

    res = chat.send_message("What is the weather in Paris?")
    print(res.text)

    for msg in chat.get_history():
        print(msg.role)
        if msg.parts:
            for p in msg.parts:
                if p.function_call:
                    print("called:", p.function_call.name)


if __name__ == "__main__":
    run_sample()
