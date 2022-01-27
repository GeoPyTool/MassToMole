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

# print(mass_reciprocal_list,clean_item_list,type_list)

mole_df = raw * type_list # 将数据从不同尺度质量分数统一化到总和设为1下的质量分数
mole_df = mole_df * mass_reciprocal_list # 将数据从质量分数换算到摩尔数
mole_df.columns = clean_item_list # 重新设置各列标签

mole_sum_list = mole_df.sum(axis = 1).tolist() # 总摩尔数
def reverse(n): return 1.0/n
x=list(map(reverse,mole_sum_list))

# mole_df = mole_df * x # 换算成摩尔分数

# print(raw,'\n', type_list,'\n',mole_df,'\n',x)

values_raw = np.matrix(mole_df.values)
sum_r = np.matrix(x).T
result = np.multiply( values_raw , sum_r)
print(np.shape(mole_df),np.shape(result))

result_df = pd.DataFrame(result)
result_df.columns = clean_item_list # 重新设置各列标签
result_df['Label'] = raw.index.tolist() # 添加 Label 这一列
result_df = result_df.set_index('Label') # Label 这一列是用来做样品备注的，就当作索引了
print(result_df)