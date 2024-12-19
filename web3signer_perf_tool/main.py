from config import properties
import typer
import os
import sys
import logging
import api
import time

app = typer.Typer()

logger = logging.getLogger()
parent_file_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_file_location)


PUB_KEY = '0xa1e55efd18658e26ec29ef6f36916493260aa8c8ad007708430bc7e17f6bc3ae43a8dfc2158c5c15c7f4fe64bf2933a8'

@app.command()
def latency():
    """Test latency."""
    logger.info(f'Latency Test Started base URL  = {properties.BASE_URL}')
    fork_info = api.get_fork_info()
    slot_data = api.get_current_slot()
    slot_to_sign = slot_data[1]['data'][0]['header']['message']['slot']
    logger.info(f'Slot to sign = {slot_to_sign}')
    attestation_data = api.get_attestaion_data(7,slot_to_sign)
    genesis_data = api.get_genesis()
    logger.info(fork_info[1]['data'])
    logger.info(attestation_data[1]['data'])
    logger.info(genesis_data[1]['data']['genesis_validators_root'])
    response = api.send_attestation_signing(PUB_KEY,fork_info[1]['data'],attestation_data[1]['data'],genesis_data[1]['data']['genesis_validators_root'])
    logger.info(response)
    attestation_data[1]['data']['target']['root'] = '0x052531a9a04dfb55f08029b4dd6735aaef5baf050413ff8a10e67fd583bed412'
    response = api.send_attestation_signing(PUB_KEY,fork_info[1]['data'],attestation_data[1]['data'],genesis_data[1]['data']['genesis_validators_root'])
    logger.info(response)


@app.command()
def throughput():
    """Test throughput."""
    print("Throughput test started!")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app()