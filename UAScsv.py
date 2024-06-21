import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Fungsi untuk memuat data dari file CSV
def load_data():
    file_path = 'IMDB_FILM_UAS.csv'  # Path ke file CSV yang telah diunggah
    return pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=';')

# Fungsi untuk membuat dashboard
def main():
    st.markdown('<h1 style="font-size:30px; text-align:center;">Dashboard Analisis Film</h1>', unsafe_allow_html=True)
    
    # Memuat data
    data = load_data()

    # Sidebar untuk filter nama film
    st.sidebar.title('📊 Dashboard Analisis Film')
    selected_movie = st.sidebar.selectbox("Filter Nama Film", ["All"] + list(data['Title'].unique()))

    # Menambahkan Nama dengan link GitHub dan NPM di sidebar
    st.sidebar.markdown('<p style="font-size:14px; text-align:center;">Nama: <a href="https://github.com/anggraenideaa/21082010029_UAS_DAVIS" target="_blank">Dea Puspita Anggraeni</a></p>', unsafe_allow_html=True)
    st.sidebar.markdown('<p style="font-size:14px; text-align:center;">NPM: 21082010029</p>', unsafe_allow_html=True)


    # Filter data berdasarkan nama film yang dipilih
    if selected_movie == "All":
        filtered_data = data
    else:
        filtered_data = data[data['Title'] == selected_movie]

    if not filtered_data.empty:
        # Bubble Chart: Menunjukkan hubungan antara Budget, Pendapatan Kotor Global, dan Durasi Film
        st.markdown('<h2 style="font-size:20px; text-align:center;">Hubungan antara Budget, Gross Worldwide, dan Runtime</h2>', unsafe_allow_html=True)
        # Kode untuk Bubble Chart
        fig1 = px.scatter(
            data_frame=filtered_data, 
            x='Budget', 
            y='Gross worldwide', 
            size='Runtime', 
            color='Runtime',
            hover_name='Title',
            labels={'Budget': 'Anggaran ($)', 'Gross worldwide': 'Pendapatan Kotor Global ($)', 'Runtime': 'Durasi (menit)'},
            color_continuous_scale='Viridis'
        )
        fig1.update_yaxes(tick0=0, dtick=200000000)  # Set the tick step for y-axis to 0.2B
        st.plotly_chart(fig1)

        # Bar chart untuk Comparison (2 variabel per item)
        st.markdown('<h2 style="font-size:20px; text-align:center;">Perbandingan antara Gross US & Canada and Gross Worldwide per Film</h2>', unsafe_allow_html=True)
        # Kode untuk Bar chart
        fig2 = px.bar(
            data_frame=filtered_data, 
            x='Title', 
            y=['Gross US & Canada', 'Gross worldwide'], 
            barmode='group',
            color_discrete_map={'Gross US & Canada': 'blue', 'Gross worldwide': 'orange'},  # Menggunakan skema warna yang berbeda untuk setiap variabel
            category_orders={"Title": filtered_data.groupby("Title")["Gross US & Canada"].sum().sort_values(ascending=False).index}
        )
        fig2.update_yaxes(tick0=0, dtick=200000000)  # Set the tick step for y-axis to 0.2B
        fig2.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels for better readability
        st.plotly_chart(fig2)

        # Scatter Plot interaktif untuk Distribution (2 variabel)
        st.markdown('<h2 style="font-size:20px; text-align:center;">Distribusi Dua Variabel: Opening Weekend vs Gross US & Canada</h2>', unsafe_allow_html=True)
        # Kode untuk Scatter Plot
        fig_interactive = go.Figure()
        fig_interactive.add_trace(go.Scatter(
            x=filtered_data['Opening weekend US & Canada'],
            y=filtered_data['Gross US & Canada'],
            mode='markers',
            marker=dict(
                size=filtered_data['Runtime'] / 10,
                color=filtered_data['Gross worldwide'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Gross Worldwide ($)')
            ),
            text=filtered_data['Title'],
            hoverinfo='text+x+y'
        ))
        fig_interactive.update_layout(
            xaxis=dict(title='Pendapatan Akhir Minggu Pembukaan ($)'),
            yaxis=dict(title='Pendapatan Kotor di AS & Kanada ($)'),
            hovermode='closest'
        )
        st.plotly_chart(fig_interactive)

        # Stacked Bar Chart untuk Komposisi Pendapatan Kotor
        st.markdown('<h2 style="font-size:20px; text-align:center;">Komposisi Pendapatan Kotor Film</h2>', unsafe_allow_html=True)
        # Kode untuk Stacked Bar Chart
        fig_stacked_bar = px.bar(filtered_data, x='Title', y=['Gross US & Canada', 'Gross worldwide', 'Opening weekend US & Canada'],
                                barmode='stack', color_discrete_map={'Gross US & Canada': 'blue', 'Gross worldwide': 'orange', 'Opening weekend US & Canada': 'green'},
                                category_orders={"Title": filtered_data.groupby("Title")["Gross US & Canada"].sum().sort_values(ascending=False).index})
        st.plotly_chart(fig_stacked_bar)

    else:
        st.warning("Film tidak ditemukan dalam data.")


    # Adding the interactive expander for Grafik Explanation
    with st.expander("Penjelasan Grafik", expanded=False):
        st.markdown("""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h2 style="font-size:20px; text-align:center;">Penjelasan Grafik</h2>
            <p style="text-align:justify;">
                <b>1. Data</b> yang digunakan adalah scrapping film Top Picks dari pencarian film The Garfield Movie pada link <a href="https://www.imdb.com" target="_blank">www.imdb.com</a> dengan mengambil informasi berupa judul film, link film, informasi box office dan technical specs.
            </p>
            <p style="text-align:justify;">
                <b>2. Bubble Plot Hubungan antara Budget, Gross Worldwide, dan Runtime</b> digunakan untuk mengetahui hubungan antara Budget, Gross Worldwide, dan Runtime.
            </p>
            <p style="text-align:justify;">
                <b>3. Bar Chart Perbandingan antara Gross US & Canada and Gross Worldwide per Film</b> digunakan untuk membandingkan dua variabel yaitu Gross US & Canada dengan Gross Worldwide untuk setiap film.
            </p>
            <p style="text-align:justify;">
                <b>4. Scatter Plot Distribusi Dua Variabel: Opening Weekend vs Gross US & Canada</b> digunakan untuk mengetahui distribusi pendapatan dua variabel yaitu Opening Weekend US & Canada dan Gross US & Canada.
            </p>
            <p style="text-align:justify;">
                <b>5. Stacked Bar Chart Komposisi Pendapatan Kotor Film</b> digunakan untuk mengetahui komposisi dari total pendapatan dari berbagai film berdasarkan Gross US & Canada, Gross Worldwide, dan Opening Weekend US & Canada.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Adding the interactive expander for Dashboard Usage Interpretation
    with st.expander("Interpretasi Penggunaan Dashboard", expanded=False):
        st.markdown("""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h2 style="font-size:20px; text-align:center;">Interpretasi Penggunaan Dashboard</h2>
            <h3 style="font-size:18px;">Fitur Interaktif</h3>
            <p style="text-align:justify;">
                <b>Klik/Hover</b>: Setiap chart pada dashboard ini bisa diklik atau dihover untuk highlight detail.
                <br><b>Zoom</b>: Chart juga bisa dizoom untuk melihat bagian yang lebih spesifik.
                <br><b>Reset</b>: Untuk mengembalikan chart ke tampilan default, cukup dengan mengklik dua kali pada chart tersebut.
            </p>
            <h3 style="font-size:18px;">Filter</h3>
            <p style="text-align:justify;">
                <b>Filter Berdasarkan Nama Film</b>: Di sisi kiri dashboard, terdapat filter yang memungkinkan Anda untuk memfilter data berdasarkan nama film tertentu. Untuk mengembalikan ke tampilan semula, pilih filter "All".
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
