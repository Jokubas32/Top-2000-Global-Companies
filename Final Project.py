from os import lstat

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk

default_market_value = 150
default_profit = 10

# read in data
def read_data():
    return pd.read_csv("Data.csv").set_index('Company')

# filter data
def filter_data(sel_continents, max_market_value, min_profit):
    df = read_data()
    df = df.loc[df['Continent'].isin(sel_continents)]
    df = df.loc[df['Market Value ($billion)'] < max_market_value]
    df = df.loc[df['Profits ($billion)'] > min_profit]

    return df

# print(data['Market Value ($billion)'])


# count the frequency of continents

def all_continents():
    df = read_data()
    list = []
    for ind, row in df.iterrows():
        if row['Continent'] not in list:
            list.append(row['Continent'])
    return list

def geo_division(continent, df):
    return [df.loc[df['Continent'].isin([continent])].shape[0] for continent in continent]

def continent_averages(dict_sales):
    dict = {}
    for key in dict_sales.keys():
        dict[key] = np.mean(dict_sales[key])

    return dict


def continent_sales(df):
    # loop
    sales = [row['Sales ($billion)'] for ind, row in df.iterrows()]
    continents = [row['Continent'] for ind, row in df.iterrows()]

    dict = {}
    for continent in continents:
        dict[continent] = []

    for i in range(len(sales)):
            dict[continents[i]].append(sales[i])

    return dict

# pie chart
def gen_pie_chart(counts, sel_continents):
    plt.figure

    explodes = [0 for i in range(len(counts))]

    maximum = counts.index(np.max(counts))
    explodes[maximum] = 0.2
    plt.pie(counts, labels=sel_continents, explode= explodes, autopct = "%.2f")
    plt.title(f"Geographical Division: {','.join(sel_continents)}")
    return plt

# baar chart

def gen_bar_chart(dict_averages):
    plt.figure()

    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y)
    plt.xticks(rotation=45)
    plt.ylabel("Sales")
    plt.xlabel("Continents")
    plt.title(f"Average Sale per Continent: {','.join(dict_averages.keys())}")

    return plt

def gen_map(df):
    map_df = df.filter(['Company', 'Latitude' , 'Longitude'])

    view_state = pdk.ViewState(latitude=map_df['Latitude'].mean(),
                               longitude=map_df['Longtitude'].mean(),
                               zoom = 2)
    layer = pdk.Layer('ScaterplotLayer',
                      data=map_df,
                      get_position='[logitude, latitude]',
                      get_radius=5000000,
                      get_color = [50, 200, 250],
                      pickable=True)

    tool_tip = {'html': 'Listing:<br> <b>{name}</b', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initilal_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
    st.pydeck_chart(map)


def main():
    st.title("Data Visualization with Python")
    st.write("Welcome to this Top 2000 Compnaies data! Open the side bar to begin")

    st.sidebar.write("Please choose your options to display data")
    continents =st.sidebar.multiselect("Select a continent: ", all_continents())
    max_market_value =st.sidebar.slider("Max Market Value: ", 0, 100000)
    min_profit = st.sidebar.slider("Min Profit: ", 0, 100000)

    data = filter_data(continents, max_market_value, min_profit)
    series = geo_division(continents,data)

    if len(continents) > 0 and max_market_value > 0 and min_profit > 0:
        st.write("View a map of listings")
        gen_map(data)

        st.write("View a pie chart")
        st.pyplot(gen_pie_chart(series, continents))

        st.write("View a bar chart")
        st.pyplot(gen_bar_chart(continent_averages(continent_sales(data))))

# main()
#
# data = filter_data(default_continents,default_market_value,default_profit)
# counts = geo_division(default_continents,data)
#
# # st.pyplot(gen_pie_chart(counts, default_continents))
# sales = continent_sales(data)
# averages = continent_averages(sales)
#
# # st.pyplot(gen_bar_chart(averages))
# gen_map(data)

# map doesnt work