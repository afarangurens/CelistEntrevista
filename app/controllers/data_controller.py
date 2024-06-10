from fastapi import APIRouter, HTTPException, Query, Depends, Request
from app.services.parquet_service import ParquetService
from typing import Optional
from app.auth.firebase_auth import get_user_token, UserCredentials, Token, verify_jwt_token
from firebase_admin import auth

router = APIRouter()
parquet_service = ParquetService(data_dir="data")

 
@router.post("/get_token")
async def get_token(user_credentials: UserCredentials):
    token = get_user_token(user_credentials)
    return {"token": token}

@router.post("/verify_token")
async def verify_token(token: Token):
    verification = verify_jwt_token(token.payload)
    return {"token": verification}


@router.get("/data/{filename}")
async def get_data(filename: str, query: str = Query(None), token: dict = Depends(verify_jwt_token)):
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
    key_value: Optional[str] = None,
    cummulative: Optional[bool] = False,
    token: dict = Depends(verify_jwt_token)
):
    """
    Router to query data based on Keys (KeyStore, KeyEmployee, KeyProduct).

    :param filename: Name of the Parquet file to query.
    :param start_date: Start date for the query in the format 'YYYY-MM-DD'.
    :param end_date: End date for the query in the format 'YYYY-MM-DD'.
    :param key_type: Type of key to filter by (KeyStore, KeyEmployee, or KeyProduct).
    :param key_value: Optional. Value of the key to filter by.
    :param cummulative: Optional. If True, returns cumulative values for each individual key (Qty, Amount, AvgAmount).
                        Defaults to False, which returns individual sales data.
    :return: Dict containing the queried data.
    :raises HTTPException 404: If the specified Parquet file is not found.
    """
    try:
        data = parquet_service.query_data_by_total_and_avg(
            filename=filename,
            start_date=start_date,
            end_date=end_date,
            key_type=key_type,
            key_value=key_value,
            cummulative=cummulative
        )
        return {"data": data}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))