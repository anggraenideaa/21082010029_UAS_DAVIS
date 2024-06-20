import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Function to create a connection to the database
def create_connection():
    return mysql.connector.connect(
        host="kubela.id",
        user="davis2024irwan",
        passwd="wh451n9m@ch1n3",
        port=3306,  
        database="aw"
    )

# Function to fetch data based on selected country
def fetch_data(country=None):
    dataBase = create_connection()
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

    cursor.execute(query)
    data = pd.DataFrame(cursor.fetchall(), columns=['YearlyIncome', 'TotalSales'])

    cursor.close()
    dataBase.close()
    
    return data

# Function to fetch available countries
def fetch_countries():
    dataBase = create_connection()
    cursor = dataBase.cursor()
    
    cursor.execute("SELECT DISTINCT SalesTerritoryCountry FROM dimsalesterritory")
    countries = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    dataBase.close()
    
    return countries

# Function to fetch sales data per product category by sales territory
def fetch_sales_data(country=None):
    dataBase = create_connection()
    cursor = dataBase.cursor()

    base_query = """
    SELECT dst.SalesTerritoryRegion, dpc.EnglishProductCategoryName, SUM(fis.SalesAmount) AS TotalSales
    FROM factinternetsales fis
    JOIN dimsalesterritory dst ON fis.SalesTerritoryKey = dst.SalesTerritoryKey
    JOIN dimproduct dp ON fis.ProductKey = dp.ProductKey
    JOIN dimproductsubcategory dps ON dp.ProductSubcategoryKey = dps.ProductSubcategoryKey
    JOIN dimproductcategory dpc ON dps.ProductCategoryKey = dpc.ProductCategoryKey
    {}
    GROUP BY dst.SalesTerritoryRegion, dpc.EnglishProductCategoryName;
    """
    
    if country:
        query = base_query.format(f"WHERE dst.SalesTerritoryCountry = '{country}'")
    else:
        query = base_query.format("")

    cursor.execute(query)
    data = pd.DataFrame(cursor.fetchall(), columns=['SalesTerritoryRegion', 'ProductCategory', 'TotalSales'])

    cursor.close()
    dataBase.close()
    
    return data

# Function to fetch and display treemap data
def fetch_treemap_data(country=None):
    dataBase = create_connection()
    cursor = dataBase.cursor()

    base_query = """
    SELECT dpc.EnglishProductCategoryName, SUM(fis.SalesAmount) AS TotalSales
    FROM factinternetsales fis
    JOIN dimproduct dp ON fis.ProductKey = dp.ProductKey
    JOIN dimproductsubcategory dps ON dp.ProductSubcategoryKey = dps.ProductSubcategoryKey
    JOIN dimproductcategory dpc ON dps.ProductCategoryKey = dpc.ProductCategoryKey
    {}
    GROUP BY dpc.EnglishProductCategoryName;
    """
    
    if country:
        query = base_query.format(f"WHERE EXISTS (SELECT 1 FROM dimsalesterritory dst WHERE fis.SalesTerritoryKey = dst.SalesTerritoryKey AND dst.SalesTerritoryCountry = '{country}')")
    else:
        query = base_query.format("")

    cursor.execute(query)
    data = pd.DataFrame(cursor.fetchall(), columns=['ProductCategory', 'TotalSales'])

    cursor.close()
    dataBase.close()
    
    return data


# Function to fetch data for choropleth map
def fetch_choropleth_data(country=None):
    dataBase = create_connection()
    cursor = dataBase.cursor()

    base_query = """
    SELECT dst.SalesTerritoryRegion, SUM(fis.SalesAmount) AS TotalSales
    FROM factinternetsales fis
    JOIN dimsalesterritory dst ON fis.SalesTerritoryKey = dst.SalesTerritoryKey
    {}
    GROUP BY dst.SalesTerritoryRegion
    ORDER BY TotalSales DESC;
    """
    
    if country:
        query = base_query.format(f"WHERE dst.SalesTerritoryCountry = '{country}'")
    else:
        query = base_query.format("")

    cursor.execute(query)
    data = pd.DataFrame(cursor.fetchall(), columns=['SalesTerritoryRegion', 'TotalSales'])

    cursor.close()
    dataBase.close()
    
    return data

# Streamlit interface
st.set_page_config(layout="wide")
st.markdown('<h1 style="font-size:30px; text-align:center;">Dashboard Penjualan</h1>', unsafe_allow_html=True)

# Sidebar for selecting country
st.sidebar.title('📊 Dashboard Penjualan')
countries = fetch_countries()
selected_country = st.sidebar.selectbox('Pilih Negara', options=['All'] + countries)

# Menambahkan Nama dengan link GitHub dan NPM di sidebar
st.sidebar.markdown('<p style="font-size:14px; text-align:center;">Nama: <a href="https://github.com/anggraenideaa/21082010029_UAS_DAVIS" target="_blank">Dea Puspita Anggraeni</a></p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size:14px; text-align:center;">NPM: 21082010029</p>', unsafe_allow_html=True)

# Fetch data based on selected country
data = fetch_data(country=None if selected_country == 'All' else selected_country)

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
    st.markdown('<h2 style="font-size:20px; text-align:center;">Perbandingan Penjualan di Berbagai Region Untuk Berbagai Kategori Produk</h2>', unsafe_allow_html=True)
    fig = px.bar(pivot_data, x='SalesTerritoryRegion', y=pivot_data.columns[1:], color_discrete_sequence=["#543310", "#F8F4E1", "#AF8F6F"])
    st.plotly_chart(fig, use_container_width=True)

    # Fetch data for choropleth map
    choropleth_data = fetch_choropleth_data(country=None if selected_country == 'All' else selected_country)
    sales_territory_regions, total_sales = zip(*choropleth_data.values)
    

    st.markdown('<h2 style="font-size:20px; text-align:center;"></h2>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size:20px; text-align:center;"></h2>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-size:20px; text-align:center;"></h2>', unsafe_allow_html=True)
    # Display choropleth map
    st.markdown('<h2 style="font-size:20px; text-align:center;">Penjualan Terdistribusi di Berbagai Wilayah Penjualan (SalesTerritoryregion)</h2>', unsafe_allow_html=True)
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
    st.markdown('<h2 style="font-size:20px; text-align:center;">Komposisi Total Penjualan Berdasarkan Kategori Produk</h2>', unsafe_allow_html=True)
    fig = px.treemap(treemap_data, path=['ProductCategory'], values='TotalSales', color_discrete_sequence=["#543310", "#74512D", "#AF8F6F"])
    st.plotly_chart(fig, use_container_width=True)

    # Display each product category and its total sales in a card format
    st.markdown('<h2 style="font-size:20px; text-align:center;">Total Penjualan Berdasarkan Kategori Produk</h2>', unsafe_allow_html=True)
    for index, row in treemap_data.iterrows():
        category = row['ProductCategory']
        total_sales = row['TotalSales']
        st.markdown(f'<div style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin: 10px 0;">'
                    f'<h3 style="font-size:20px; text-align:center;">{category}</h3>'
                    f'<h1 style="font-size:50px; text-align:center;">{total_sales}</h1>'
                    '</div>', unsafe_allow_html=True)
                    


    # Fetch data for histogram of sales amount by sales territory region based on selected country
    st.markdown('<h2 style="font-size:20px; text-align:center;">Penjualan Terdistribusi di Berbagai Wilayah Penjualan (SalesTerritoryregion)</h2>', unsafe_allow_html=True)
    sales_amount_data = fetch_choropleth_data(country=None if selected_country == 'All' else selected_country)


    # Plot histogram using Plotly Express
    fig = px.bar(sales_amount_data, x='SalesTerritoryRegion', y='TotalSales', 
                labels={'SalesTerritoryRegion': 'Sales Territory Region', 'TotalSales': 'Total Sales'}, color_discrete_sequence=["#543310"])
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Adding text card below the last graph for narrative explanation
    st.markdown("""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h2 style="font-size:20px; text-align:center;">Penjelasan Grafik</h2>
            <p style="text-align:justify;">
                1. <b>Data yang digunakan</b> adalah datawerehouse adventure works.
            </p>
            <p style="text-align:justify;">
                2. <b>Scatter Plot Hubungan Antara Pendapatan Tahunan dan Total Penjualan</b> digunakan untuk mengetahui hubungan antara jumlah penjualan dengan pendapatan tahunan customer.
            </p>
            <p style="text-align:justify;">
                3. <b>Treemap Persentase Penjualan per Kategori Produk (Bahasa Inggris)</b> digunakan untuk mengetahui perbandingan penjualan di berbagai region untuk berbagai kategori produk.
            </p>
            <p style="text-align:justify;">
                4. <b>Card Text per Kategori Produk</b> yang diambil dari grafik treemap untuk menampilkan penjualan tiap produk.
            </p>
            <p style="text-align:justify;">
                5. <b>Stacked Bar Chart Penjualan Per Kategori Produk berdasarkan Wilayah Penjualan</b> digunakan untuk mengetahui perbandingan penjualan di berbagai region untuk berbagai kategori produk.
            </p>
            <p style="text-align:justify;">
                6. <b>Map Chart Total Sales by Sales Territory Region</b> digunakan untuk mengetahui peta wilayah region yang terhubung dari stacked bar chart.
            </p>
            <p style="text-align:justify;">
                7. <b>Column Histogram Histogram of Sales Amount by Sales Territory Region</b> digunakan untuk mengetahui penjualan terdistribusi di berbagai wilayah penjualan (SalesTerritoryregion).
            </p>
        </div>
    """, unsafe_allow_html=True)
