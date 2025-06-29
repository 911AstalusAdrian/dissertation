import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.data_ingestion.openf1_loader import get_driver_image
from src.data_ingestion.fastf1_loader import get_driver_full_info, get_distinct_drivers
from src.utils.plot_utils import TEAM_COLORS

@st.cache_data(show_spinner='Getting the list of available drivers...')
def get_drivers_data():
    drivers_list = get_distinct_drivers()
    return drivers_list

# @st.cache_data(show_spinner='Fetching driver data...')
# def get_driver_stats(driver_name):
#     stats = get_driver_stats_multiseason(driver_full_name=driver_name)
#     return stats

# @st.cache_data
# def get_driver_results(driver_name):
#     results = get_race_results_over_seasons(driver_name)
#     return results


@st.cache_data
def get_driver_photo(driver_name):
    return get_driver_image(driver_name)

# @st.cache_data
# def get_driver_comparisons(driver_name):
#     comparisons = get_driver_teammate_comparison_over_seasons(driver_name)
#     return comparisons

def plot_driver_results(df):

    df['RaceIndex'] = range(len(df)) # add a race index

    # Calculate the inverse position so the higher places are at the top of the plot
    df['InvPos'] = df['Position'].astype(int)
    max_pos = df['InvPos'].max()
    df['InvPos'] = max_pos - df['InvPos'] + 1

    fig, ax = plt.subplots(figsize=(12,6))

    segment_x, segment_y = [], []
    prev_team = df.loc[0, 'TeamName']

    for i, row in df.iterrows():
        current_team = row['TeamName']
        color = TEAM_COLORS.get(current_team, '#888888')

        if current_team != prev_team:
            ax.plot(segment_x, segment_y, color = TEAM_COLORS.get(prev_team, '#888888'),
                    linewidth=2, label=prev_team if prev_team not in ax.get_legend_handles_labels()[1] else "")
            segment_x, segment_y = [], []
            prev_team = current_team
        
        segment_x.append(row['RaceIndex'])
        segment_y.append(row['Position'])

    if segment_x:
        ax.plot(segment_x, segment_y, color = TEAM_COLORS.get(prev_team, '#888888'),
                linewidth=2, label=prev_team if prev_team not in ax.get_legend_handles_labels()[1] else "")
        
    ax.set_xlabel('Race Index')
    ax.set_ylabel('Finishing Position')
    ax.set_title('Driver Race Results')
    ax.set_yticks(range(max_pos, 0, -1))
    ax.set_yticklabels(list(range(max_pos, 0, -1)))
    ax.invert_yaxis()  # P1 on top
    ax.legend(title="Teams", loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    st.pyplot(fig)

def plot_h2h(df):
    quali_delta = df[['Season', 'QualiDelta']]
    quali_delta['Season'] = quali_delta['Season'].astype(str)
    fig = go.Figure()

    # Main QualiDelta line
    fig.add_trace(go.Scatter(
        x=quali_delta['Season'],
        y=quali_delta['QualiDelta'],
        mode='lines+markers',
        name='Quali Delta',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))

    # Horizontal zero baseline
    fig.add_trace(go.Scatter(
        x=quali_delta['Season'],
        y=[0] * len(quali_delta),
        mode='lines',
        name='Baseline (0s)',
        line=dict(color='red', dash='dash'),
        showlegend=False
    ))

    fig.update_layout(
        title='Avg Qualifying Delta vs Teammate (per Season)',
        xaxis_title='Season',
        yaxis_title='Delta (s)',
        yaxis=dict(zeroline=False),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_h2h_summary(h2h_analysis):
    df = h2h_analysis.copy()
    all_seasons = df['Season'].tolist()
    df['Season'] = df['Season'].astype(str)

    # Qualifying Bar Chart
    fig_quali = go.Figure()
    fig_quali.add_trace(go.Bar(
        x=df['Season'],
        y=df['QualiFor'],
        name='Quali Wins',
        marker_color='green'
    ))
    fig_quali.add_trace(go.Bar(
        x=df['Season'],
        y=df['QualiAgainst'],
        name='Quali Losses',
        marker_color='red'
    ))
    fig_quali.update_layout(
        barmode='group',
        title='Qualifying Head-to-Head Summary',
        xaxis=dict(
            title='Season',
            tickmode='array',
            tickvals=all_seasons,
            ticktext=all_seasons
        ),
        xaxis_title='Season',
        yaxis_title='Count',
        legend_title='Category'
    )

    # Race Bar Chart
    fig_race = go.Figure()
    fig_race.add_trace(go.Bar(
        x=df['Season'],
        y=df['RaceFor'],
        name='Race Wins',
        marker_color='blue'
    ))
    fig_race.add_trace(go.Bar(
        x=df['Season'],
        y=df['RaceAgainst'],
        name='Race Losses',
        marker_color='orange'
    ))
    fig_race.update_layout(
        barmode='group',
        title='Race Head-to-Head Summary',
        xaxis=dict(
            title='Season',
            tickmode='array',
            tickvals=all_seasons,
            ticktext=all_seasons
        ),
        xaxis_title='Season',
        yaxis_title='Count',
        legend_title='Category'
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_quali, use_container_width=True)
    with col2:
        st.plotly_chart(fig_race, use_container_width=True)
    
@st.cache_data(show_spinner='Fetching ALL the possible thata for this driver... This may take a sec..')
def get_driver_info(driver):
    full_data = get_driver_full_info(driver)
    return full_data


drivers_list = get_drivers_data()
seasons = list(range(2018, 2026))


# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=drivers_list)  # Example list
show_driver_button = st.sidebar.button('Show Driver Details')

if show_driver_button:
    driver_data = get_driver_info(driver)

    st.session_state["driver_data"] = driver_data
    st.session_state["driver_selected"] = driver

    if "driver_data" in st.session_state and st.session_state.get("driver_selected") == driver:
        st.header(f"Stats for {driver}")
        st.write("Driver Info Dictionary:", st.session_state["driver_data"])
        st.dataframe(st.session_state["driver_data"]["Results"])
        st.dataframe(st.session_state["driver_data"]["Comparisons"])

    profile_col1, profile_col2 = st.columns([1,3])
    with profile_col1:
        st.image(get_driver_photo(driver), width=150)
    with profile_col2:
        kpi_cols = st.columns(3)
        kpi_cols[0].metric('Total Races', driver_data['TotalRaces'])
        kpi_cols[1].metric('Finished', driver_data['Finished'])
        kpi_cols[2].metric('DNFs', driver_data['DNFs'])

        kpi_cols2 = st.columns(3)
        kpi_cols2[0].metric('Wins', driver_data['Wins'])
        kpi_cols2[1].metric('Podiums', driver_data['Podiums'])
        kpi_cols2[2].metric('Total Points', driver_data['Points'])

        st.markdown(f'Teams raced for: {driver_data['Teams']}')

    plot_driver_results(driver_data['Results'])
    plot_h2h(driver_data['Comparisons'])
    plot_h2h_summary(driver_data['Comparisons'])