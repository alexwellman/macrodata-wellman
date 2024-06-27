import matplotlib.pyplot as plt

def plot_dataset(datasets_dict, dataset_key, title, x_label, y_label):
    if dataset_key in datasets_dict:
        df = datasets_dict[dataset_key]
        plt.figure(figsize=(14, 7))
        for country in df.columns:
            plt.plot(df.index, df[country], label=country)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print(f"Dataset '{dataset_key}' not found in the dictionary.")
