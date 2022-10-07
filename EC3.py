# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 09:46:40 2022

@author: emman
"""

import streamlit as st
from PIL import Image
import copy
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models,expected_returns,plotting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from binance import Client
from PIL import Image
import datetime
import plotly.express as px
import math


#Codes analyses Colab
aapl = yf.download("AAPL", start="2017-05-23", end="2022-05-23")
fb =  yf.download("META", start="2017-05-23", end="2022-05-23")
gg = yf.download("GOOG", start="2017-05-23", end="2022-05-23")
msft = yf.download("MSFT", start="2017-05-23", end="2022-05-23")
amzn = yf.download("AMZN", start="2017-05-23", end="2022-05-23")
amzn["Entreprise"] = "AMAZON"
aapl["Entreprise"] = "APPLE"
fb["Entreprise"] = "FACEBOOK"
gg["Entreprise"] = "GOOGLE"
msft["Entreprise"] = "MICROSOFT"
data = pd.concat([amzn,aapl,fb,gg,msft])
data["Date"] = data.index
data["Date"] = pd.to_datetime(data['Date'])
data.info()
data["Année"] = data['Date'].dt.year
data_2022 = data.loc["2022"]
data_2020 = data.loc["2020"]
data_2017 = data.loc["2017"]

dataClose=data[['Adj Close','Entreprise']]
dataClose=dataClose.pivot_table(index=dataClose.index,values='Adj Close',columns='Entreprise')
RetourInvestJournalier=dataClose.pct_change(1)
RetourInvestJournalier100=RetourInvestJournalier.mean().mul(100)
RetourInvestAnnuel=RetourInvestJournalier.mean()*252
RetourInvestAnnuel=RetourInvestAnnuel.sort_values(ascending = False)
RisqueAnnuel=RetourInvestJournalier.std()*math.sqrt(252)
dataRetourInvestissementAnnuel = pd.DataFrame()
dataRetourInvestissementAnnuel['Retour Investissement Annuel Souhaité']=RetourInvestAnnuel
dataRetourInvestissementAnnuel['Risque Investissement Annuel Souhaité']=RisqueAnnuel
dataRetourInvestissementAnnuel['Entreprise']=RetourInvestAnnuel.index
dataRetourInvestissementAnnuel['Ratio']=dataRetourInvestissementAnnuel['Retour Investissement Annuel Souhaité']/dataRetourInvestissementAnnuel['Risque Investissement Annuel Souhaité']
dataRetourInvestissementAnnuel=dataRetourInvestissementAnnuel.sort_values(by='Ratio',axis=0,ascending=False,inplace=False)
stocks = pd.concat([aapl['Adj Close'], amzn['Adj Close'], gg['Adj Close'], msft['Adj Close'], fb['Adj Close']], axis = 1)
stocks.columns = ['Apple', 'Amazon', 'Google', 'Microsoft', 'Facebook']
stocks.pct_change(1).mean()
stocks.pct_change(1).corr()
log_returns = np.log(stocks/stocks.shift(1))


st.set_page_config(page_title="Projet DA", page_icon="📊",layout="centered", initial_sidebar_state="auto")
st.title('OPA : Online Portfolio Allocation')
st.text("19/10/2022")
st.sidebar.title('Navigation')
options=st.sidebar.radio('',options=['Présentation du projet','Dataset','Exploration des données','Analyse','Complément CAC40',
                        'Simulateur de portefeuille 🔢'])
with st.sidebar:
  st.header("Promotion Formation Continue Mars 2022")
  
  st.write("Participants:")
  st.write("Emmanuelle Cuminal")
  st.write("Cécile XIE")
if options == 'Présentation du projet':
    image = Image.open('C:/Users/emman/Documents/GitHub/OPA-STREAMLIT/image/photo page garde stockmarket.jpg')
    new_image = image.resize((600, 200))
    st.image(new_image)
    st.header("Analyse de protefeuille d'actions en ligne")
    st.subheader("Contexte")
    st.write("Nous avons décidé d’analyser les actions émises par les GAFAM (Google, Apple, Facebook, Amazon, Microsoft) depuis 5 ans. Ces géants du web battent tous les records depuis plusieurs années, ils ont su s’imposer sur le marché en tant qu’acteur indispensable de la vie économique mondiale. Ils ne cessent de repenser nos habitudes. Ces entreprises sont à l’origine de tout un éventail de produits et de services faisant partie intégrante du quotidien de milliards de personnes. Ils représentent à eux seuls une richesse sans précédent (5,9 trillions de dollars de capitalisation boursière).")
    st.subheader("Problématique ")
    st.write("Comment investir en Bourse dans les géants de la tech américaine (GAFAM) ? Suite à l’explosion des services numériques due à la crise sanitaire du covid19, les GAFAM ont performé dans leurs activités et en bourse. Nous allons dans un premier temps analyser l'évolution boursière des GAFAM puis nous mettrons en place un modèle de répartition optimal de portefeuille 100% GAFAM, et pour finir nous analyserons ces résultats en fonction des prévisions sur les prochaines années. ")
    st.subheader("Comment investir dans les GAFAM ? 📈 ") 
if options == 'Dataset':
    st.header('Collecte des données')
    st.write("Nous avons téléchargé les données le 23/05/2022 sur le site de Yahoo Finance, soit cinq fichiers sur 5 ans, du 23/05/2017 au 23/05/2022 : ")
    st.write("- “GOOGL.csv” pour Google")
    st.write("- “AMZN.csv” pour Amazon ")
    st.write("- “FB.csv” pour Metaverse (Facebook)")
    st.write("- “AAPLL.csv” pour Apple ")
    st.write("- “MSFT.csv” POUR Microsoft ")
    st.write("Puis nous avons fusionné les 5 dataframes.")
    st.write("Ainsi, nous avons les donées sur le cours des actions des 5 entreprises sur 5 ans par jour")
    st.write(data.head(10))
    st.header('Etapes de nettoyage des données :')
    st.write("- Fusion des 5 DF ")
    st.write("- Check des données manquantes")
    st.write("- Modifier les formats de données comme pour la date")

if options == 'Exploration des données':
    st.subheader(" Le volume d’actions par GAFAM par année") 
    fig = px.bar(data, x="Année", y="Volume",color="Entreprise", barmode = 'group')
    st.write(fig)
    st.write("On note un pic commun en 2018 puis 2020. Depuis 2022 le volume d'actions diminue. Apple vend le plus d'actions et de loin, plus de 2,5 fois plus que son plus proche concurrent Microsoft. Mais le volume d'Apple a considérablement baissé depuis 2020. Ensuite suit Facebook puis avec beaucoup moins de volume il y a Amazon, puis Google.")
    fig = data['Volume'].plot(figsize=(20,8))
    st.write(fig)
    st.subheader("L'Evolution des prix par entreprise sur 5 ans")
    fig = plt.figure(figsize=(12,8))
    amzn["Adj Close"].plot(linewidth=2)
    msft["Adj Close"].plot(linewidth=2)
    gg["Adj Close"].plot(linewidth=2)
    fb["Adj Close"].plot(linewidth=2)
    aapl["Adj Close"].plot(linewidth=2)
    plt.legend(['Amazon','Microsoft','Google','Facebook','Apple'])
    plt.xticks(fontsize = 12)                          
    plt.yticks(fontsize = 12)
    plt.xlabel('Années')
    plt.ylabel('Adj Close')
    st.write(fig)
    st.write("Amazon enregistre la valeur la plus haute, suivi par Google. Les autres entreprises sont bien plus basses.Apple qui émet le plus d’actions a une valeur très basse par rapport aux autres GAFAM.Pour analyser les prix nous nous sommes basées sur la variable “Adj Close” car elle représente le prix final de l’action émise. En effet, la clôture ajustée est le cours de clôture après les ajustements pour tous les fractionnements et distributions de dividendes applicables. Les données sont ajustées à l'aide de multiplicateurs de fractionnement et de dividendes appropriés, conformément aux normes du Centre de recherche sur les prix des titres (CRSP).")

    st.subheader(" Evolution du cours le plus haut par entreprise")
    st.write("graph normalisation problème")

    
    
    st.write("Microsoft performe même si Amazon est plus haut à certaines périodes, suivie de très près par Apple qui décolle et concurrence Microsoft en dernière période.")
    
    st.subheader(" Répartition des actions GAFAM")
    
    fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'},{'type':'domain'}]])
    fig.add_trace(go.Pie(labels=data_2022['Entreprise'], values=data_2017['Volume'], name="17"),
              1, 1)
    fig.add_trace(go.Pie(labels=data_2020['Entreprise'], values=data_2020['Volume'], name="20"),
              1, 2)
    fig.add_trace(go.Pie(labels=data_2022['Entreprise'], values=data_2022['Volume'], name="22"),
              1, 3)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='2017', x=0.10, y=0.5, font_size=20, showarrow=False),
                 dict(text='2020', x=0.50, y=0.5, font_size=20, showarrow=False),
                 dict(text='2022', x=0.89, y=0.5, font_size=20, showarrow=False)])
    st.write(fig)
    
    
    
    st.write("2017 vs 2022 : Facebook a perdu une forte part alors que Apple connaît une importante hausse.")
    st.write("2020 vs 2022 : Apple émet toujours le plus d'actions mais en baisse depuis 2020 au détriment de Facebook qui a doublé sa part en 2 ans. Microsoft a légèrement augmenté sa part de marché.")
    
    st.header("Conclusions ")
    st.write("Les actions les plus chères, soit Amazon et Google semblent ne pas bouger en part de portefeuille GAFAM depuis 5 ans, alors que Apple et Facebook gagnent puis perdent des parts, Microsoft est stable avec une part qui augmente doucement. Mais alors vaut il mieux investir plus cher pour moins d’actions ou l’inverse ?")
    st.write("Dans un premier temps, on peut observer le comportement des investisseurs, quels facteurs externes les poussent à acheter telle actions plutôt qu'une autre. Et quels sont les critères à prendre en compte avant d’investir dans les GAFAM. Nous pouvons également analyser les prédictions. ")
    st.write("Il serait également intéressant d’estimer le portefeuille possédant le plus faible taux possible de risque, pour un rendement maximum.  ")

if options =="Analyse"  :
    st.write(dataRetourInvestissementAnnuel)
    fig= plt.figure(figsize = (5, 5))
    plt.scatter("Risque Investissement Annuel Souhaité", "Retour Investissement Annuel Souhaité",data = dataRetourInvestissementAnnuel,s=200)
    plt.xticks(fontsize = 12)                          
    plt.yticks(fontsize = 12)                          
    plt.ylabel('Retour Investissement', fontsize = 12, color="green")           
    plt.xlabel("Risque", fontsize = 12, color="orange")                  
    plt.title("Positionnement risque/rendement", fontsize = 15,color="blue") 
    
    for i, j in enumerate (dataRetourInvestissementAnnuel['Entreprise'].unique()):
        plt.annotate(j,(dataRetourInvestissementAnnuel['Risque Investissement Annuel Souhaité'][i], dataRetourInvestissementAnnuel['Retour Investissement Annuel Souhaité'][i]))   
    st.write(fig)
    st.write("Ajouter code risque et rendement avec options Cecile")
    Etude= st.selectbox("Analyse",
                            ['Equilibre', 'Risque', 'Rentabilité']) 
    if Etude == "Equilibre":
        np.random.seed(101)
        weights = np.array(np.random.random(5))
        weights = weights/np.sum(weights)
        num_ports = 1000
        all_weights = np.zeros((num_ports,len(stocks.columns)))
        ret_arr = np.zeros(num_ports)
        vol_arr = np.zeros(num_ports)
        sharpe_arr = np.zeros(num_ports)
        for ind in range(num_ports):
            weights = np.array(np.random.random(5))
            weights = weights / np.sum(weights)
            all_weights[ind,:] = weights
            ret_arr[ind] = np.sum((log_returns.mean() * weights) *252)
            vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
            sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
        st.subheader("Portefeuille optimal")
        fig = make_subplots()
        fig.add_trace(go.Pie(labels=['Apple', 'Amazon', 'Google', 'Microsoft', 'Facebook'], values=all_weights[sharpe_arr.argmax(),:]))
        st.write(fig)
        st.write('Microsoft et Apple représentent la majorité des actions, soit 90% du portefeuille  à eux deux.')
        st.subheader("Sharpe ratio")
        st.write(sharpe_arr.max())
        st.write("Inférieur à 1 donc pas rentable")
        
        

if options =="Complément CAC40"  :
        st.write("Le sharpe ratio optimal pour un portefeuille 100% GAFAM est inférieur à 1, ce qui montre que quelque soit l’allocation de ce portefeuille, il ne sera pas rentable par rapport à la période actuelle. Ainsi nous avons décidé d’approfondir notre analyse en incluant les entreprises du CAC40 à notre recherche de portefeuille optimal.") 
        Actions = st.selectbox("Actions",
                                ['39 entreprises', 'Top15', 'Top5'])
        if Actions == "39 entreprises" :
            ticker2 = ("AAPL","META","MSFT","AIR.PA","STM.PA","ML.PA","DSY.PA","ERF.PA","LR.PA","ALO.PA",
          "ENGI.PA","ORA.PA","RNO.PA","BNP.PA","GLE.PA","PUB.PA","VIV.PA","DG.PA",
          "CAP.PA","SGO.PA","VIE.PA","SU.PA","EL.PA","KER.PA","HO.PA","MC.PA","RI.PA","BN.PA",
          "CS.PA","SAN.PA","EN.PA","OR.PA","TTE.PA","CA.PA","AI.PA","SAF.PA","RMS.PA","TEP.PA","ACA.PA")
            data40_v2 = yf.download(ticker2,start="2017-1-1")['Adj Close']
            np.random.seed(101)
            data40_v2.pct_change(1).mean()
            data40_v2.pct_change(1).corr()
            log_returns = np.log(data40_v2/data40_v2.shift(1))
            weights = np.array(np.random.random(39))
            weights_ = weights/np.sum(weights)
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            SR = exp_ret/exp_vol
            num_ports = 500
            all_weights = np.zeros((num_ports,len(data40_v2.columns)))
            ret_arr = np.zeros(num_ports)
            vol_arr = np.zeros(num_ports)
            sharpe_arr = np.zeros(num_ports)
            for ind in range(num_ports):
                weights = np.array(np.random.random(39))
                weights = weights / np.sum(weights)
                all_weights[ind,:] = weights
                ret_arr[ind] = np.sum((log_returns.mean() * weights) *252)
                vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
                sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
            st.subheader("Sharpe ratio optimal")
            st.write(sharpe_arr.max())
            if sharpe_arr.max()>=1 :
                st.success("Portefeuille rentable")
            elif 0<sharpe_arr.max()<1 :
                st.warning("Portefeuille non rentable")
            else :
                st.error("Attention")

            st.subheader("Répartition")
            fig = make_subplots()
            fig.add_trace(go.Pie(labels=["AAPL","META","MSFT","AIR.PA","STM.PA","ML.PA","DSY.PA","ERF.PA","LR.PA","ALO.PA",
          "ENGI.PA","ORA.PA","RNO.PA","BNP.PA","GLE.PA","PUB.PA","VIV.PA","DG.PA",
          "CAP.PA","SGO.PA","VIE.PA","SU.PA","EL.PA","KER.PA","HO.PA","MC.PA","RI.PA","BN.PA",
          "CS.PA","SAN.PA","EN.PA","OR.PA","TTE.PA","CA.PA","AI.PA","SAF.PA","RMS.PA","TEP.PA","ACA.PA"], values=all_weights[sharpe_arr.argmax(),:]))
            st.write(fig)     

        if Actions == "Top15" :
            ticker3 = ("AAPL", "AIR.PA","STM.PA","KER.PA","ALO.PA","TEP.PA","CS.PA","AI.PA","RNO.PA","SAF.PA","SGO.PA", "ORA.PA" , "DG.PA" , "BN.PA" , "OR.PA")
            data40_v3 = yf.download(ticker3,start="2017-1-1")['Adj Close']
            np.random.seed(101)
            data40_v3.pct_change(1).mean()
            data40_v3.pct_change(1).corr()
            log_returns = np.log(data40_v3/data40_v3.shift(1))
            weights = np.array(np.random.random(15))
            weights_ = weights/np.sum(weights)
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            SR = exp_ret/exp_vol
            num_ports = 500
            all_weights = np.zeros((num_ports,len(data40_v3.columns)))
            ret_arr = np.zeros(num_ports)
            vol_arr = np.zeros(num_ports)
            sharpe_arr = np.zeros(num_ports)
            for ind in range(num_ports):
                weights = np.array(np.random.random(15))
                weights = weights / np.sum(weights)
                all_weights[ind,:] = weights
                ret_arr[ind] = np.sum((log_returns.mean() * weights) *252)
                vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
                sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
            st.subheader("Sharpe ratio optimal")
            st.write(sharpe_arr.max())
            if sharpe_arr.max()>=1 :
                st.success("Portefeuille rentable")
            elif 0<sharpe_arr.max()<1 :
                st.warning("Portefeuille non rentable")
            else :
                st.error("Attention")
            st.subheader("Répartition")
            fig = make_subplots()
            fig.add_trace(go.Pie(labels=["AAPL", "AIR.PA","STM.PA","KER.PA","ALO.PA","TEP.PA","CS.PA","AI.PA","RNO.PA","SAF.PA","SGO.PA", "ORA.PA" , "DG.PA" , "BN.PA" , "OR.PA"], values=all_weights[sharpe_arr.argmax(),:]))
            st.write(fig)     
        if Actions == "Top5" :
            ticker4 = ("AAPL", "AIR.PA","AI.PA","TEP.PA","RNO.PA")
            data40_v4 = yf.download(ticker4,start="2017-1-1")['Adj Close']
            np.random.seed(101)
            data40_v4.pct_change(1).mean()
            data40_v4.pct_change(1).corr()
            log_returns = np.log(data40_v4/data40_v4.shift(1))
            weights = np.array(np.random.random(5))
            weights_ = weights/np.sum(weights)
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            exp_ret = np.sum((log_returns.mean() * weights) * 252)
            exp_vol = np.sqrt(np.dot(weights.T,np.dot(log_returns.cov() * 252, weights)))
            SR = exp_ret/exp_vol
            num_ports = 500
            all_weights = np.zeros((num_ports,len(data40_v4.columns)))
            ret_arr = np.zeros(num_ports)
            vol_arr = np.zeros(num_ports)
            sharpe_arr = np.zeros(num_ports)
            for ind in range(num_ports):
                weights = np.array(np.random.random(5))
                weights = weights / np.sum(weights)
                all_weights[ind,:] = weights
                ret_arr[ind] = np.sum((log_returns.mean() * weights) *252)
                vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
                sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
            st.subheader("Sharpe ratio optimal")
            st.write(sharpe_arr.max())
            if sharpe_arr.max()>=1 :
                st.success("Portefeuille rentable")
            elif 0<sharpe_arr.max()<1 :
                st.warning("Portefeuille non rentable")
            else :
                st.error("Attention")
            st.subheader("Répartition")
            fig = make_subplots()
            fig.add_trace(go.Pie(labels=["AAPL", "AIR.PA","STM.PA","KER.PA","ALO.PA","TEP.PA","CS.PA","AI.PA","RNO.PA","SAF.PA","SGO.PA", "ORA.PA" , "DG.PA" , "BN.PA" , "OR.PA"], values=all_weights[sharpe_arr.argmax(),:]))
            st.write(fig) 
            
if options == "Simulateur de portefeuille 🔢" : 
    st.write("Analyse sur les actions GAFAM + CAC40")

    #Récupérer les actions CAC40 sur yahoo



    ticker = ("AAPL","MSFT","AIR.PA","STM.PA","ML.PA","DSY.PA","ERF.PA","LR.PA","ALO.PA",
          "ENGI.PA","ORA.PA","RNO.PA","BNP.PA","GLE.PA","PUB.PA","VIV.PA","DG.PA",
          "CAP.PA","SGO.PA","VIE.PA","SU.PA","EL.PA","KER.PA","HO.PA","MC.PA","RI.PA","BN.PA",
          "CS.PA","SAN.PA","EN.PA","OR.PA","TTE.PA","CA.PA","AI.PA","SAF.PA","RMS.PA","TEP.PA","ACA.PA")
    
    dropdown = st.multiselect('Choisissez vos actions',ticker)
    st.write("Historique à analyser, sélectionnez les dates")
    start = st.date_input('Start',value=pd.to_datetime('2017-01-01'))
    end = st.date_input('End',value=pd.to_datetime('today'))

    
    def relativeret(df):
        rel=df.pct_change()
        cumret = (1+rel).cumprod()-1
        cumret = cumret.fillna(0)
        return cumret

    st.subheader("L'évolution des actions")
    if len(dropdown)>0:
        df=yf.download(dropdown,start,end)['Adj Close']
        st.line_chart(df)
    

    st.subheader("L'évolution relative entre les actions")
    if len(dropdown)>0:
        dfnorm=relativeret(df)
        st.line_chart(dfnorm)

    
    # Profil investisseur/option
    Profil = st.selectbox("Quel type d'investisseur êtes-vous : ",
                         ['Prudent 🦺', 'Equilibré ⚖️', 'Dynamique 🔥'])
     
    # curseur montant
    level = st.slider("Montant à investir", 100, 10000)

    if(st.button("Je découvre mon portefeuille optimal")):
        if Profil == "Prudent 🦺":
            st.subheader("La répartition de portefeuille en stratégie prudente:")  
            mu = expected_returns.mean_historical_return(df)
            s = risk_models.sample_cov(df)
            ef_risqmin=EfficientFrontier(mu,s)
            weight_risqmin=ef_risqmin.min_volatility()
            performanceoption_risqmin=ef_risqmin.portfolio_performance(verbose=True)
            a_risqmin=pd.Series(weight_risqmin.values())
            b_risqmin=pd.Series(weight_risqmin.keys())
            Poids_Action_Option_Prudent_risqmin=pd.DataFrame({'Action':b_risqmin,'Poids Par Action':a_risqmin})
            Poids_Action_Option_Prudent_risqmin=Poids_Action_Option_Prudent_risqmin[Poids_Action_Option_Prudent_risqmin['Poids Par Action']!=0]
            fig = make_subplots()
            fig.add_trace(go.Pie(labels= Poids_Action_Option_Prudent_risqmin['Action'], values=Poids_Action_Option_Prudent_risqmin['Poids Par Action']))
            st.write(fig) 
            st.subheader("La performance de portefeuille en stratégie prudente:")
            Performance_Option_Prudent_risqmin=pd.DataFrame(performanceoption_risqmin,
                                                            index=['Retour','Risque','Sharp Ratio'],
                                                            columns=['Ratio Option Prudent'])
            st.write(Performance_Option_Prudent_risqmin)
          
            
        if Profil == "Dynamique 🔥":
            st.subheader("La répartition de portefeuille en stratégie dynamique:")   
            mu = expected_returns.mean_historical_return(df)
            s = risk_models.sample_cov(df)
            ef_rentmax=EfficientFrontier(mu,s)
            weight_rentmax=ef_rentmax.max_sharpe()
            performanceoption_rentmax=ef_rentmax.portfolio_performance(verbose=True)
            a_rentmax=pd.Series(weight_rentmax.values())
            b_rentmax=pd.Series(weight_rentmax.keys())
            Poids_Action_Option_Dynamique_rentmax=pd.DataFrame({'Action':b_rentmax,'Poids Par Action':a_rentmax})
            Poids_Action_Option_Dynamique_rentmax=Poids_Action_Option_Dynamique_rentmax[Poids_Action_Option_Dynamique_rentmax['Poids Par Action']!=0]
            fig = make_subplots()
            fig.add_trace(go.Pie(labels= Poids_Action_Option_Dynamique_rentmax['Action'], values=Poids_Action_Option_Dynamique_rentmax['Poids Par Action']))
            st.write(fig)             
            
        if Profil == "Equilibré ⚖️":  
            st.subheader("Votre selection en stratégie équilibré:")
            returns_portfolio = df.pct_change()
            log_returns = np.log(df/df.shift(1))
            num_ports = 500
            all_weights = np.zeros((num_ports,len(df.columns)))
            ret_arr = np.zeros(num_ports)
            vol_arr = np.zeros(num_ports)
            sharpe_arr = np.zeros(num_ports)
            for ind in range(num_ports):
                weights = np.array(np.random.random(len(df.columns)))
                weights = weights / np.sum(weights)
                all_weights[ind,:] = weights
                ret_arr[ind] = np.sum((log_returns.mean() * weights) *252)
                vol_arr[ind] = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
                sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]
            st.write('Sharp Ratio optimisé par stratégie équilibré',round(sharpe_arr.max(),2))
            st.subheader('La répartition de portefeuille en stratégie équilibré:')
            label=df.columns.to_list()
            repart_equil=pd.DataFrame({'Action':label,'Poids Par Action':all_weights[sharpe_arr.argmax(),:]})
            fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'},{'type':'domain'}]])
            fig.add_trace(go.Pie(labels=label, values=all_weights[sharpe_arr.argmax(),:]))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader('Visualisation du sharpe ratio par rapport au rendement/risque')
            #graphique
            fig=plt.figure(figsize = (12,8))
            plt.scatter(vol_arr,ret_arr,c=sharpe_arr,cmap='Spectral')
            plt.colorbar(label='Sharpe Ratio')
            plt.xlabel('Volatility')
            plt.ylabel('Return')

             # Add red dot for max SR
            max_sr_ret = ret_arr[sharpe_arr.argmax()]
            max_sr_vol = vol_arr[sharpe_arr.argmax()]
            plt.scatter(max_sr_vol,max_sr_ret,c='red',s=50,edgecolors='black',label='Option équilibré')
            plt.legend()
            st.pyplot(fig)           
         




    
    