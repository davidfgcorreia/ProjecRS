import os
import subprocess
import tempfile
import json
import time



def run_marker_on_pdf(pdf_path, output_dir, gimimy_api_key=None):
    """
    Calls the 'marker_single' tool to convert a PDF to a structured markdown file.
    Output is saved in the output_dir with the same basename as the PDF, .md extension.
    Supports LLM mode with GIMIMY (Gemini) API key if provided.
    Uses a config JSON file for advanced configuration.
    """
    if gimimy_api_key is None:
        gimimy_api_key = os.environ.get("GEMINI_API_KEY")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    config = {
        "output_format": "markdown",
        "use_llm": True,
        "disable_image_extraction": True,
    }
    if gimimy_api_key:
        config["gemini_api_key"] = gimimy_api_key
    # Write config to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(config, tmp)
        tmp.flush()
        config_path = tmp.name
    cmd = [
        "marker_single",
        pdf_path,
        "--config_json", config_path,
        "--output_dir", output_dir
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Converted {pdf_path} to markdown in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error running marker_single on {pdf_path}: {e}")
    finally:
        os.unlink(config_path)

def batch_convert_pdfs(pdf_dir, output_dir, gimimy_api_key=None):
    """
    Converts all PDFs in pdf_dir to markdown using marker_single.
    """
    for fname in os.listdir(pdf_dir):
        if fname.lower().endswith('.pdf'):
            run_marker_on_pdf(os.path.join(pdf_dir, fname), output_dir, gimimy_api_key)
            time.sleep(15)  # Avoid rate limiting issues

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch convert PDFs to structured markdown using marker_single.")
    parser.add_argument('--pdf_dir', default='../storage/pdfs', help='Directory with input PDFs')
    parser.add_argument('--output_dir', default='../storage/markdown', help='Directory to store markdown files')
    parser.add_argument('--gimimy_api_key', default=None, help='GIMIMY API key for LLM mode')
    args = parser.parse_args()
    batch_convert_pdfs(args.pdf_dir, args.output_dir, args.gimimy_api_key)

if __name__ == "__main__":
    main()
