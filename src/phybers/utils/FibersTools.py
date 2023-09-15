#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as N
import pandas as pd
import regex

#%%
_curves_count_p = regex.compile(r"\s*'curves_count'\s*:\s*(\d+),")
def getBundleSize( bundlefile ):
    """ Get Bundles Size from file.
    """
    #get center names from bundle file
    with open(bundlefile, 'rt') as f:
        m = _curves_count_p.search(f.read())
        if m:
            return int(m.group(1))
        else:
            raise Exception

def fiber_lens(fiber):
    """
    Find the length of a fiber.
    """
    final_len = 0
    for i in range(fiber.shape[0]-1):
        current_lens = N.linalg.norm(fiber[i,:] - fiber[i+1,:])
        final_len+=current_lens
    return final_len


def Stadistics_txt_toxlsx(dirstad):
    """Create Dataframe from statistical measures: sizes, lens, intra_means,intra_min and Ri_dbindex.
    """
    tam  = []
    with open(dirstad+"/sizes.txt", "r") as file:
        for i in file:
            tam.append(int(i[:-1]))

    larg  = []
    with open(dirstad+"/lens.txt", "r") as file:
        for i in file:
            larg.append(round(float(i[:-1]),2))


    intra_mean  = []
    with open(dirstad+"/mensure_intra_means_dists.txt", "r") as file:
        for i in file:
            intra_mean.append(round(float(i.split(" ")[1][:-1]),2))

    Ri_db  = []
    with open(dirstad+"/mensure_Ri_db.txt", "r") as file:
        for i in file:
            Ri_db.append(round(float(i.split(" ")[1][:-1]),2))


    data= {'sizes':tam,'lens':larg,'intra_mean':intra_mean,'Ri_db':Ri_db }

    df_data = pd.DataFrame(data, columns = ['sizes','lens','intra_mean','Ri_db'])

    df_data.to_excel(dirstad+'/stadistics.xlsx')
