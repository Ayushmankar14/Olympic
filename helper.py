import numpy as np

# Fetch medal tally based on year and/or country
def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    flag = 0

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[
            (medal_df['Year'] == int(year)) & (medal_df['region'] == country)
        ]

    if flag == 1:
        x = temp_df.groupby('Year').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    x[['Gold', 'Silver', 'Bronze', 'total']] = x[['Gold', 'Silver', 'Bronze', 'total']].astype(int)

    return x


# Get list of years and countries for dropdowns
def country_year_list(df):
    years = df['Year'].dropna().unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    countries = np.unique(df['region'].dropna().values).tolist()
    countries.sort()
    countries.insert(0, 'Overall')

    return years, countries


# Count of values of any column over time
def data_over_time(df, col):
    temp_df = df.drop_duplicates(['Year', col])
    count_df = temp_df['Year'].value_counts().reset_index().sort_values('index')
    count_df.rename(columns={'index': 'Edition', 'Year': col}, inplace=True)
    return count_df


# Most successful athletes (overall or by sport)
def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    x = temp_df['Name'].value_counts().reset_index().head(15).merge(
        df, left_on='index', right_on='Name', how='left'
    )[['index', 'Name_x', 'Sport', 'region']].drop_duplicates('index')

    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x


# Country-wise medal tally over the years
def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df


# Country-wise heatmap (sport vs year)
def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )

    new_df = temp_df[temp_df['region'] == country]
    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


# Top 10 successful athletes from a given country
def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    x = temp_df['Name'].value_counts().reset_index().head(10).merge(
        df, left_on='index', right_on='Name', how='left'
    )[['index', 'Name_x', 'Sport']].drop_duplicates('index')

    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x


# Height vs weight data for a selected sport
def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)

    if sport != 'Overall':
        return athlete_df[athlete_df['Sport'] == sport]
    else:
        return athlete_df


# Men vs Women participation over the years
def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final
