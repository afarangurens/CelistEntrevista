import pandas as pd
import os
from fastapi import HTTPException

class ParquetService:
    """
    Service class for handling operations on the Apache Parquet files in folder data/.
    """

    def __init__(self, data_dir=r"C:\Users\USUARIO\Documents\Entrevistas\PruebaCelis\microservicio-datamart\data") -> None:
        """
        Initialize the ParquetService with the directory containing the Parquet files.

        :param data_dir: Directory where the Parquet files are stored.
        """
        self.data_dir = data_dir
    

    def get_data(self, filename, query=None) -> list[dict]:
        """
        Load data from a Parquet file and return it as a list of dictionaries.

        :param filename: Name of the Parquet file.
        :param query: Optional query string to filter the data.
        :return: Data from the Parquet files as a list of dictionaries.
        :raises FileNotFoundError: If the file does not exist in the specified directory.
        """
        file_path = os.path.join(self.data_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File {filename} not found in {self.data_dir}"
            )
        
        loaded_data = self._load_df_with_parquet(file_path=file_path, query=query)

        return loaded_data.to_dict(orient="records")
    

    def _load_df_with_parquet(self, file_path, query) -> pd.DataFrame:
        """
        Load a Dataframe from a parquet file and optionally filter it with a query.

        :param file_path: Full path to the Parquet files.
        :param query: Optional query string to filter the data.
        :return: Loaded pandas DataFrame.
        """
        df = pd.read_parquet(file_path)

        if query:
            df = df.query(query)
        
        return df


    def query_data(self, filename: str, start_date: str, end_date: str, key_type:str, key_value: str = None) -> list[dict]:
        """
        Query data based on date range and KeyEmployee.

        :param filename: Name of the Parquet file.
        :param start_date: Start date for the query in the format 'YYYY-MM-DD'.
        :param end_date: End date for the query in the format 'YYYY-MM-DD'.
        :param key_type: Type of key to filter by (KeyEmployee, KeyProduct, or KeyStore).
        :param key_value: Key to filter by.
        :return: Filtered list of dictionaries.
        """
        file_path = os.path.join(self.data_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File {filename} not found in {self.data_dir}"
            )

        loaded_df = self._load_filtered_dataframe(file_path, key_type)
        
        start_date = self._date_to_str(start_date)
        end_date = self._date_to_str(end_date)

        filtered_df = self._filter_df(loaded_df, start_date, end_date, key_type, key_value)

        return filtered_df
    

    def _load_filtered_dataframe(self, file_path, key_type) -> pd.DataFrame:
        """
        Load a filtered DataFrame from a Parquet file based on a specified key type.

        :param file_path: Path to the Parquet file.
        :param key_type: Type of key to filter by (KeyEmployee, KeyProduct, or KeyStore).
        :return: Filtered DataFrame.
        """
        try:
            df = pd.read_parquet(file_path, columns=['KeyDate', key_type, 'Qty', 'Amount'])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{key_type} not found in the Parquet files.")

        return df
    
    def _date_to_str(self, date) -> pd.Timestamp:
        """
        Convert a date string to a pandas Timestamp object.

        :param date: Date string in the format 'YYYY-MM-DD'.
        :return: Pandas Timestamp object.
        """
        return pd.to_datetime(date, format='%Y-%m-%d')
    
    def _filter_df(self, df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp, key_type: str, key_value: str = None) -> list[dict]:
        """
        Filter DataFrame based on date range and optionally by key value, then aggregate the results.

        :param df: DataFrame to filter.
        :param start_date: Start date for filtering.
        :param end_date: End date for filtering.
        :param key_type: Type of key to filter by (KeyEmployee, KeyProduct, or KeyStore).
        :param key_value: Value of the key to filter by.
        :return: Aggregated result as a list of dictionaries.
        """

        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="DataFrame is empty or None.")

        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

        if key_type not in df.columns:
            raise HTTPException(status_code=400, detail=f"{key_type} not found in DataFrame columns.")

        df['KeyDate'] = pd.to_datetime(df['KeyDate'], format='%m/%d/%Y %I:%M %p')

        df_filtered = df[(df['KeyDate'] >= start_date) & (df['KeyDate'] <= end_date)]

        if key_value:
            df_filtered = df_filtered[df_filtered[key_type] == key_value]

        df_filtered['AvgAmount'] = df_filtered['Amount'] / df_filtered['Qty']

        df_grouped = df_filtered.groupby(key_type).agg({'Qty': 'sum', 'Amount': 'sum', 'AvgAmount': 'mean'}).reset_index()

        return df_grouped.to_dict(orient="records")