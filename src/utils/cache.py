# import streamlit as st
# import fastf1
# @st.cache_data(show_spinner="Loading all F1 schedules...")
# def load_schedule():
#     schedule = []

#     for year in range(2018, 2026):
#         try:
#             year_schedule = fastf1.get_event_schedule(year)
#             schedule.append({
#                 'season': year,
#                 'schedule': year_schedule
#             })
#         except Exception as e:
#             st.warning(f"Failed to load schedule for {year}: {e}")
#             continue

#     return schedule

# # Load the schedule once at app start
# SCHEDULE_CACHE = load_schedule()

# def get_schedule():
#     return SCHEDULE_CACHE

# def get_schedule_for_year(year: int = 2025):
#     for entry in SCHEDULE_CACHE:
#         if entry['season'] == year:
#             return entry['schedule']
#     return None  # fallback if year not found
DRIVERS_2018 = ['Lewis Hamilton', 'Sebastian Vettel', 'Kimi Räikkönen', 'Max Verstappen', 'Valtteri Bottas',
                'Daniel Ricciardo', 'Nico Hulkenberg', 'Sergio Perez', 'Kevin Magnussen', 'Carlos Sainz',
                'Fernando Alonso', 'Esteban Ocon', 'Charles Leclerc', 'Romain Grosjean', 'Pierre Gasly',
                'Stoffel Vandoorne', 'Marcus Ericsson', 'Lance Stroll', 'Brendon Hartley', 'Sergey Sirotkin']

DRIVERS_2019 = ['Lewis Hamilton', 'Valtteri Bottas', 'Max Verstappen', 'Charles Leclerc', 'Sebastian Vettel',
                'Carlos Sainz', 'Pierre Gasly', 'Alexander Albon', 'Daniel Ricciardo', 'Sergio Perez',
                'Lando Norris', 'Kimi Raikkonen', 'Daniil Kvyat', 'Nico Hulkenberg', 'Lance Stroll',
                'Kevin Magnussen', 'Antonio Giovinazzi', 'Romain Grosjean', 'Robert Kubica', 'George Russell']

DRIVERS_2020 = ['Lewis Hamilton', 'Valtteri Bottas', 'Max Verstappen', 'Sergio Perez', 'Daniel Ricciardo',
                'Carlos Sainz', 'Alexander Albon', 'Charles Leclerc', 'Lando Norris', 'Pierre Gasly',
                'Lance Stroll', 'Esteban Ocon', 'Sebastian Vettel', 'Daniil Kvyat', 'Nico Hulkenberg',
                'Kimi Raikkonen', 'Antonio Giovinazzi', 'George Russell', 'Romain Grosjean', 'Kevin Magnussen',
                'Nicholas Latifi', 'Jack Aitken', 'Pietro Fittipaldi']

DRIVERS_2021 = ['Max Verstappen', 'Lewis Hamilton', 'Valtteri Bottas', 'Sergio Perez', 'Carlos Sainz',
                'Lando Norris', 'Charles Leclerc', 'Daniel Ricciardo', 'Pierre Gasly', 'Fernando Alonso',
                'Esteban Ocon', 'Sebastian Vettel', 'Lance Stroll', 'Yuki Tsunoda', 'George Russell', 
                'Kimi Raikkonen', 'Nicholas Latifi', 'Antonio Giovinazzi', 'Mick Schumacher', 'Robert Kubica',
                'Nikita Mazepin']

DRIVERS_2022 = ['Max Verstappen', 'Charles Leclerc', 'Sergio Perez', 'George Russell', 'Carlos Sainz',
                'Lewis Hamilton', 'Lando Norris', 'Esteban Ocon', 'Fernando Alonso', 'Valtteri Bottas',
                'Daniel Ricciardo', 'Sebastian Vettel', 'Kevin Magnussen', 'Pierre Gasly', 'Lance Stroll',
                'Mick Schumacher', 'Yuki Tsunoda', 'Zhou Guanyu', 'Alexander Albon', 'Nicholas Latifi',
                'Nyck De Vries', 'Nico Hulkenberg'  ]