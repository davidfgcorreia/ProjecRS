from sqlalchemy.orm import Session
from app.models.table_data import TableData
from app.schemas.table_data import TableDataCreate


def modular_processing_and_store(data: TableDataCreate, db: Session):
    """
    Process and fill the columns_content of the table, then store it in the database.
    This is a placeholder for modular processing logic.
    """
    # Example: Fill columns_content with dummy data (replace with real logic)
    filled_content = [[f"cell_{i}_{j}" for j in range(len(data.row_ids))] for i in range(data.num_rows)]
    # Create a new TableData instance or update existing one
    table = db.query(TableData).filter(TableData.query_id == data.query_id).first()
    if table:
        setattr(table, 'userid', data.userid)
        setattr(table, 'num_rows', data.num_rows)
        setattr(table, 'row_ids', data.row_ids)
        setattr(table, 'columns_content', filled_content)
    else:
        table = TableData(
            query_id=data.query_id,
            userid=data.userid,
            num_rows=data.num_rows,
            row_ids=data.row_ids,
            columns_content=filled_content
        )
        db.add(table)
    db.commit()
    db.refresh(table)
    return table
