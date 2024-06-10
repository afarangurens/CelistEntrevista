from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.parquet_service import ParquetService
from typing import Optional

router = APIRouter()
parquet_service = ParquetService(data_dir="data")

@router.get("/data/{filename}")
async def get_data(filename: str, query: str = Query(None)):
    """
    Router get data for handling queries to a certain Parquet file.

    :param filename: Name of the Parquet file to be queried.
    :param query: Optional query string operation to filter the data.
    :raises HTTPException: If file not found raises FileNotFoundError.
    """
    try:
        data = parquet_service.get_data(filename=filename, query=query)
        return {"data": data}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.get("/query_data/{filename}")
async def query_data(
    filename: str,
    start_date: str,
    end_date: str,
    key_type: str,
    key_value: Optional[str] = None
):
    try:
        data = parquet_service.query_data(
            filename=filename,
            start_date=start_date,
            end_date=end_date,
            key_type=key_type,
            key_value=key_value
        )
        return {"data": data}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))