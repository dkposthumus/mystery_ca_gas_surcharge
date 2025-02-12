import pandas as pd
from pathlib import Path
from typing import List, Tuple
import numpy as np
import osmnx as ox
import networkx as nx
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

df = pd.read_csv('/Users/danpost/Downloads/master_bare_data.csv')

master = df.copy()
master = master.dropna(subset=['Latitude', 'Longitude'])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
 
    return R*c
 
# define function to find the k-nearest gas stations by road distance for each station in the data
def find_nearest_stations(df: pd.DataFrame, k: int = 3, 
                          network_type: str = 'drive', search_radius_km: float = 8) -> pd.DataFrame:
    ox.settings.use_cache = True
    ox.settings.log_console = True

    # Create a result DataFrame
    result_df = df.copy()

    # ✅ Group Data by `year` and `zip`
    grouped_df = df.groupby(['year', 'zip'])

    all_distances = defaultdict(list)
    processed_stations = set()
    
    for (year, zip_code), group in grouped_df:
        print(f'Processing Year: {year}, Zip: {zip_code}... ({len(group)} stations)')
        station_indices = group.index.tolist()  # Fix: Define `station_indices`

        if len(station_indices) > k:
            area_df = df.loc[station_indices]

            # ✅ Define a Larger Bounding Box   
            buffer = 0.02
            west = area_df['Longitude'].min() - buffer
            east = area_df['Longitude'].max() + buffer
            south = area_df['Latitude'].min() - buffer
            north = area_df['Latitude'].max() + buffer
            # ✅ Get Road Network
            G = ox.graph_from_bbox([west, south, east, north], network_type='drive', simplify=True)

            print('Finding nearest nodes for all stations...')

            # ✅ Nearest Nodes Mapping
            station_nodes = {idx: ox.distance.nearest_nodes(G, X=row['Longitude'], Y=row['Latitude'])
                             for idx, row in area_df.iterrows()}

            # ✅ Compute Road Distances
            for source_idx in station_indices:
                source_node = station_nodes[source_idx]
                station_distances = []

                for target_idx in station_indices:
                    if source_idx != target_idx:
                        target_node = station_nodes[target_idx]
                        try:
                            distance = nx.shortest_path_length(G, source=source_node, target=target_node, weight='length')
                        except nx.NetworkXNoPath:
                            distance = float('inf')
                        station_distances.append((target_idx, distance))

                # ✅ Store k-nearest distances
                station_distances.sort(key=lambda x: x[1])
                nearest_k = station_distances[:k]
                all_distances[source_idx] = [dist for _, dist in nearest_k]
                processed_stations.add(source_idx)

        else:
            print(f'Zip {zip_code} has fewer than {k+1} stations, using Haversine distance...')
            for source_idx in station_indices:
                if source_idx in processed_stations:
                    continue

                source_row = df.loc[source_idx]

                nearby_stations = []
                for target_idx, target_row in df.iterrows():
                    if source_idx != target_idx:
                        dist = haversine_distance(
                            source_row['Latitude'], source_row['Longitude'],
                            target_row['Latitude'], target_row['Longitude']
                        )
                        if dist <= search_radius_km:
                            nearby_stations.append(target_idx)

                # If not enough stations, take additional nearest by Haversine
                if len(nearby_stations) < k:
                    remaining_stations = [idx for idx in df.index if idx not in nearby_stations and idx != source_idx]
                    remaining_stations.sort(key=lambda idx: haversine_distance(
                        source_row['Latitude'], source_row['Longitude'],
                        df.loc[idx, 'Latitude'], df.loc[idx, 'Longitude']
                    ))
                    nearby_stations.extend(remaining_stations[:(k - len(nearby_stations))])

                # ✅ Assign Distances for Small Zip Codes
                station_distances = []
                for target_idx in nearby_stations:
                    dist = haversine_distance(
                        source_row['Latitude'], source_row['Longitude'],
                        df.loc[target_idx, 'Latitude'], df.loc[target_idx, 'Longitude']
                    )
                    station_distances.append((target_idx, dist))

                # ✅ Store k-nearest distances
                station_distances.sort(key=lambda x: x[1])
                nearest_k = station_distances[:k]
                all_distances[source_idx] = [dist for _, dist in nearest_k]
                processed_stations.add(source_idx)

    # ✅ Add Results to DataFrame
    for i in range(k):
        result_df[f'distance_to_nearest_{i+1}'] = [
            all_distances[idx][i] if idx in all_distances and i < len(all_distances[idx])
            else None
            for idx in df.index
        ]
   
    return result_df

# let's test this with a small sample
bakersfield = master[master['zip'] == 94306]
 
result = find_nearest_stations(bakersfield, k=3)
 
print(result)