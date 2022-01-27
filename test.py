import pandas as pd
import numpy as np
import chempy,os
from chempy import Substance

LocationOfMySelf = os.path.dirname(__file__)
DataFileInput = LocationOfMySelf +"./test.csv"
raw = pd.read_csv(DataFileInput, engine='python')
raw = raw.set_index('Label') # Label 这一列是用来做样品备注的，就当作索引了

item_list = raw.columns.tolist()
type_list = [] # 数据类型，质量分数、ppm、ppb等等
clean_item_list = [] # 只保留化学式，去掉多余字符
mass_reciprocal_list = [] # 对应化学式的摩尔质量的倒数，如果不是化学式就为0
mole_sum_list = [] # 每一个样品的总摩尔数，用来计算各分量摩尔比

for i in item_list:
    type_tmp = 0.0
    mass_tmp = 0.0
    item_tmp =''
    if 'wt%' in i :
        type_tmp = 1.0/100
        item_tmp = i.replace("wt%", "")
    elif 'ppm' in i :
        type_tmp = 1.0/1000000
        item_tmp = i.replace("ppm", "")
    elif 'ppb' in i :
        type_tmp = 1.0/1000000000
        item_tmp = i.replace("ppb", "")
    else:
        pass
    
    for k in ['(',')','[',']']:
        item_tmp = item_tmp.replace(k, "")
    
    try: 
        mass_tmp = 1.0/(Substance.from_formula(item_tmp).mass)
    except:
        pass

    mass_reciprocal_list.append(mass_tmp)
    clean_item_list.append(item_tmp)
    type_list.append(type_tmp)

print(mass_reciprocal_list,clean_item_list,type_list)

mole_df = raw*mass_reciprocal_list
mole_df.columns = clean_item_list

mole_sum_list = mole_df.sum(axis = 1).tolist()

print(mole_df,mole_sum_list)