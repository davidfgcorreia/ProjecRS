"""
Run LLM prompt (ChatGPT-4.1) on all markdown title files in the 'pdfs_titles' folder using the prompt in 'promts/promt_titles.txt'.
Outputs results to 'output_file_tiles_promt_ai/ouput_titles.txt'.
"""
import os
import openai

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'promts', 'promt_titles.txt'))
TITLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'pdfs_titles'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'output_file_tiles_promt_ai'))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'ouput_titles.txt')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

INDEXES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'table_indexs', 'indexes.txt'))

def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def get_title_files(titles_dir=TITLES_DIR):
    return [os.path.join(titles_dir, f) for f in os.listdir(titles_dir) if f.endswith('.txt')]

def get_index_files(indexes_dir=None):
    if indexes_dir is None:
        indexes_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'extracted_remain_indexes'))
    return [os.path.join(indexes_dir, f) for f in os.listdir(indexes_dir) if f.endswith('.txt')]

def run_chatgpt41_titles(titles_dir=TITLES_DIR, indexes_dir=None, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if not client.api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')

    # Build content string as requested
    index_files = get_index_files(indexes_dir)
    title_files = get_title_files(titles_dir)
    content_lines = []
    # For each file, match index and title by base name
    for title_file in title_files:
        base = os.path.splitext(os.path.basename(title_file))[0].replace('_titles','')
        # Find matching index file
        index_file = None
        for idx_file in index_files:
            if base in os.path.basename(idx_file):
                index_file = idx_file
                break
        indexes = read_file(index_file) if index_file else ''
        titles = read_file(title_file)
        content_lines.append(f"indexes_{base}:\n{indexes.strip()};\ntitles_{base}:\n{titles.strip()} \n")

    full_prompt = "\n".join(content_lines)

    response = client.responses.create(
        model="gpt-4.1-2025-04-14",
        prompt={
            "id": "pmpt_687e2ff0ffd88195979294fb0a531b69042bea55915ae1b1",
            "version": "4",
        },
        input=[
            {
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": full_prompt
                }]
            }
        ]
    )

    # return response.output_text
    return response.output_text



def main(titles_dir=TITLES_DIR, indexes_dir=None, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    print("Sending prompt to gpt-4.1-2025-04-14 for titles...")
    try:
        result = run_chatgpt41_titles(titles_dir, indexes_dir, output_dir, output_file)
    except Exception as e:
        result = f"Error: {e}"
    # Clear output directory before writing
    for f in os.listdir(output_dir):
        fp = os.path.join(output_dir, f)
        if os.path.isfile(fp):
            os.remove(fp)
    # Write only the string output
    with open(output_file, 'w') as out:
        out.write(result if isinstance(result, str) else str(result))
    print(f"Result written to {output_file}")

if __name__ == "__main__":
    main()
