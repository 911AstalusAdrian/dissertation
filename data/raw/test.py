# from urllib.request import urlopen
# import pandas as pd
# import json

# response = urlopen('https://api.openf1.org/v1/drivers?driver_number=1&session_key=9158')
# data = json.loads(response.read().decode('utf-8'))

# df = pd.DataFrame(data)
# print(df.transpo)


import fastf1
session = fastf1.get_session(2017, 'Monza', 'Q')
session.load(telemetry=False, laps=False, weather=False)
vettel = session.get_driver('VET')
print(f"Pronto {vettel['FirstName']}?")


'''
telemetry/
laps/
pit/
drivers/ and stints/
position/
'''

# FastF1 API - Telemetry data available only from 2018 onwards
# Ergast API - Historical data (1996 onwards), but no telemetry data
# OpenF1 (https://openf1.org/) - data available only from 2023 season onwards