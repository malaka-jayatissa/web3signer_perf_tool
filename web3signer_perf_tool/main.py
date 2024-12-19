from config import properties
import typer
import os
import sys
import logging
import api
import time
import state
import psycopg2
import file
from psycopg2.extras import DictCursor

app = typer.Typer()

logger = logging.getLogger()
parent_file_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_file_location)


PUB_KEY = '0xa63c3eb769abd7ef7a053afee544c37eb2626fcd490e952277c22a33fe90a54bb23df86bf0325817252e5329a5a2d2a8'


def load_public_keys():
    with psycopg2.connect(
        dbname = properties.KEYS_DATABASE,
        user = properties.KEYS_USER,
        password = properties.KEYS_DB_PASSWORD,
        host = properties.KEYS_DB_URL,
        port = properties.KEYS_DB_PORT ) as conn:
        validator_details = []
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * from public.KEYS')
            rows = cursor.fetchall()
            for row in rows:
                result = dict(row)
                validator_details.append(result['public_key'])
    
    logger.info(f'loaded {len(validator_details)} keys')
    return validator_details[100:200]

@app.command()
def latency(env:str):
    """Test latency."""
    logger.info(f'Latency Test Started base URL  = {properties.BASE_URL}')
    fork_info = api.get_fork_info()
    slot_data = api.get_current_slot()
    slot_to_sign = slot_data[1]['data'][0]['header']['message']['slot']
    logger.info(f'Slot to sign = {slot_to_sign}')
    attestation_data = api.get_attestaion_data(1,slot_to_sign)
    genesis_data = api.get_genesis()
    validator_details = load_public_keys()
    i = 0
    for key in validator_details:
        start_time = time.perf_counter()
        response = api.send_attestation_signing(key,fork_info[1]['data'],attestation_data[1]['data'],genesis_data[1]['data']['genesis_validators_root'])
        end_time = time.perf_counter()
        result_obj = state.Result(response[0], response[1], end_time-start_time)
        state.STATE.add_result(i,result_obj)
        i+=1
    file.generate_results(parent_file_location,'latency',env, state.STATE)



@app.command()
def throughput():
    """Test throughput."""
    print("Throughput test started!")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app()