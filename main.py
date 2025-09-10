import anthropic
import sys

with open("camera-raw-data/Table_defs_v2.csv", 'r') as f:
    def_table = f.read()

with open("camera-raw-data/Table_feeds_v2.csv", 'r') as f:
    feed_table = f.read()

with open("camera-raw-data/encoder_schema.json", 'r') as f:
    encoder_schema = f.read()

with open("camera-raw-data/encoder_params.json", 'r') as f:
    encoder_params = f.read()

with open("camera-raw-data/decoder_schema.json", 'r') as f:
    decoder_schema = f.read()

with open("camera-raw-data/decoder_params.json", 'r') as f:
    decoder_params = f.read()

system_prompt = f"""
You are an expert analyst for camera feed systems.
The table represents the parameters for each one of a total of 100 camera feeds that are being processed by an analyst. The feeds are encoded and decoded based on the Encoder Parameters and Decoder Parameters respectively. The parameters are defined in the Encoder Scheme and Decoder Schema respectively.
Here is the data:

Camera Feeds Table, in CSV format:
{feed_table}

The definition of columns in `feed_table`, in CSV format:
{def_table}

Encoder Parameters, in JSON:
{encoder_params}

Encoder Schema, in JSON:
{encoder_schema}

Decoder Parameters, in JSON:
{decoder_params}

Decoder Schema, in JSON:
{decoder_schema}

Answer questions about camera feeds, encoding, and decoding.
"""

def exit_program(exit_code=0):
    print(f"Exiting program with code {exit_code}")
    sys.exit(exit_code)


def main():
    client = anthropic.Anthropic()
    messages = []

    print("Hi, I can answer your questions about camera feed, video encoding and decoding. What do you want to ask me?")
    while True:
        try:
            user_input = input(": ")
        except EOFError:
            print("\nGoodbye!")
            sys.exit(0)

        messages.append({"role": "user", "content": user_input})

        with client.messages.stream(
            messages=messages,
            model="claude-sonnet-4-0",
            max_tokens=1024,
            system=system_prompt,
            tools=[
                {
                    "name": "exit_program",
                    "description": "Exit the current program",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "exit_code": {
                                "type": "integer",
                                "description": "The exit code. If not specified, use 0 by default",
                            }
                        },
                        "required": ["exit_code"],
                    },
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            print("\n")
    
            final_message = stream.get_final_message()
            for content_block in final_message.content:
                if content_block.type == "tool_use" and content_block.name == "exit_program":
                    exit_code = content_block.input.get("exit_code", 0)
                    exit_program(exit_code)

            messages.append({"role": "assistant", "content": stream.get_final_text()})

if __name__ == "__main__":
    main()
