import json
from datetime import datetime

import requests
from airflow.decorators import dag, task
from airflow import DAG


@dag(
    start_date=datetime(2024, 7, 28),
    description="DAG to extract data from Fake Store API and send to Pipedream",
    schedule="0 23 * * *",
    catchup=False,
    default_args={"owner": "Levy Py"},
    tags=["maio"],
    is_paused_upon_creation=True
)
def maio_dag_taskflow():
    
    #pipedream_url = DAG.config.get('connections', 'pipedream_api').host
    pipedream_url = 'https://eog1uuz7izhfdbl.m.pipedream.net/'



    def fetch_product_data(product_id: int) -> dict:
        """Fetches product data from the Fake Store API.

        Args:
            product_id (int): The ID of the product.

        Returns:
            dict: A dictionary containing the product data, or None if an error occurs.
        """
        try:
            response = requests.get(
                f'https://fakestoreapi.com/products/{product_id}')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching product {product_id}: {e}")
            return None

    def create_product_object(product_data: dict) -> dict:
        """Creates a product object from the given data.

        Args:
            product_data (dict): A dictionary containing product data.

        Returns:
            dict: A formatted product object.
        """
        return {
            'id': product_data.get('id', None),
            'title': product_data.get('title', None),
            'price': product_data.get('price', None),
            'image': product_data.get('image', None),
            'category': product_data.get('category', None)
        }

    @task
    def send_data_to_pipedream(products_list: list):
        """Sends data to Pipedream.

        Args:
            products_list (list): A formatted list with product object.
        """
        data_json = json.dumps(products_list)
        try:
            response = requests.post(pipedream_url, data=data_json, headers={
                'Content-Type': 'application/json'})
            response.raise_for_status()
            print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to Pipedream: {e}")

    @task
    def extract_products(start_id: int, end_id: int) -> list:
        """Fetches product data for a range of IDs.

        Args:
            start_id (int): The starting product ID.
            end_id (int): The ending product ID.
        Returns:
            list: A formatted list with product object.
        """
        products = []
        for product_id in range(start_id, end_id + 1):
            product_data = fetch_product_data(product_id)
            if product_data:
                products.append(create_product_object(product_data))
        return products

    send_data_to_pipedream(extract_products(1, 20))


maio_dag_taskflow()
