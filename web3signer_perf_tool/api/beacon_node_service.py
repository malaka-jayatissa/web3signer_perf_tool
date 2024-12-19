from config.properties import BAECON_NODE
import requests
import json
import logging


logger = logging.getLogger()

def get_fork_info():
    url = f'{BAECON_NODE}/eth/v1/beacon/states/head/fork'
    response = requests.get(url)
    return (response.status_code, response.json())



def get_attestaion_data(index:int, slot:int ):
    url = f'{BAECON_NODE}/eth/v1/validator/attestation_data?slot={slot}&committee_index={index}'
    response = requests.get(url)
    return (response.status_code, response.json())


def get_current_slot():
    url = f'{BAECON_NODE}/eth/v1/beacon/headers'
    response = requests.get(url)
    return (response.status_code, response.json())

def get_genesis():
    url = f'{BAECON_NODE}/eth/v1/beacon/genesis'
    response = requests.get(url)
    return (response.status_code, response.json())

