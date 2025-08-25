"""
Table description LLM service for ProjecRS backend.

This module provides functions to format tabular data for LLM input and generate a markdown-formatted table description using the OpenAI API.
It is used to automate the creation of concise, informative descriptions for tables in the application.

Functions:
    - format_table_for_llm: Format TableData as markdown for LLM input.
    - get_table_description_llm: Generate table description using OpenAI GPT-4.1.
"""
import openai
from app.models.table_data import TableData
import os
import logging

def format_table_for_llm(table: TableData) -> str:
    # Format the table as markdown for LLM input
    headers = table.row_ids
    flat_headers = [str(h) for h in headers]
    flat_headers = ["File"] + flat_headers
    rows = []
    for row in table.columns_content:
        row_data = []
        for i in range(len(flat_headers)):
            val = row.get(f'col{i}', '-')
            val_str = str(val) if val is not None and str(val).strip() != '' else '-'
            row_data.append(val_str)
        rows.append(row_data)
    # Markdown table
    md = '| ' + ' | '.join(flat_headers) + ' |\n'
    md += '| ' + ' | '.join(['---'] * len(flat_headers)) + ' |\n'
    for row in rows:
        md += '| ' + ' | '.join(row) + ' |\n'
    logging.debug(f"[LLM] Formatted markdown table for LLM:\n{md}")
    return md

def get_table_description_llm(table: TableData) -> str:
    md_table = format_table_for_llm(table)
    prompt = f"""
Given the following table, write a concise and informative description of its contents, including the meaning of each column and any notable patterns or insights.\n\n{md_table}\n\nDescription:
"""
    logging.debug(f"[LLM] Prompt sent to LLM:\n{prompt}")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment.')
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    description = content.strip() if content is not None else ""
    logging.debug(f"[LLM] Response from LLM:\n{description}")
    return description
