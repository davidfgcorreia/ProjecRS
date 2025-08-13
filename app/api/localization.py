from fastapi import APIRouter, Depends, HTTPException, Response # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.db.database import get_db
from app.models.query import Query
from pathlib import Path
from app.processing_operation.operarions.find_section_by_marker import main as find_section_main
import os


router = APIRouter(prefix="/localization", tags=["localization"])

@router.get("/pdf-section/")
def get_pdf_section(query_id: str, user_id: int, marker: str):
    """
    Receives query_id, user_id, marker string.
    Finds the temp folder for the query/user, locates the PDF and markdown files, and returns the highlighted PDF section as a file response.
    """
    try:
        STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
        temp_dir = os.path.join(STORAGE_DIR, "temporary", f"query_{query_id}")
        query_folder = Path(temp_dir)
        pdf_dir = str(query_folder/"pdfs")
        md_dir = str(query_folder / "markdown")
        output_pdf_dir = str(query_folder / "highlighted")
        os.makedirs(output_pdf_dir, exist_ok=True)
        output_pdf_path = str(Path(output_pdf_dir) / f"highlighted_{marker}.pdf")

        # Try to find localizations_map.json in markdown or query folder
        json_path = None
        json_candidate1 = query_folder / "localizations" / "localizations_map.json"
        json_candidate2 = query_folder / "localizations_map.json"
        if json_candidate1.exists():
            json_path = str(json_candidate1)
        elif json_candidate2.exists():
            json_path = str(json_candidate2)
        find_section_main(pdf_dir, md_dir, marker, output_pdf_path, json_path)
        if not Path(output_pdf_path).exists():
            raise Exception("Failed to generate highlighted PDF")
        return Response(content=Path(output_pdf_path).read_bytes(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF localization error: {str(e)}")
