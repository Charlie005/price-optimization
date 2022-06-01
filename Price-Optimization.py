# -*- coding: utf-8 -*-
"""
Created on Wed May 25 13:00:14 2022

@author: amalj
"""

import pandas as pd
from statsmodels.formula.api import ols
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

df = pd.read_csv("https://raw.githubusercontent.com/Charlie005/price-optimization/master/priceOptimize.csv")
#df3  = pd.read_csv("https://raw.githubusercontent.com/Charlie005/price-optimization/master/coefs.csv")

names = ['< PRODUCT >']
categories = ['< CATEGORY >'] + sorted(df['MC'].unique().tolist())
brands = ['< BRAND >']
# cName = df['NAME'].value_counts()
zones = ['< ZONE >']

df.dropna(inplace=True)

df = df.loc[df['Sales_at_Cost'] >= 0]
df = df.loc[df['NSU'] >= 0]
df = df.loc[df['MRP'] >= 0]
df = df.loc[df['SP'] >= 0]


df['UC'] = df['Sales_at_Cost']/df['NSU']
df['UGST'] = df['GST']/df['NSU']
names = ['< PRODUCT >'] + sorted(df['NAME'].unique().tolist())
categories = ['< CATEGORY >'] + sorted(df['MC'].unique().tolist())
brands = ['< BRAND >'] + sorted(df['Brand'].unique().tolist())
#cName = df['NAME'].value_counts()
zones = ['< ZONE >','NORTH','SOUTH','EAST','WEST']
dfdict = {}
for i in names:
    df1 = df.loc[df['NAME'] == i]
    dfdict[i] = df1
  
df3 = pd.DataFrame(columns=['NAME','ZONE','Intercept','SP_Coef','UC_Coef','UC','UGST'])    
for k in dfdict:
    zgroups = dfdict[k].groupby('ZONE')
    zonevals = zgroups.groups.keys()
    for i in zonevals:
        zval = zgroups.get_group(i)
        model = ols("NSU ~ SP + UC", data = zval).fit()
        p = model.params
        cost = dfdict[k].UC.mean()
        gst = dfdict[k].UGST.mean()
        temp = {'NAME':k,'ZONE':i, 'Intercept':p[0], 'SP_Coef':p[1], 'UC_Coef':p[2], 'UC':cost, 'UGST':gst}
        df3 = df3.append(temp,ignore_index=True)
#df3.to_csv('coefs.csv')


def getprice():
    
                val = df3.loc[(df3['NAME'] == product) & (df3['ZONE'] == zone)]
            
                S = []
                for i in np.arange(mrp/2,mrp,0.01):
                     S = S + [i]
            
                intercept = val['Intercept'].values[0]
                spcoef = val['SP_Coef'].values[0]
                uccoef = val['UC_Coef'].values[0]
                cost = val['UC'].values[0]
                gst = val['UGST'].values[0]
                Revenue = []
                N = []
                Discount = []
                DisPer = []
                for p in S:
                    nsu = intercept + (spcoef * p) + (uccoef * cost)
                    N.append(nsu)
                    # profit function
                    Revenue.append(nsu * (p - cost - gst))
                    dis = mrp - p
                    disper = (dis/mrp) * 100
                    Discount.append(dis)
                    DisPer.append(disper)
                # create data frame of price and revenue
                profit = pd.DataFrame({"NSU":N,"Price": S, "Revenue": Revenue,"Discount":Discount,"Discount%":DisPer})
            
                # taking only positive NSU's 
                profit2 = profit.loc[(profit['NSU']>0) & (profit['Revenue']>0)]
                if len(profit2) == 0:
                    st.write('Error: Given MRP cannot create positive Revenue!')
                else:
                    # to find the Price at which maximum units are sold AND max revenue is generated
                    profit2['Revenue x NSU'] = profit2['Revenue'] * profit2['NSU']
                
                
                
                    plt.plot(profit2['Price'], profit2['Revenue x NSU'])
                    plt.xlabel('Price')
                    plt.ylabel('Max revenue with Max NSU')
                
                    # Optimal price is where Revenue and NSU is maximum
                    optimal_price = profit2.loc[profit2['Revenue x NSU'] == max(profit2['Revenue x NSU'])]
                    rop = round((optimal_price['Price'].values[0]),2)
                    rnsu = round((optimal_price['NSU'].values[0]),2)
                    rrev = round((optimal_price['Revenue'].values[0]),2)
                    rdis = round((optimal_price['Discount%'].values[0]),2)
                    outputtable = pd.DataFrame({'Product':product,'Price':[rop],'NSU':[rnsu],'Revenue':[rrev],'Discount%':[rdis]})
                    outputtable.set_index('Product',inplace=True)
                    st.table(outputtable)
                       


#Page Config
st.set_page_config(page_title='Retail Price Optimisation',layout="wide")

# Title

st.title("Retail Price Optimisation")

cont = st.container()

col1, col2, col3, col4 = cont.columns(4)

category = col1.selectbox('Select Category',categories,index=categories.index('< CATEGORY >'))
if (category != '< CATEGORY >' ):
    val = df.loc[(df['MC'] == category)]
    brands = ['< BRAND >'] + sorted(val['Brand'].unique().tolist())
brand = col2.selectbox('Select Brand',brands,index = brands.index('< BRAND >'))
if(brand != '< BRAND >'):
    val = df.loc[(df['MC'] == category) & (df['Brand'] == brand)]
    names = ['< PRODUCT >'] + sorted(val['NAME'].unique().tolist())
product = col3.selectbox('Select Product',names,index = names.index('< PRODUCT >'))
if(product != '< PRODUCT >'):
    val = df3.loc[(df3['NAME'] == product)]
    zones = ['< ZONE >'] + val['ZONE'].unique().tolist()

zone = col4.selectbox('Select Zone',zones,index = zones.index('< ZONE >'))
if(zone != '< ZONE >'):
    val = df.loc[(df['NAME'] == product) & (df['ZONE'] == zone)]
    maxmrp = str(max(val['MRP']))
    minmrp = str(min(val['MRP']))
    mrpr = 'Previous MRP Range : ' + minmrp + ' - ' + maxmrp
    st.write(mrpr)
mrp = st.number_input("Enter MRP")



gp = st.button('Get Price')
if(gp):
    if((category != '< CATEGORY >' ) and (brand != '< BRAND >') and (product != '< PRODUCT >') and (zone != '< ZONE >')):
        getprice()
# with st.sidebar:
#     ld = st.button('Load Data')

# if(ld):
#     with st.spinner('Loading Data...'):
#         load_data()
#         df3  = pd.read_csv('C:\\Users\\amalj\\Desktop\\360\\coefs.csv')         
#     st.success('Done!')
