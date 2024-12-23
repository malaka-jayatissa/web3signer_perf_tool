import requests
import json
from config.properties import BASE_URL
import json
import httpx

def send_attestation_signing(pubkey: str, fork_info:dict, attestation:dict, genesis_validators_root ):
    url = f'{BASE_URL}:6174/api/v1/eth2/sign/{pubkey}'
    headers = {
    "Content-Type": "application/json"
    }
    data = {
        "type": "ATTESTATION",
        "fork_info": {'fork':fork_info, "genesis_validators_root": genesis_validators_root},
        "attestation":attestation
    }
    response = requests.post(url, data=json.dumps(data), headers=headers )
    return (response.status_code, response.text)
    

async def send_attestation_signing_async(pubkey: str, fork_info:dict, attestation:dict, genesis_validators_root ):
    timeout = httpx.Timeout(600.0, connect=5.0) 
    url = f'{BASE_URL}:6174/api/v1/eth2/sign/{pubkey}'
    headers = {
    "Content-Type": "application/json"
    }
    data = {
        "type": "ATTESTATION",
        "fork_info": {'fork':fork_info, "genesis_validators_root": genesis_validators_root},
        "attestation":attestation
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers, timeout=timeout)
        return response.status_code, response.text