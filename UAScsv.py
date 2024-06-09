import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Tentukan path ke file CSV
file_path = 'IMDB_FILM_UAS.csv'

st.markdown('<h1 style="font-size:30px; text-align:center;">Dashboard Film</h1>', unsafe_allow_html=True)

# Periksa apakah file tersebut ada
if not os.path.exists(file_path):
    st.error(f"File tidak ditemukan: {file_path}")
else:
    # Coba muat dataset dengan delimiter ;
    try:
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1')
        except UnicodeDecodeError:
            st.error("Gagal membaca file dengan encoding UTF-8 dan ISO-8859-1.")
            st.stop()

    # Sidebar
    st.sidebar.title('Navigasi')
    movie_names = ["All"] + sorted(df['Title'].unique().tolist())
    selected_movie = st.sidebar.selectbox('Pilih Film', movie_names)

    # Filter berdasarkan nama film yang dipilih
    if selected_movie == "All":
        selected_movie_df = df
    else:
        selected_movie_df = df[df['Title'] == selected_movie]

    # Chart 1: Scatter Plot
    if not selected_movie_df.empty:
        st.markdown(f'<h2 style="font-size:20px; text-align:center;">Hubungan antara Budget, Pendapatan Kotor Global, dan Durasi Film: {selected_movie} </h2>', unsafe_allow_html=True)
        fig = px.scatter(selected_movie_df,
                        x='Budget',
                        y='Gross worldwide',
                        size='Runtime',
                        color='Runtime',
                        hover_name='Title',
                        labels={'Budget': 'Anggaran ($)', 'Gross worldwide': 'Pendapatan Kotor Global ($)',
                                'Runtime': 'Durasi (menit)'},
                        color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True, width=800, height=600)

    # Chart 2: Scatter Plot Interaktif
    if not selected_movie_df.empty:
        st.markdown(f'<h2 style="font-size:20px; text-align:center;">Scatter Plot Interaktif: Opening Weekend vs Gross US & Canada dengan Interaksi yang Lebih Luar Biasa: {selected_movie} </h2>', unsafe_allow_html=True)
        fig_interactive = go.Figure()
        fig_interactive.add_trace(go.Scatter(
            x=selected_movie_df['Opening weekend US & Canada'],
            y=selected_movie_df['Gross US & Canada'],
            mode='markers',
            marker=dict(
                size=selected_movie_df['Runtime'] / 10,
                color=selected_movie_df['Gross worldwide'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Gross Worldwide ($)')
            ),
            text=selected_movie_df['Title'],
            hoverinfo='text+x+y'
        ))
        fig_interactive.update_layout(
            xaxis=dict(title='Pendapatan Akhir Minggu Pembukaan ($)'),
            yaxis=dict(title='Pendapatan Kotor di AS & Kanada ($)'),
            hovermode='closest'
        )
        st.plotly_chart(fig_interactive, use_container_width=True, width=800, height=600)

    # Chart 3: Bar Chart
    if not selected_movie_df.empty:
        st.markdown(f'<h2 style="font-size:20px; text-align:center;">Perbandingan Pendapatan Kotor Global dari Berbagai Film: {selected_movie} </h2>', unsafe_allow_html=True)
        # Perbaikan: Mengurutkan data sebelum membuat Bar Chart
        df_sorted = selected_movie_df.sort_values(by='Gross worldwide', ascending=False)
        bar_fig = px.bar(df_sorted,
                        x='Title',
                        y='Gross worldwide',
                        labels={'Title': 'Judul Film', 'Gross worldwide': 'Pendapatan Kotor Global ($)'},
                        color='Gross worldwide',
                        color_continuous_scale='Viridis')
        bar_fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(bar_fig, use_container_width=True, width=800, height=600)

    # Chart 4: Stacked Bar Chart
    if not selected_movie_df.empty:
        selected_movie_df['Total Gross'] = selected_movie_df['Gross US & Canada'] + selected_movie_df[
            'Opening weekend US & Canada'] + selected_movie_df['Gross worldwide']
        st.markdown(f'<h2 style="font-size:20px; text-align:center;">Komposisi Pendapatan Kotor dari Berbagai Film: {selected_movie} </h2>', unsafe_allow_html=True)
        stacked_bar_fig = go.Figure()
        stacked_bar_fig.add_trace(go.Bar(
            x=selected_movie_df['Title'],
            y=selected_movie_df['Gross US & Canada'],
            name='Gross US & Canada',
            marker_color=px.colors.sequential.Viridis[1]
        ))
        stacked_bar_fig.add_trace(go.Bar(
            x=selected_movie_df['Title'],
            y=selected_movie_df['Opening weekend US & Canada'],
            name='Opening weekend US & Canada',
            marker_color=px.colors.sequential.Viridis[3]
        ))
        stacked_bar_fig.add_trace(go.Bar(
            x=selected_movie_df['Title'],
            y=selected_movie_df['Gross worldwide'],
            name='Gross worldwide',
            marker_color=px.colors.sequential.Viridis[5]
        ))
        stacked_bar_fig.update_layout(
            barmode='stack',
            xaxis_tickangle=-45,
            xaxis=dict(title='Judul Film'),
            yaxis=dict(title='Pendapatan Kotor ($)')
        )
        st.plotly_chart(stacked_bar_fig, use_container_width=True, width=800, height=600)
        
    # Chart 5: Pie Chart
        st.markdown(f'<h2 style="font-size:20px; text-align:center;">Pie Chart Komposisi Pendapatan Kotor: {selected_movie} </h2>', unsafe_allow_html=True)
        pie_fig = px.pie(selected_movie_df,
                        values='Total Gross',
                        names='Title',
                        title=f'Komposisi Pendapatan Kotor Global dari Berbagai Film: {selected_movie}',
                        labels={'Total Gross': 'Pendapatan Kotor Total ($)', 'Title': 'Judul Film'},
                        color_discrete_sequence=px.colors.sequential.Viridis,
                        hole=0.3)
        st.plotly_chart(pie_fig, use_container_width=True, width=800, height=600)
