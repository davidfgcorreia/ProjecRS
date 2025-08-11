"""
Step 3: Run LLM prompt (ChatGPT-4.1) on all markdown table files in the 'tables' folder using the prompt in 'promts/promt_tables.txt'.
Outputs results to 'output_file_promt_ai/ouput_indexs.txt'.
"""
import os
import openai
import tiktoken
import time

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

def count_tokens(text, model="gpt-4.1-2025-04-14"):
    # Use cl100k_base for GPT-4.1
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def run_chatgpt41(tables_dir=TABLES_DIR, indexes_path=INDEXES_PATH, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if not client.api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')

    os.makedirs(output_dir, exist_ok=True)

    table_files = get_table_files(tables_dir)
    indexes_text = read_file(indexes_path)
    max_tokens = 25000
    model = "gpt-4.1-2025-04-14"

    # Prepare the indexes content
    indexes_content = {
        "type": "input_text",
        "text": f"Indexes:\n{indexes_text}"
    }
    indexes_tokens = count_tokens(indexes_content["text"], model)

    # Preprocess batches
    batches = []
    current_batch = [indexes_content]
    current_tokens = indexes_tokens

    for table_file in table_files:
        table_text = read_file(table_file)
        file_content = {
            "type": "input_text",
            "text": f"Table file ({os.path.basename(table_file)}):\n{table_text}"
        }
        file_tokens = count_tokens(file_content["text"], model)
        # If adding this file would exceed the limit, start a new batch
        if current_tokens + file_tokens > max_tokens and len(current_batch) > 1:
            batches.append(current_batch)
            current_batch = [indexes_content]
            current_tokens = indexes_tokens
        # Only add the file if it fits with indexes
        if file_tokens + indexes_tokens <= max_tokens:
            current_batch.append(file_content)
            current_tokens += file_tokens
        # If a single file is too large, skip it
    if len(current_batch) > 1:
        batches.append(current_batch)

    # Send requests and append output
    with open(output_file, 'w') as out:
        for i, batch in enumerate(batches):
            if i> 0:
                time.sleep(60)  # Wait to avoid rate limits
            print(f"Sending batch {i+1}/{len(batches)} to GPT-4.1...")
            response = client.responses.create(
                model=model,
                prompt={
                    "id": "pmpt_687a4ce5c6848193adc34b2a1d9d99910b342dfcb447dd90",
                    "version": "7",
                },
                input=[
                    {
                        "role": "user",
                        "content": batch
                    }
                ]
            )
            out.write(response.output_text if isinstance(response.output_text, str) else str(response.output_text))
            out.write("\n\n")
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
