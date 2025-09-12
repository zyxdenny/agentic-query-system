root = "."

with open(f"{root}/camera-raw-data/Table_defs_v2.csv", 'r') as f:
    def_table = f.read()

with open(f"{root}/camera-raw-data/Table_feeds_v2.csv", 'r') as f:
    feed_table = f.read()

with open(f"{root}/camera-raw-data/encoder_schema.json", 'r') as f:
    encoder_schema = f.read()

with open(f"{root}/camera-raw-data/encoder_params.json", 'r') as f:
    encoder_params = f.read()

with open(f"{root}/camera-raw-data/decoder_schema.json", 'r') as f:
    decoder_schema = f.read()

with open(f"{root}/camera-raw-data/decoder_params.json", 'r') as f:
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
