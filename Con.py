""" Name: Jokubas Skurdenis
    CS230: CS230-6
    Data: Top 2000 Companies Globally
    Description:The code creates a Streamlit dashboard that visualizes data about the world’s top 2000 companies
    using pie charts, bar charts, Seaborn plots, and an interactive map. It allows users to explore company financials
    and locations by selecting metrics and navigating between a data table, dashboard, and map view.

"""

import pandas as pd #manipulation
import matplotlib.pyplot as plt #plots
import numpy as np #numerical operations
import streamlit as st #web
import folium #map
from streamlit_folium import st_folium #redner folium map
import seaborn as sns #Stats

# Went in for help at CIS Lab because it wasn't running at first
def read_data():
    data = pd.read_csv("Top2000CompaniesGlobally.csv")  # No full path
    columns = data.columns.tolist()
    return data, columns


# Show company count by continent on the dashboard
def show_company_counts(data):
    continent_counts = data["Continent"].value_counts().to_dict()  # Count companies per continent
    st.subheader("Number of Companies by Continent")
    for continent, count in continent_counts.items(): #Dictionary
        st.write(f"{continent}: {count} companies")

def gen_pie_chart(data):
    selected_continents = st.multiselect("Select continents for pie chart",
        options=["Africa", "Asia", "Europe", "North America", "South America", "Oceania"],
        default=["Africa", "Asia", "Europe", "North America", "South America", "Oceania"])

    metric = st.selectbox("Select metric for pie chart", options=["Sales ($billion)", "Profits ($billion)", "Assets ($billion)", "Market Value ($billion)"])

    pie_data = data[data["Continent"].isin(selected_continents)]  # Filter data for selected continents
    avg_values = pie_data.groupby("Continent")[metric].mean()

    # referenced the video for the rest
    max_index = np.argmax(avg_values.values) #enlarge the slice (max val)
    explodes = [0.2 if i == max_index else 0 for i in range(len(avg_values))] #List comprehension

    # Plot pie chart
    try:
        plt.figure(figsize=(8, 8)) #size 8 inches by 8
        plt.pie(avg_values, labels=avg_values.index, explode=explodes, autopct="%.2f") #actual num, names of cont., which to pop, decimals
        plt.title("Average " + " ".join(metric.split()[:-1]) + " by Continent")
        st.pyplot(plt)
    except Exception as e:
        st.error(f"Error generating pie chart: {e}")


def gen_bar_chart(data):
    st.subheader("Company Comparison Bar Chart")
    metric = st.selectbox("Select metric to display:",["Assets ($billion)", "Market Value ($billion)", "Profits ($billion)", "Sales ($billion)","Profit Margin (%)"])
    sort_order = st.selectbox("Select sort order:", ["Top 20 (Descending)", "Bottom 20 (Ascending)"])

    filtered_data = data.dropna(subset=["Company", "Sales ($billion)", "Profits ($billion)"]) #remove missing values from data

    if metric == "Profit Margin (%)":
        filtered_data = filtered_data[filtered_data["Sales ($billion)"] > 0]
        filtered_data["Profit Margin (%)"] = filtered_data.apply(lambda row: (row["Profits ($billion)"] / row["Sales ($billion)"]) * 100,axis=1) #each row

    if filtered_data.empty or metric not in filtered_data.columns:
        return

    if sort_order == "Bottom 20 (Ascending)":
        ascending = True
    else:
        ascending = False

    top_companies = filtered_data.sort_values(by=metric, ascending=ascending).head(20)

    plt.figure(figsize=(10, 8))
    #horizontal chart (used ChatGPT help)
    plt.barh(top_companies["Company"], top_companies[metric], color='skyblue') #names on y axis, length of each bar
    plt.xlabel(metric) #x axis
    title_order = "Lowest" if ascending else "Top"
    plt.title(f"{metric} of {title_order} 20 Global Companies")
    plt.gca().invert_yaxis() #reverse y axis --> largest at the top
    plt.tight_layout()
    st.pyplot(plt)


def gen_seaborn_charts(data):
    st.subheader("Seaborn Visualizations")
    st.write("These visualizations help reveal deeper trends across the dataset."
             " You’ll find relationships between sales and profits by continent, and see how company assets vary across regions.")

    st.subheader("Sales vs Profits by Continent")
    st.write("This scatter plot shows how much companies are selling (sales) compared to how much they are earning (profits). Each dot is a company, and colors show which continent it belongs to.")
    fig1, ax1 = plt.subplots() #size
    sns.scatterplot(data=data, x="Sales ($billion)", y="Profits ($billion)", hue="Continent")
    ax1.set_title("Sales vs Profits (colored by Continent)")
    st.pyplot(fig1)

    st.subheader("Assets Distribution by Continent")
    st.write("This box plot shows how company assets vary by continent. It helps you see which regions have companies with the most or least assets overall.")
    fig2, ax2 = plt.subplots()
    sns.boxplot(data=data, x="Continent", y="Assets ($billion)")
    ax2.set_title("Assets by Continent")
    st.pyplot(fig2)

def gen_map(data):
    # Required columns
    required_cols = ['Latitude_final', 'Longitude_final', 'Company', 
                     'Sales ($billion)', 'Profits ($billion)', 'Market Value ($billion)']

    # Check if all required columns exist
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"Missing required columns in dataset: {', '.join(missing_cols)}")
        return

    # Drop rows with missing values in required columns
    companies_with_coords = data.dropna(subset=required_cols)

    # Create map
    m = folium.Map(location=[20, 0], zoom_start=2)

    for i, row in companies_with_coords.iterrows():
        folium.Marker(
            location=[row['Latitude_final'], row['Longitude_final']],
            popup=row['Company']
        ).add_to(m)

    st_folium(m, width=700)

    # Add markers to the map for each company
    for company_index, company_details in companies_with_coords.iterrows():
        company_name = company_details['Company']
        company_sales = company_details['Sales ($billion)']
        company_market_value = company_details['Market Value ($billion)']
        company_profits = company_details['Profits ($billion)']
        company_latitude = company_details['Latitude_final']
        company_longitude = company_details['Longitude_final']

        popup_info = (
            f"Company: {company_name}\n"
            f"Sales: ${company_sales:,.2f} Billion\n"
            f"Market Value: ${company_market_value:,.2f} Billion\n"
            f"Profits: ${company_profits:,.2f} Billion"
        )

        # Add a CircleMarker for each company
        folium.CircleMarker(
            location=[company_latitude, company_longitude],
            radius=5,
            color='blue',
            fill=True,
            fill_color='skyblue',
            fill_opacity=0.7,
            tooltip=popup_info
        ).add_to(m)

    st_folium(m, width=700, height=500)

def main():
    st.set_page_config(page_title="Global Companies Dashboard", layout="centered")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Data Table", "Dashboard", "Map"])

    df, num_rows = read_data()
    if df.empty:
        return

    if page == "Data Table":
        st.title("Company Dataset")
        st.write("This table displays the top 2000 global companies along with key financial metrics, "
                 "such as sales, profits, assets, market value, and geographic location. "
                 "You can scroll and search to explore company-specific details.")
        st.dataframe(df)

        st.header("Visualize Company Metrics")
        st.write("Use the bar chart below to compare various financial metrics between the top 20 companies. "
                 "You can switch between metrics like assets, market value, sales, profits, and calculated profit margin. "
                 "This helps in understanding which companies lead in specific financial areas.")
        gen_bar_chart(df)

    elif page == "Dashboard":
        st.title("Top Global Companies Dashboard")
        st.write("Explore the world’s largest companies by continent, sales, assets, and more!")

        show_company_counts(df)
        st.header("Average Metric by Continent")
        gen_pie_chart(df)

        gen_seaborn_charts(df)

    elif page == "Map":
        st.title("Interactive Company Map")
        gen_map(df)

if __name__ == "__main__":
    main()

