import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# Load data with caching and error handling
@st.cache_data
def load_data():
    df = pd.read_csv('athlete_events.zip', compression='zip')
    region_df = pd.read_csv('noc_regions.csv')
    return preprocessor.preprocess(df, region_df)

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# Sidebar UI
st.sidebar.title("🏅 Olympics Analysis")
st.sidebar.image("https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png")

user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
)

# Medal Tally
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("🏆 Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"🎯 Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"📊 {selected_country} Overall Performance")
    else:
        st.title(f"📍 {selected_country} in {selected_year} Olympics")

    st.table(medal_tally)

# Overall Analysis
elif user_menu == 'Overall Analysis':
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.title("📈 Top Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Host Cities", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    st.title("🌍 Participating Nations Over the Years")
    nations_over_time = helper.data_over_time(df, 'region')
    st.plotly_chart(px.line(nations_over_time, x="Edition", y="region"), use_container_width=True)

    st.title("🎪 Events Over the Years")
    events_over_time = helper.data_over_time(df, 'Event')
    st.plotly_chart(px.line(events_over_time, x="Edition", y="Event"), use_container_width=True)

    st.title("👤 Athletes Over the Years")
    athlete_over_time = helper.data_over_time(df, 'Name')
    st.plotly_chart(px.line(athlete_over_time, x="Edition", y="Name"), use_container_width=True)

    st.title("📌 Events Heatmap (per Sport over Years)")
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    fig, ax = plt.subplots(figsize=(20, 20))
    pivot = x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int)
    sns.heatmap(pivot, annot=True, ax=ax)
    st.pyplot(fig)

    st.title("🏅 Most Successful Athletes")
    sport_list = sorted(df['Sport'].dropna().unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    successful = helper.most_successful(df, selected_sport)
    st.table(successful)

# Country-wise Analysis
elif user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    countries = sorted(df['region'].dropna().unique())
    selected_country = st.sidebar.selectbox("Select Country", countries)

    st.title(f"{selected_country} Medal Tally Over the Years")
    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"), use_container_width=True)

    st.title(f"{selected_country} Performance Heatmap")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pt, annot=True, ax=ax)
    st.pyplot(fig)

    st.title(f"🏅 Top 10 Athletes of {selected_country}")
    top10 = helper.most_successful_countrywise(df, selected_country)
    st.table(top10)

# Athlete-wise Analysis
elif user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Age distribution
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4],
        ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
        show_hist=False, show_rug=False)
    fig.update_layout(width=1000, height=600)
    st.title("🎯 Age Distribution")
    st.plotly_chart(fig)

    st.title("🏅 Age Distribution by Sport (Gold Medalists)")
    x, name = [], []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Athletics', 'Swimming', 'Badminton',
                     'Sailing', 'Gymnastics', 'Handball', 'Wrestling', 'Hockey',
                     'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling',
                     'Diving', 'Canoeing', 'Tennis', 'Archery', 'Volleyball']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig)

    st.title("📊 Height vs Weight by Sport")
    sport_list = sorted(df['Sport'].dropna().unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select Sport", sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(data=temp_df, x="Weight", y="Height", hue="Medal", style="Sex", s=60, ax=ax)
    st.pyplot(fig)

    st.title("👨‍🦰 Men vs 👩‍🦰 Women Participation Over the Years")
    gender_df = helper.men_vs_women(df)
    fig = px.line(gender_df, x="Year", y=["Male", "Female"])
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig)
