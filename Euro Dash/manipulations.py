import numpy as np

data_manipulations = {
    'yoy_change': lambda df: df.pct_change(periods=12) * 100,
    'log_scale': lambda df: np.log(df)
}

def apply_manipulation_and_save(data_key, manipulation_key, result_key, datasets_dict):
    if data_key in datasets_dict and manipulation_key in data_manipulations:
        manipulation_function = data_manipulations[manipulation_key]
        datasets_dict[result_key] = manipulation_function(datasets_dict[data_key])
    else:
        print(f"Data for key {data_key} or manipulation {manipulation_key} not found")

