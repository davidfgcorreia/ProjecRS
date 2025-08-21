"""
Run LLM prompt (ChatGPT-4.1) on copied markdown sections for each study, sending indexes and copied sections as input.
Outputs results to 'output_file_sections_promt_ai/ouput_sections.txt'.
"""
import os
import openai # type: ignore

PROMPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'promts', 'promt_sections.txt'))
SECTIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'extracted_by_titles'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'output_file_sections_promt_ai'))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'ouput_sections.txt')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

INDEXES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main_storage', 'exemple', 'extracted_remain_indexes'))

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def get_section_files(sections_dir=SECTIONS_DIR):
    return [os.path.join(sections_dir, f) for f in os.listdir(sections_dir) if f.endswith('.md')]

def run_chatgpt41_sections(sections_dir=SECTIONS_DIR, indexes_dir=SECTIONS_DIR, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if not client.api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')

    # Read markdown section files as text
    section_files = get_section_files(sections_dir)
    # Get all indexes files
    index_files = [os.path.join(indexes_dir, f) for f in os.listdir(indexes_dir) if f.endswith('.txt')]

    # For each study, send a separate request and write output per study
    for section_file in section_files:
        base = os.path.splitext(os.path.basename(section_file))[0].replace('_selected_sections','')
        # Find matching index file by exact stem match
        index_file = None
        for idx_file in index_files:
            idx_stem = os.path.splitext(os.path.basename(idx_file))[0]
            if idx_stem == base:
                index_file = idx_file
                break
        if index_file:
            print(f"[DEBUG] Matched index file for '{base}': {index_file}")
        else:
            print(f"[DEBUG] No index file found for '{base}'")
        indexes = read_file(index_file) if index_file else ''
        section_text = read_file(section_file)
        content_str = f"indexes_{base}:\n{indexes.strip()};\n \n copied_sections_{base}:\n{section_text.strip()}\n"
        # Debug log: print the content being sent to the model
        response = client.responses.create(
            model="gpt-4.1-2025-04-14",
            prompt={
                "id": "pmpt_687e676223308190a57a480e5c51d03f02910677094f6041",
                "version": "2",
            },
            input=[
                {
                    "role": "user",
                    "content": content_str
                }
            ]
        )
        # Append LLM output to the main output file
        with open(output_file, 'a') as out:
            out.write(response.output_text if isinstance(response.output_text, str) else str(response.output_text))
            out.write("\n\n")  # Separate each study's output with a newline


def main(sections_dir=SECTIONS_DIR, indexes_dir=INDEXES_DIR, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    print("Sending prompt to gpt-4.1-2025-04-14 for copied sections...")
    run_chatgpt41_sections(
        sections_dir=sections_dir,
        indexes_dir=indexes_dir,
        output_dir=output_dir,
        output_file=output_file
    )

if __name__ == "__main__":
    main()
