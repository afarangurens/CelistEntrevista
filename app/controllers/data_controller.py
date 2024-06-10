from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.parquet_service import ParquetService

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