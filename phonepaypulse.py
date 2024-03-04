import json
import pymysql
import pandas as pd
import requests
import plotly.express as px
import plotly.io as pio
import streamlit as st

myconnection = pymysql.connect(host="localhost",user="root",passwd="9867335172$Ss",database="phonepay")
cur=myconnection.cursor()

cur.execute("select * from aggregated_trans;")
myconnection.commit()
df1= pd.DataFrame(cur.fetchall(),columns = ("States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"))

#Aggregated_user
cur.execute("select * from aggregated_users")
myconnection.commit()
df2 = pd.DataFrame(cur.fetchall(),columns = ("States", "Years", "Quarter", "Brands", "Transaction_count", "Percentage"))

#Map_transaction
cur.execute("select * from map_transa")
myconnection.commit()
df3 = pd.DataFrame(cur.fetchall(),columns = ("States", "Years", "Quarter", "Districts", "Transaction_count", "Transaction_amount"))

#Map_user
cur.execute("select * from map_user")
myconnection.commit()
df4 = pd.DataFrame(cur.fetchall(),columns = ("States", "Years", "Quarter", "Districts", "RegisteredUser", "AppOpens"))

#Top_transaction
cur.execute("select * from top_transa")
myconnection.commit()
df5 = pd.DataFrame(cur.fetchall(),columns = ("States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"))
df5['Pincodes']=df5['Pincodes'].astype('string')

#Top_user
cur.execute("select * from top_user")
myconnection.commit()
df6 = pd.DataFrame(cur.fetchall(), columns = ("States", "Years", "Quarter", "Pincodes", "RegisteredUser"))


def dis_map_amt(a,b):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response =requests.get(url)
    india_states= json.loads(response.content)

    map_df1=df1[(df1['Years']==a)&(df1['Quarter']==b)]

    fig=px.choropleth(map_df1,locations="States",geojson=india_states,color="Transaction_amount",scope="asia", featureidkey= "properties.ST_NM",title = "TRANSACTION AMOUNT"
                    ,color_continuous_scale= 'portland', range_color= (1000000,500000000))
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(width =800, height= 700)
    return st.plotly_chart(fig)

def dis_map_count(a,b):
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response =requests.get(url)
    india_states= json.loads(response.content)

    map_df1=df1[(df1['Years']==a)&(df1['Quarter']==b)]

    fig1=px.choropleth(map_df1,locations="States",geojson=india_states,color="Transaction_count",scope="asia", featureidkey= "properties.ST_NM",title = "TRANSACTION COUNT"
                    ,color_continuous_scale= 'portland', range_color= (0,1000000))
    fig1.update_geos(fitbounds="locations",visible=False)
    fig1.update_layout(width =800, height= 700)
    return st.plotly_chart(fig1)

def dis_bar_amt(a,b):        
    map_df1=df1[(df1["Years"]==a)&(df1["Quarter"]==b)].groupby("Transaction_type").agg({"Transaction_amount":"sum"}).reset_index()
    fig2=px.bar(map_df1,x="Transaction_type",y="Transaction_amount",title = "TRANSACTION AMOUNT",color_discrete_sequence=px.colors.sequential.Tealgrn)
    fig2.update_layout(width=700, height= 700)
    return st.plotly_chart(fig2)

def dis_bar_count(a,b):        
    map_df1=df1[(df1["Years"]==a)&(df1["Quarter"]==b)].groupby("Transaction_type").agg({"Transaction_count":"sum"}).reset_index()
    fig3=px.bar(map_df1,x="Transaction_type",y="Transaction_count",title = "TRANSACTION COUNT",color_discrete_sequence=px.colors.sequential.Bluered)
    fig3.update_layout(width=700, height= 700)
    return st.plotly_chart(fig3)

def dis_bar_brand(a,b):        
    map_df2=df2[(df2["Years"]==a)&(df2["Quarter"]==b)].groupby("Brands").agg({"Transaction_count":"sum"}).sort_values("Transaction_count",ascending=False).reset_index()
    fig4=px.bar(map_df2,x="Brands",y="Transaction_count",title = "Mobile Brand Used",color_discrete_sequence=px.colors.sequential.Pinkyl_r)
    fig4.update_layout(width=1200, height= 700)
    return st.plotly_chart(fig4)

def dis_state_bar(a,b,c):
    map_df3=df3[(df3["Years"]==a)& (df3["Quarter"]==b)&(df3["States"]==c)]
    fig5=px.bar(map_df3,x="Districts",y=["Transaction_count","Transaction_amount"],title = "Transaction Details of District ",color_discrete_sequence=px.colors.sequential.Rainbow)
    fig5.update_layout(width=1200, height= 700)
    return st.plotly_chart(fig5)

def top_count(a,b,c):

    if c=="Pincodes":
        data=df5

    else:
        data=df3
 

    if a=="All":
        map_df4=data.groupby(c).agg({"Transaction_count":"sum"}).sort_values("Transaction_count",ascending=False).head(10).reset_index()
    elif b=="All":
        map_df4=data[(data["Years"]==a)].groupby(c).agg({"Transaction_count":"sum"}).sort_values("Transaction_count",ascending=False).head(10).reset_index()
    else:
        map_df4=data[(data["Years"]==a)&(data["Quarter"]==b)].groupby(c).agg({"Transaction_count":"sum"}).sort_values("Transaction_count",ascending=False).head(10).reset_index()
        
    fig6=px.bar(map_df4,x=c,y="Transaction_count",title = "TRANSACTION COUNT",color_discrete_sequence=px.colors.sequential.Pinkyl_r)
    fig6.update_layout(xaxis_type='category',width=600, height= 700)

    return st.plotly_chart(fig6)

def top_amount(a,b,c):

    if c=="Pincodes":
        data=df5

    else:
        data=df3
 

    if a=="All":
        map_df5=data.groupby(c).agg({"Transaction_amount":"sum"}).sort_values("Transaction_amount",ascending=False).head(10).reset_index()
    elif b=="All":
        map_df5=data[(data["Years"]==a)].groupby(c).agg({"Transaction_amount":"sum"}).sort_values("Transaction_amount",ascending=False).head(10).reset_index()
    else:
        map_df5=data[(data["Years"]==a)&(data["Quarter"]==b)].groupby(c).agg({"Transaction_amount":"sum"}).sort_values("Transaction_amount",ascending=False).head(10).reset_index()
        
    fig7=px.bar(map_df5,x=c,y="Transaction_amount",title = "TRANSACTION AMOUNT",color_discrete_sequence=px.colors.sequential.Agsunset)
    fig7.update_layout(xaxis_type='category',width=600, height= 700)

    return st.plotly_chart(fig7)

def top_users(a,b,c):

    if c=="Pincodes":
        data=df6

    else:
        data=df4
 

    if a=="All":
        map_df6=data.groupby(c).agg({"RegisteredUser":"sum"}).sort_values("RegisteredUser",ascending=False).head(10).reset_index()
    elif b=="All":
        map_df6=data[(data["Years"]==a)].groupby(c).agg({"RegisteredUser":"sum"}).sort_values("RegisteredUser",ascending=False).head(10).reset_index()
    else:
        map_df6=data[(data["Years"]==a)&(data["Quarter"]==b)].groupby(c).agg({"RegisteredUser":"sum"}).sort_values("RegisteredUser",ascending=False).head(10).reset_index()
        
    fig8=px.bar(map_df6,x=c,y="RegisteredUser",title = "USERS COUNT",color_discrete_sequence=px.colors.sequential.Greens_r)
    fig8.update_layout(xaxis_type='category',width=600, height= 700)

    return st.plotly_chart(fig8)

def dis_pie(a,b):
    if a=="All":
        map_df7=df1.groupby("Transaction_type").agg({"Transaction_amount":"sum"}).reset_index()
    elif b=="All":
        map_df7=df1[(df1["Years"]==a)].groupby("Transaction_type").agg({"Transaction_amount":"sum"}).reset_index()
    else:
        map_df7=df1[(df1["Years"]==a)&(df1["Quarter"]==b)].groupby("Transaction_type").agg({"Transaction_amount":"sum"}).reset_index()
        
    fig9=px.pie(map_df7,values="Transaction_amount",names="Transaction_type",title = "Transaction Tyeps",color_discrete_sequence=px.colors.sequential.Rainbow)
    fig9.update_layout(width=600, height= 700)
    return st.plotly_chart(fig9)




st.set_page_config(layout= "wide")
st.title("PHONEPE PLUSE")

tab1, tab2, tab3 = st.tabs(["***HOME***","***EXPLORE DATA***","***TOP 10***"])

with tab1:
    col1, col2  = st.columns(2)
    with col1:
        st.header("About")
        st.write('''The Indian digital payments story has truly captured the world's imagination. From the largest towns to the remotest villages, there is a payments revolution being driven by the penetration of mobile phones and data.

When PhonePe started 5 years back, we were constantly looking for definitive data sources on digital payments in India. Some of the questions we were seeking answers to were - How are consumers truly using digital payments? What are the top cases? Are kiranas across Tier 2 and 3 getting a facelift with the penetration of QR codes?
This year as we became India's largest digital payments platform with 46% UPI market share, we decided to demystify the what, why and how of digital payments in India.

This year, as we crossed 2000 Cr. transactions and 30 Crore registered users, we thought as India's largest digital payments platform with 46% UPI market share, we have a ring-side view of how India sends, spends, manages and grows its money. So it was time to demystify and share the what, why and how of digital payments in India.

PhonePe Pulse is your window to the world of how India transacts with interesting trends, deep insights and in-depth analysis based on our data put together by the PhonePe team.''')
    
    with col2:
        st.video("https://youtu.be/c_1H6vivsiA?si=3H3-0_GkSN9mfPVx")


with tab2:
    col1, col2  = st.columns(2)
    with col1:
        year = st.selectbox('**YEAR**',(2018,2019,2020,2021,2022,2023))
    with col2:
        if year==2023:
            month= st.selectbox('**QUARTER**',("Jan-Mar","Apr-Jun","Jul-Sep"))
        else:
            month= st.selectbox('**QUARTER**',("Jan-Mar","Apr-Jun","Jul-Sep","Oct-Dec"))

    if month=="Jan-Mar":
        quater=1
    elif month=="Apr-Jun":
        quater=2
    elif month=="Jul-Sep":
        quater=3
    elif month=="Oct-Dec":
        quater=4

    colu1,colu2=st.columns(2)

    with colu1:
        dis_map_amt(year,quater)
        dis_map_count(year,quater)
    with colu2:
        dis_bar_amt(year,quater)
        dis_bar_count(year,quater)

    dis_bar_brand(year,quater)

    state_name=st.selectbox('**State**',('Andaman & Nicobar', 'Andhra Pradesh', 'Arunachal Pradesh',
       'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh',
       'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Goa',
       'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir',
       'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep',
       'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
       'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan',
       'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
       'Uttarakhand', 'West Bengal'))
    
    dis_state_bar(year,quater,state_name)

with tab3:
    cols1, cols2,cols3  = st.columns(3)
    
    with cols1:
        year=st.selectbox("**YEAR**",("All",2018,2019,2020,2021,2022,2023))

    with cols2:
        if year=="All":
            month=st.selectbox("**MONTH**",("All"," "))
        elif year==2023:
            month= st.selectbox('**MONTH**',("All","Jan-Mar","Apr-Jun","Jul-Sep"))
        else:
            month= st.selectbox('**MONTH**',("All","Jan-Mar","Apr-Jun","Jul-Sep","Oct-Dec"))

        if month=="Jan-Mar":
            quater=1
        elif month=="Apr-Jun":
            quater=2
        elif month=="Jul-Sep":
            quater=3
        elif month=="Oct-Dec":
            quater=4
        else:
            quater="All"

    with cols3:
         option=st.selectbox('TOP 10',("States","Districts","Pincodes"))

    colum1,colum2=st.columns(2)

    with colum1:
         top_count(year,quater,option)
         top_users(year,quater,option)
    with colum2:
        top_amount(year,quater,option)
        dis_pie(year,quater)
    