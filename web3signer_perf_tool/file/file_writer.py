import state
import os
import pandas as pd
from dataclasses import  asdict
from datetime import datetime

def generate_results(parent_folder:str, measurement:str, env: str ,state: state.State, msgs_per_min: int = None):
    combined_path = os.path.join(parent_folder,'results' ,measurement,env)
    if not os.path.exists(combined_path):
        os.makedirs(combined_path)
    df = pd.DataFrame( [asdict(obj) for obj in state.results if obj is not None])
    if msgs_per_min != None:
        df['throughput'] = msgs_per_min
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = os.path.join(combined_path, f'result_{timestamp}') 
    os.makedirs(folder_name)
    file_name = os.path.join(folder_name, 'raw_data.csv') 
    df.to_csv(file_name,index=False)


