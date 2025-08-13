from fastapi import APIRouter, HTTPException, Response # type: ignore
from pathlib import Path
import os
import logging
import traceback
from app.processing_operation.operarions.highlight_header_values import main as highlight_header_main

router = APIRouter(prefix="/highlight-header", tags=["highlight-header"])

@router.get("/")
def get_highlighted_header_pdf(query_id: str, header: str, pdf_name: str):
    """
    Receives query_id and header string.
    Finds the temp folder for the query, locates the PDF, and returns a PDF with possible header values highlighted.
    """
    logger = logging.getLogger("pdf_highlight_header")
    try:
        STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
        temp_dir = os.path.join(STORAGE_DIR, "temporary", f"query_{query_id}")
        query_folder = Path(temp_dir)
        # Remove .pdf extension if present, then add .pdf
        pdf_stem = pdf_name[:-4] if pdf_name.lower().endswith('.pdf') else pdf_name
        pdf_path = str(query_folder / "pdfs" / f"{pdf_stem}.pdf")
        if not Path(pdf_path).exists():
            logger.error(f"[ERROR] PDF file not found: {pdf_path}")
            raise Exception(f"PDF file not found: {pdf_path}")
        output_dir = str(query_folder / "highlighted")
        logger.info(f"[DEBUG] query_id={query_id}, header={header}, pdf_name={pdf_name}")
        logger.info(f"[DEBUG] pdf_path={pdf_path}")
        logger.info(f"[DEBUG] output_dir={output_dir}")
        highlight_header_main(header, pdf_path, output_dir)
        output_pdf_path = str(Path(output_dir) / f"{Path(pdf_path).stem}_highlighted.pdf")
        logger.info(f"[DEBUG] output_pdf_path={output_pdf_path}")
        if not Path(output_pdf_path).exists():
            logger.error(f"[ERROR] Highlighted PDF not generated at {output_pdf_path}")
            raise Exception("Failed to generate highlighted header PDF")
        logger.info(f"[DEBUG] Returning highlighted PDF at {output_pdf_path}")
        return Response(content=Path(output_pdf_path).read_bytes(), media_type="application/pdf")
    except Exception as e:
        logger.error(f"[ERROR] PDF highlight header error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF highlight header error: {str(e)}")
