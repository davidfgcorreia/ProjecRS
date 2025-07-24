"""
Step 3: Run LLM prompt (ChatGPT-4.1) on all markdown table files in the 'tables' folder using the prompt in 'promts/promt_tables.txt'.
Outputs results to 'output_file_promt_ai/ouput_indexs.txt'.
"""
import os
import openai
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'promts', 'promt_tables.txt'))
TABLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'tables'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'output_file_promt_ai'))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'ouput_indexs.txt')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

INDEXES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'table_indexs', 'indexes.txt'))

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def get_table_files(tables_dir=TABLES_DIR):
    return [os.path.join(tables_dir, f) for f in os.listdir(tables_dir) if f.endswith('.md')]

def run_chatgpt41(tables_dir=TABLES_DIR, indexes_path=INDEXES_PATH, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if not client.api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Read markdown table files as text
    table_files = get_table_files(tables_dir)
    # Read indexes.txt as text
    indexes_text = read_file(indexes_path)

    # Build content array for OpenAI API
    content = []
    # Add the prompt as input_text first
    content.append({
        "type": "input_text",
        "text": f"Indexes:\n{indexes_text}"
    })
    # Add each markdown file as input_text
    for table_file in table_files:
        table_text = read_file(table_file)
        content.append({
            "type": "input_text",
            "text": f"Table file ({os.path.basename(table_file)}):\n{table_text}"
        })

    # Use the responses API format
    response = client.responses.create(
        model="gpt-4.1-2025-04-14",
        prompt={
            "id": "pmpt_687a4ce5c6848193adc34b2a1d9d99910b342dfcb447dd90",
            "version": "7",
        },
        input=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    # Write only the string output
    with open(output_file, 'w') as out:
        out.write(response.output_text if isinstance(response.output_text, str) else str(response.output_text))
    print(f"Result written to {output_file}")


def main(tables_dir=TABLES_DIR, indexes_path=INDEXES_PATH, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    print("Sending prompt to gpt-4.1-2025-04-14...")
    run_chatgpt41(
        tables_dir=tables_dir,
        indexes_path=indexes_path,
        output_dir=output_dir,
        output_file=output_file
    )

if __name__ == "__main__":
    main()
