import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide', page_title='Netflix Dashboard')

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    [data-testid="stMetricValue"] {
        color: #6C63FF;
    }
    </style>
""", unsafe_allow_html=True)

st.title('🎬 Netflix Data Dashboard')
st.caption('Interactive analysis of 8,807 Netflix titles')

df = pd.read_csv('netflix_titles.csv')
df['director'] = df['director'].fillna('Unknown')
df['cast'] = df['cast'].fillna('Unknown')
df['country'] = df['country'].fillna('Unknown')

st.sidebar.title('🔍 Filters')

type_filter = st.sidebar.multiselect('Content Type', options=df['type'].unique(), default=df['type'].unique())

year_min = int(df['release_year'].min())
year_max = int(df['release_year'].max())
year_range = st.sidebar.slider('Release Year', year_min, year_max, (2010, year_max))

search_title = st.sidebar.text_input('🔎 Search Title')

filtered_df = df[df['type'].isin(type_filter)]
filtered_df = filtered_df[(filtered_df['release_year'] >= year_range[0]) & (filtered_df['release_year'] <= year_range[1])]

if search_title:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search_title, case=False, na=False)]

st.markdown('---')

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Titles', len(filtered_df))
col_m2.metric('Movies', len(filtered_df[filtered_df['type']=='Movie']))
col_m3.metric('TV Shows', len(filtered_df[filtered_df['type']=='TV Show']))
col_m4.metric('Countries', filtered_df['country'].nunique())

st.markdown('---')

tab1, tab2, tab3 = st.tabs(['📊 Overview', '🌍 Geography', '⭐ Ratings & Duration'])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(filtered_df, names='type', title='Movies vs TV Shows', color_discrete_sequence=['#6C63FF', '#4ECDC4'], hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        year_data = filtered_df['release_year'].value_counts().sort_index().reset_index()
        year_data.columns = ['Year', 'Count']
        fig2 = px.area(year_data, x='Year', y='Count', title='Content Added Over Years', color_discrete_sequence=['#6C63FF'])
        st.plotly_chart(fig2, use_container_width=True)

    genres = filtered_df['listed_in'].str.split(', ').explode()
    top_genres = genres.value_counts().head(10).reset_index()
    top_genres.columns = ['Genre', 'Count']
    fig3 = px.bar(top_genres, x='Count', y='Genre', orientation='h', title='Top 10 Genres', color='Count', color_continuous_scale='Purples')
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    top_countries = filtered_df['country'].value_counts().head(10).reset_index()
    top_countries.columns = ['Country', 'Count']
    fig4 = px.bar(top_countries, x='Country', y='Count', title='Top 10 Countries', color='Count', color_continuous_scale='Tealgrn')
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.treemap(top_countries, path=['Country'], values='Count', title='Country Distribution (Treemap)', color='Count', color_continuous_scale='Purples')
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    col5, col6 = st.columns(2)
    with col5:
        top_ratings = filtered_df['rating'].value_counts().head(8).reset_index()
        top_ratings.columns = ['Rating', 'Count']
        fig6 = px.pie(top_ratings, names='Rating', values='Count', title='Content Ratings', color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig6, use_container_width=True)
    with col6:
        movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
        movies_df['duration_min'] = movies_df['duration'].str.replace(' min', '', regex=False)
        movies_df = movies_df[movies_df['duration_min'].str.isnumeric()]
        movies_df['duration_min'] = movies_df['duration_min'].astype(float)
        fig7 = px.histogram(movies_df, x='duration_min', nbins=30, title='Movie Duration Distribution', color_discrete_sequence=['#4ECDC4'])
        st.plotly_chart(fig7, use_container_width=True)

st.markdown('---')
st.subheader('📋 Browse Titles')
st.dataframe(filtered_df[['title', 'type', 'country', 'release_year', 'rating', 'listed_in']].head(50), use_container_width=True)
st.markdown('---')
st.subheader('🎭 Top Directors & Actors')

col7, col8 = st.columns(2)

with col7:
    directors = filtered_df[filtered_df['director'] != 'Unknown']['director'].str.split(', ').explode()
    top_directors = directors.value_counts().head(10).reset_index()
    top_directors.columns = ['Director', 'Count']
    fig8 = px.bar(top_directors, x='Count', y='Director', orientation='h', title='Top 10 Directors', color='Count', color_continuous_scale='Purples')
    st.plotly_chart(fig8, use_container_width=True)

with col8:
    actors = filtered_df[filtered_df['cast'] != 'Unknown']['cast'].str.split(', ').explode()
    top_actors = actors.value_counts().head(10).reset_index()
    top_actors.columns = ['Actor', 'Count']
    fig9 = px.bar(top_actors, x='Count', y='Actor', orientation='h', title='Top 10 Actors', color='Count', color_continuous_scale='Tealgrn')
    st.plotly_chart(fig9, use_container_width=True)

st.markdown('---')
st.subheader('☁️ Word Cloud from Descriptions')

from wordcloud import WordCloud
import matplotlib.pyplot as plt

text = ' '.join(filtered_df['description'].dropna())
wordcloud = WordCloud(width=1000, height=400, background_color='#0E1117', colormap='cool').generate(text)

fig_wc, ax_wc = plt.subplots(figsize=(12, 5))
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis('off')
fig_wc.patch.set_facecolor('#0E1117')
st.pyplot(fig_wc)

st.markdown('---')
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label='📥 Download Filtered Data as CSV',
    data=csv,
    file_name='netflix_filtered_data.csv',
    mime='text/csv'
)