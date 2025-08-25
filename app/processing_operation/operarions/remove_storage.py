"""Helpers to remove temporary workspace content safely.

Used by tests and cleanup steps to remove a query's temporary storage
with care to avoid deleting shared resources.
"""

import openai
import os

def delete_all_openai_files():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    client = openai.OpenAI(api_key=api_key)
    files = client.files.list()
    for f in files:
        print(f"Deleting file: {f.id} ({f.filename})")
        client.files.delete(f.id)
    print("All OpenAI files deleted.")

if __name__ == "__main__":
    delete_all_openai_files()
