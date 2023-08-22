#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd

#%%
def getBundleSize( bundlefile ):
    """ Get Bundles Size from file.
    """
    # Get center names from bundle file.
    ns = dict()
    exec(compile(open( bundlefile ).read(), bundlefile, 'exec'), ns)
    size = ns[ 'attributes' ][ 'curves_count' ]
    return  size

def fiber_lens(fiber):
    """
    Find the length of a fiber.
    """
    final_len = 0
    for i in range(fiber.shape[0]-1):
        current_lens = np.linalg.norm(fiber[i,:] - fiber[i+1,:])
        final_len+=current_lens
    return final_len


def Stadistics_txt_toxlsx(dirstad):
    """Create Dataframe from statistical measures: sizes, lens, intra_means,intra_min and Ri_dbindex.
    """
    with open(dirstad+"sizes.txt", "r") as file:
        tam = [int(i[:-1]) for i in file]

    with open(dirstad+"lens.txt", "r") as file:
        larg = [round(float(i[:-1]), 2) for i in file]

    with open(dirstad+"mensure_intra_dists.txt", "r") as file:
        intra_max = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    with open(dirstad+"mensure_intra_means_dists.txt", "r") as file:
        intra_mean = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    with open(dirstad+"mensure_Ri_db.txt", "r") as file:
        Ri_db = [round(float(i.split(" ")[1][:-1]), 2) for i in file]

    data= {'sizes':tam,'lens':larg,'intra_max':intra_max,'intra_mean':intra_mean,'Ri_db':Ri_db }
    df_data = pd.DataFrame(data, columns = ['sizes','lens','intra_max','intra_mean','Ri_db'])
    df_data.to_excel(dirstad+'stadistics.xlsx')
