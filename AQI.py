from collections import namedtuple
from datetime import datetime
import requests, re

Station         = namedtuple('Station', 'Id Name Address Latitude Longitude')
Concentration   = namedtuple('Concentration', 'ReadTime PM10 SO2 O3 NO2 CO')
AQI             = namedtuple('AQI', 'ReadTime PM10 SO2 O3 NO2 CO AQIIndex ContaminantParameter State Color')

def GetAQIStations():
    with requests.Session() as s:
        url = 'https://api.ibb.gov.tr/havakalitesi/OpenDataPortalHandler/GetAQIStations'
        r = s.get(url)
        r.raise_for_status()

        pattern  = r'POINT\s\((?P<Lng>.*)\s(?P<Lat>.*)\)'
        stations = []

        for station in r.json():
            address  = station.pop('Adress')
            location = station.pop('Location')
            matches  = re.match(pattern, location)
            station.update({
                'Address': address,
                'Latitude': float(matches.group('Lat')),
                'Longitude': float(matches.group('Lng'))
                })
            stations.append(Station(**station))
            
        return stations
    
def GetAQIByStationId(stationId: str, startDate: datetime, endDate: datetime):
    with requests.Session() as s:
        url = 'https://api.ibb.gov.tr/havakalitesi/OpenDataPortalHandler/GetAQIByStationId'
        params = {
            'StationId': stationId,
            'StartDate': startDate.strftime('%d.%m.%Y %H:%M:%S'),
            'EndDate': endDate.strftime('%d.%m.%Y %H:%M:%S')
            }
        r = s.get(url, params=params)
        r.raise_for_status()

        C, A = [], []
        for record in r.json():
            ReadTime = record.pop('ReadTime')
            ReadTime = datetime.fromisoformat(ReadTime)
            if c := record.get('Concentration'):
                c |= {'ReadTime': ReadTime}
                C.append(Concentration(**c))
            if a := record.get('AQI'):
                a |= {'ReadTime': ReadTime}
                A.append(AQI(**a))

        return C, A

if __name__ == '__main__':
    stations = GetAQIStations()
    # print(*stations, sep='\n')
    # >>> Station(Id='6b7a9840-1e13-4045-a79d-0f881c4852ad', Name='Maslak', Address='İstanbul / Sarıyer - Turkey', Latitude=41.10007237141238, Longitude=29.02451200417135)
    # ...
    # >>> Station(Id='476aac30-cec4-4dc3-b180-fc1522d8a37c', Name='Arnavutköy', Address='İstanbul - Arnavutköy', Latitude=41.22092094312305, Longitude=28.70756051481934)
    # >>> Station(Id='30a7a252-f4ea-43f8-a8db-fdea5ca332d3', Name='Tuzla', Address='İstanbul - Tuzla', Latitude=40.843121743887025, Longitude=29.302621843152615)

    C, A = GetAQIByStationId('6b7a9840-1e13-4045-a79d-0f881c4852ad', datetime(2020,1,1), datetime(2020,1,2))
    # print(*C, sep='\n')
    # >>> Concentration(ReadTime=datetime.datetime(2020, 1, 1, 0, 0), PM10=28.5, SO2=3.2, O3=6.3, NO2=52.2, CO=None)
    # ...
    # >>> Concentration(ReadTime=datetime.datetime(2020, 1, 1, 23, 0), PM10=5.2, SO2=2.9, O3=28.6, NO2=12.0, CO=None)
    # >>> Concentration(ReadTime=datetime.datetime(2020, 1, 2, 0, 0), PM10=9.6, SO2=2.8, O3=25.1, NO2=10.3, CO=None)
    # 
    # print(*A, sep='\n')
    # >>> AQI(ReadTime=datetime.datetime(2020, 1, 1, 0, 0), PM10=14.0, SO2=2.0, O3=4.0, NO2=26.0, CO=None, AQIIndex=26.0, ContaminantParameter='NO2', State='Hava kalitesi memnun edici ve hava kirliliği az riskli veya hiç risk teşkil etmiyor.', Color='#13a261')
    # ...
    # >>> AQI(ReadTime=datetime.datetime(2020, 1, 1, 23, 0), PM10=20.0, SO2=2.0, O3=10.0, NO2=6.0, CO=None, AQIIndex=20.0, ContaminantParameter='PM10', State='Hava kalitesi memnun edici ve hava kirliliği az riskli veya hiç risk teşkil etmiyor.', Color='#13a261')
    # >>> AQI(ReadTime=datetime.datetime(2020, 1, 2, 0, 0), PM10=19.0, SO2=2.0, O3=10.0, NO2=5.0, CO=None, AQIIndex=19.0, ContaminantParameter='PM10', State='Hava kalitesi memnun edici ve hava kirliliği az riskli veya hiç risk teşkil etmiyor.', Color='#13a261')
