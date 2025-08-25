"""Run debug LLM prompt flow for tables (typo-preserving legacy name).

Contains helper `run_chatgpt41` used by the pipeline in debug mode.
"""
import os
import openai
import tiktoken
import time



def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def get_table_files(tables_dir):
    return [os.path.join(tables_dir, f) for f in os.listdir(tables_dir) if f.endswith('.md')]

def count_tokens(text, model="gpt-4.1-2025-04-14"):
    # Use cl100k_base for GPT-4.1
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def run_chatgpt41(tables_dir, indexes_path, output_dir, output_file):
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
            if i > 0:
                time.sleep(30)  # Wait to avoid rate limits
            print(f"Sending batch {i+1}/{len(batches)} to GPT-4.1...")
            response = client.responses.create(
                model=model,
                prompt={
                    "id": "pmpt_6888b16de68481949b00b9fdedd143f10649530ba4589afd",
                    "version": "1",
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

def main(tables_dir, indexes_path, output_dir, output_file):
    print("Sending prompt to gpt-4.1-2025-04-14...")
    run_chatgpt41(
        tables_dir=tables_dir,
        indexes_path=indexes_path,
        output_dir=output_dir,
        output_file=output_file
    )

if __name__ == "__main__":
    # Example usage: update these paths as needed for standalone runs
    main(
        tables_dir="./tables",
        indexes_path="./table_indexes/indexes.txt",
        output_dir="./output_debug_file_promt_ai",
        output_file="./output_debug_file_promt_ai/ouput_indexs.txt"
    )
