import streamlit as st
import fastf1

@st.cache_data(show_spinner="Loading all F1 schedules...")
def load_schedule():
    schedule = []

    for year in range(2018, 2026):
        try:
            year_schedule = fastf1.get_event_schedule(year)
            schedule.append({
                'season': year,
                'schedule': year_schedule
            })
        except Exception as e:
            st.warning(f"Failed to load schedule for {year}: {e}")
            continue

    return schedule

# Load the schedule once at app start
SCHEDULE_CACHE = load_schedule()

def get_schedule():
    return SCHEDULE_CACHE

def get_schedule_for_year(year: int = 2025):
    for entry in SCHEDULE_CACHE:
        if entry['season'] == year:
            return entry['schedule']
    return None  # fallback if year not found
