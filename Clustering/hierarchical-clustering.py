#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2


conn = psycopg2.connect(host="192.168.107.30", port = 5432, database="postgres", user="postgres", password="")
cur = conn.cursor()
cur.execute("""with log as (
select ip from ip_port 
group by ip 
order by sum(traffic) desc limit 100 )
select ip_port.* from ip_port
join log
using(ip)
""") 
query_all = cur.fetchall()
df =  pd.DataFrame(query_all,columns=[ "ip",
"port",
"udp_percentage'",
"tcp_percentage" ,  
"icmp_percentage",
"http_percentage" ,
"https_percentage",
"dns_percentage",
"quic_percentage", 
"traffic", 
"hits"]);
df = df.fillna(0)
df['ip'] = df['ip'].astype('category')
df['port'] =  df['port'].astype('category')


from sklearn.preprocessing import LabelEncoder
labelencoder = LabelEncoder()
df['port_cat'] = labelencoder.fit_transform(df['port'])
df['ip_cat'] = labelencoder.fit_transform(df['ip'])



from sklearn.preprocessing import OneHotEncoder 
enc = OneHotEncoder(handle_unknown='ignore')
enc_port = pd.DataFrame(enc.fit_transform(df[['port_cat','ip_cat']]).toarray())
df = df.join(enc_port)


df.drop('port_cat',inplace=True,axis= 1)
df.drop('ip_cat',inplace=True,axis=1)



X = df.iloc[:, 2:].values
Y = df.iloc[:,0].values


# Feature Scaling
from sklearn.preprocessing import StandardScaler
sc_X = StandardScaler()
X_std = sc_X.fit_transform(X)



import scipy.cluster.hierarchy as shc
plt.figure(figsize=(10, 7))  
plt.title("Dendrograms")  
dend = shc.dendrogram(shc.linkage(X_std, method='ward'))




plt.figure(figsize=(10, 7))  
plt.title("Dendrograms")  
dend = shc.dendrogram(shc.linkage(X_std, method='ward'))
plt.axhline(y=28, color='r', linestyle='--')



from sklearn.cluster import AgglomerativeClustering
cluster = AgglomerativeClustering(n_clusters=10, affinity='euclidean', linkage='ward')  
class_number = cluster.fit_predict(X_std)
