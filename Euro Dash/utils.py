def list_dataset_names(datasets_dict):
    if datasets_dict:
        print("Datasets available:")
        for dataset_name in datasets_dict.keys():
            print(dataset_name)
    else:
        print("No datasets available.")

