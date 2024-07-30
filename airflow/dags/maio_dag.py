import json
from datetime import datetime
import requests
from requests.exceptions import RequestException
from airflow import DAG
from airflow.operators.python_operator import PythonOperator



def pegando_id_produto_por_id(pid: int) -> 'dict':
    """Fazer o request dos dados de cada produto de acordo com o pid fornecido

    Args:
        pid (int): id do produto

    Returns:
        dict: dicionário com os dados do produto
    """
    try:
        r = requests.get(f'https://fakestoreapi.com/products/{pid}')
        r.raise_for_status()
        return r.json()
    except RequestException as e:
        print(f"Erro ao pegar o produto com id {pid}: {e}")
        return {}

def enviando_objeto_pipedream(data: list) -> 'requests.models.Response':
    """Envia um dict para o pipedream via post

    Args:
        data (list): lista para ser enviada, no formato de dicionário

    Returns:
        requests.models.Response: retorno do request
    """
    url = 'https://eog1uuz7izhfdbl.m.pipedream.net/'
    data_json = json.dumps(data)
    try:
        r = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'})
        r.raise_for_status()
        print(r.text)
        return r
    except RequestException as e:
        print(f"Erro ao enviar dados para Pipedream: {e}")
        return None

def teste_maio():
    pegar_ate_id = 20
    objeto_final = []
    id_atual = 1

    for id_atual in range(1, pegar_ate_id + 1):
        produto_atual = pegando_id_produto_por_id(id_atual)
        if produto_atual:
            objeto_final.append({
                'id': produto_atual.get('id', None),
                'title': produto_atual.get('title', None),
                'price': produto_atual.get('price', None),
                'image': produto_atual.get('image', None),
                'category': produto_atual.get('category', None)
    })

    enviar_pipedream = enviando_objeto_pipedream(objeto_final)

dag = DAG(
    'teste_maio',
    is_paused_upon_creation=True,
    default_args={
        'owner': 'Levy Py',
        'start_date': datetime(2024, 7, 28)
    },
    schedule_interval='0 23 * * *',
    catchup=False
)

enviar_pipedream_task = PythonOperator(
    task_id='enviar_pipedream',
    python_callable=teste_maio,
    dag=dag
)

enviar_pipedream_task
