import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Function to create a connection to the database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="kubela.id",
            user="davis2024irwan",
            passwd="wh451n9m@ch1n3",
            port=3306,  
            database="aw"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Function to fetch data based on selected country
def fetch_data(country=None):
    dataBase = create_connection()
    if dataBase is None:
        return pd.DataFrame()
    cursor = dataBase.cursor()

    # Query to fetch data
    base_query = """
    SELECT dc.YearlyIncome, SUM(fis.SalesAmount) as TotalSales
    FROM factinternetsales fis
    JOIN dimcustomer dc ON fis.CustomerKey = dc.CustomerKey
    JOIN dimsalesterritory dst ON fis.SalesTerritoryKey = dst.SalesTerritoryKey
    {}
    GROUP BY dc.YearlyIncome
    """
    
    if country:
        query = base_query.format(f"WHERE dst.SalesTerritoryCountry = '{country}'")
    else:
        query = base_query.format("")

    try:
        cursor.execute(query)
        data = pd.DataFrame(cursor.fetchall(), columns=['YearlyIncome', 'TotalSales'])
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        data = pd.DataFrame()
    finally:
        cursor.close()
        dataBase.close()
    
    return data

# Function to fetch available countries
def fetch_countries():
    dataBase = create_connection()
    if dataBase is None:
        return []
    cursor = dataBase.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT SalesTerritoryCountry FROM dimsalesterritory")
        countries = [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        countries = []
    finally:
        cursor.close()
        dataBase.close()
    
    return countries

# Other fetch functions (fetch_sales_data, fetch_treemap_data, etc.) should follow the same pattern...

# Streamlit interface
st.set_page_config(layout="wide")
st.markdown('<h1 style="font-size:30px; text-align:center;">Dashboard Penjualan</h1>', unsafe_allow_html=True)

# Sidebar for selecting country
st.sidebar.title('📊 Dashboard Penjualan')
countries = fetch_countries()
selected_country = st.sidebar.selectbox('Pilih Negara', options=['All'] + countries)

# Fetch data based on selected country
data = fetch_data(country=None if selected_country == 'All' else selected_country)

# Ensure data is valid
if not data.empty:
    # Convert columns to appropriate data types
    data['YearlyIncome'] = data['YearlyIncome'].astype(float)
    data['TotalSales'] = data['TotalSales'].astype(float)

    # Layout of the dashboard
    col1, col2 = st.columns((3, 3))

    with col1:
        # Display scatter plot using Plotly
        st.markdown('<h2 style="font-size:20px; text-align:center;">Hubungan Antara Pendapatan Tahunan dan Total Penjualan</h2>', unsafe_allow_html=True)
        fig = px.scatter(data, x='YearlyIncome', y='TotalSales', color_discrete_sequence=["#543310"])
        st.plotly_chart(fig, use_container_width=True)

        # Fetch sales data based on selected country
        sales_data = fetch_sales_data(country=None if selected_country == 'All' else selected_country)

        # Pivot data for bar chart
        pivot_data = sales_data.pivot_table(index='SalesTerritoryRegion', columns='ProductCategory', values='TotalSales', fill_value=0).reset_index()

        # Display bar chart using Plotly
        st.markdown('<h2 style="font-size:20px; text-align:center;">Penjualan Per Kategori Produk berdasarkan Wilayah Penjualan</h2>', unsafe_allow_html=True)
        fig = px.bar(pivot_data, x='SalesTerritoryRegion', y=pivot_data.columns[1:], color_discrete_sequence=["#543310", "#F8F4E1", "#AF8F6F"])
        st.plotly_chart(fig, use_container_width=True)

        # Fetch data for choropleth map
        choropleth_data = fetch_choropleth_data(country=None if selected_country == 'All' else selected_country)
        sales_territory_regions, total_sales = zip(*choropleth_data.values)

        # Display choropleth map
        st.markdown('<h2 style="font-size:20px; text-align:center;">Total Sales by Sales Territory Region</h2>', unsafe_allow_html=True)
        fig = go.Figure(go.Choropleth(
            locations=sales_territory_regions,  # Menggunakan nama region sebagai locations
            z=total_sales,  # Menentukan nilai yang akan diplot sebagai warna
            locationmode='country names',  # Menggunakan mode nama negara
            colorscale=[[0, "#543310"], [0.5, "#74512D"], [1, "#AF8F6F"]],  # Skala warna yang digunakan
            colorbar_title='Total Sales',  # Judul color bar
        ))

        # Menyeting tampilan layout
        fig.update_layout(
            geo=dict(
                showcoastlines=True,  # Menampilkan garis pantai
                showland=True,  # Menampilkan daratan
                projection_type='mercator'  # Tipe proyeksi (peta dunia)
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Fetch treemap data based on selected country
        treemap_data = fetch_treemap_data(country=None if selected_country == 'All' else selected_country)

        # Display treemap
        st.markdown('<h2 style="font-size:20px; text-align:center;">Treemap Persentase Penjualan per Kategori Produk (Bahasa Inggris)</h2>', unsafe_allow_html=True)
        fig = px.treemap(treemap_data, path=['ProductCategory'], values='TotalSales', color_discrete_sequence=["#543310", "#74512D", "#AF8F6F"])
        st.plotly_chart(fig, use_container_width=True)

        # Fetch order quantity data based on selected country
        order_quantity_data = fetch_order_quantity_data(country=None if selected_country == 'All' else selected_country)

        # Display histogram of order quantities
        st.markdown('<h2 style="font-size:20px; text-align:center;">Distribusi Order Quantity dari factinternetsales</h2>', unsafe_allow_html=True)
        fig = px.histogram(order_quantity_data, x='OrderQuantity', nbins=20, labels={'OrderQuantity': 'Order Quantity'}, color_discrete_sequence=["#543310"])
        fig.update_layout(xaxis_title='Order Quantity', yaxis_title='Frequency', width=600, height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Fetch total order quantity based on selected country
        total_order_quantity = fetch_total_order_quantity(country=None if selected_country == 'All' else selected_country)

        # Display total order quantity
        st.markdown('<h2 style="font-size:20px; text-align:center;">Total Order Quantity</h2>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="font-size:70px; text-align:center;">{total_order_quantity}</h1>', unsafe_allow_html=True)

        # Fetch data for histogram of sales amount by sales territory region based on selected country
        st.markdown('<h2 style="font-size:20px; text-align:center;">Histogram of Sales Amount by Sales Territory Region</h2>', unsafe_allow_html=True)
        sales_amount_data = fetch_choropleth_data(country=None if selected_country == 'All' else selected_country)

        # Plot histogram using Plotly Express
        fig = px.bar(sales_amount_data, x='SalesTerritoryRegion', y='TotalSales', 
                    labels={'SalesTerritoryRegion': 'Sales Territory Region', 'TotalSales': 'Total Sales'}, color_discrete_sequence=["#543310"])
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No data available for the selected country.")
