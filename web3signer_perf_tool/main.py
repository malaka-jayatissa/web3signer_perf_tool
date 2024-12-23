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
import asyncio
from multiprocessing import Pool, Manager, cpu_count

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
    return validator_details

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
    if(len(validator_details) < properties.SAMPLE_SIZE):
        raise Exception('Not enough validators for test')
  
    for i in range(properties.SAMPLE_SIZE):
        key = validator_details[i]
        start_time = time.perf_counter()
        response = api.send_attestation_signing(key,fork_info[1]['data'],attestation_data[1]['data'],genesis_data[1]['data']['genesis_validators_root'])
        end_time = time.perf_counter()
        result_obj = state.Result(response[0], response[1], end_time-start_time)
        logger.info(f'respnse = {response} i = {i}')
        state.STATE.add_result(i,result_obj)
        
    file.generate_results(parent_file_location,'latency',env, state.STATE)


async def send_attestation_async(key,fork_info, attestation_data, genesis_data, index:int ):
    start_time = time.perf_counter()
    response = await api.send_attestation_signing_async(key,fork_info[1]['data'],attestation_data[1]['data'],genesis_data[1]['data']['genesis_validators_root'])
    end_time = time.perf_counter()
    logger.info(f'respnse = {response} index = {index} start_time = {start_time}')
    result_obj = state.Result(response[0], response[1], end_time-start_time)
    return result_obj


def async_worker(key, fork_info, attestation_data, genesis_data, results_queue):
    """Wrapper to run async function in multiprocessing."""
    return asyncio.run(
        send_attestation_async(key, fork_info, attestation_data, genesis_data, results_queue)
    )


async def process_batch(keys, fork_info, attestation_data, genesis_data, results_queue,sleep_time):
    """Process a batch of keys asynchronously."""
    tasks = []
        
    for key in keys:
       task = asyncio.create_task(send_attestation_async(key, fork_info, attestation_data, genesis_data))
       tasks.append(task)
       await asyncio.sleep(sleep_time)
       
    results = await asyncio.gather(*tasks)
    for result in results:
        if result:
            results_queue.put(result)

def worker_process(keys, fork_info, attestation_data, genesis_data, results_queue, sleep_time):
    """Worker process to handle a batch of keys using asyncio."""
    asyncio.run(
        process_batch(keys, fork_info, attestation_data, genesis_data, results_queue, sleep_time)
    )


def throughput_with_pool(msgs_per_min:int, env :str):
    logger.info(f'Trhoughput Test Started base URL  = {properties.BASE_URL}')
    fork_info = api.get_fork_info()
    slot_data = api.get_current_slot()
    slot_to_sign = slot_data[1]['data'][0]['header']['message']['slot']
    logger.info(f'Slot to sign = {slot_to_sign}')
    attestation_data = api.get_attestaion_data(1,slot_to_sign)
    genesis_data = api.get_genesis()
    validator_details = load_public_keys()
    sleep_time = 60/msgs_per_min

    num_workers = min(cpu_count(), properties.SAMPLE_SIZE)
    batch_size = max(1, len(validator_details) // num_workers)
    logger.info(f'number of workers = {num_workers} batch size = {batch_size}')
    pool = Pool(processes=num_workers)
    manager = Manager()
    results_queue = manager.Queue()

    batches = [
        validator_details[i:i + batch_size]
        for i in range(0, len(validator_details), batch_size)
    ]

    if(len(validator_details) < properties.SAMPLE_SIZE):
        raise Exception('Not enough validators for test')
    
     # Submit tasks to the pool
    for batch in batches:
        pool.apply_async(worker_process, args=(batch, fork_info, attestation_data, genesis_data, results_queue, sleep_time))

    
    pool.close()
    pool.join()

    count = 0
    while not results_queue.empty():
        result = results_queue.get()
        state.STATE.add_result(count,result)
        count +=1

    # Generate results
    file.generate_results(parent_file_location, "throughput", env, state.STATE, msgs_per_min)
    






@app.command()
def throughput(msgs_per_min:int, env: str):
    """Test throughput."""
    logger.info('Throughput test started')
    throughput_with_pool(msgs_per_min, env)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app()