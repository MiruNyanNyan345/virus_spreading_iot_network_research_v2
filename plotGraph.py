import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot(df, title):
    fractional_size = np.array(df['fractional_size'])
    fraction_of_remove = np.array(df['fraction_of_remove'])

    plt.xlim(0, 1)
    plt.title(title)
    plt.plot(fraction_of_remove, fractional_size)
    plt.xlabel("Fraction Of Remove")
    plt.ylabel("Fractional Size")
    plt.show()


def fraction_remove(df_list, label_list, title, folder_path):
    while df_list and label_list:
        df = pd.read_csv(df_list.pop(0))
        df['fraction_of_remove'].plot()
        plt.title(title)
        plt.xlabel("TimeStep")
        plt.ylabel("Fraction of Remove")
        plt.legend(label_list)
    plt.savefig("{}/{}.png".format(folder_path, title))
    plt.show()


def fraction_size(df_list, label_list, title, folder_path):
    while df_list and label_list:
        df = pd.read_csv(df_list.pop(0))
        df['fractional_size'].plot()
        plt.title(title)
        plt.xlabel("TimeStep")
        plt.ylabel("Fractional Size")
        plt.legend(label_list)
    plt.savefig("{}/{}.png".format(folder_path, title))
    plt.show()


def plot_all(df_list, label_list, title):
    while df_list and label_list:
        df = pd.read_csv(df_list.pop(0))
        label = label_list.pop(0)
        fractional_size = np.array(df['fractional_size'])
        fraction_of_remove = np.array(df['fraction_of_remove'])
        plt.title(title)
        plt.plot(fraction_of_remove, fractional_size, label=label)
        plt.xlabel("Fraction Of Remove")
        plt.ylabel("Fractional Size")
        plt.legend()
    plt.savefig("{}.png".format(title))
    plt.show()
