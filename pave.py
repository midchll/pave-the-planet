"""
pave-the-planet
Mitchell Deevers ~ midchll
2026
"""

from dataclasses import dataclass, field
from collections import deque
from dotenv import load_dotenv
import re
import os

from google.maps import routing_v2
from google.type import latlng_pb2
from geojson import LineString
import polyline

load_dotenv()
ROUTES_API_KEY = os.getenv("ROUTES_API_KEY")


DMS_PATTERN = re.compile(r"\D*(\d+)\D*(\d+)\D*(\d+\.\d+)\D*([nNsSeEwW])\D*")


@dataclass
class RouteNode:
    seqid: int
    lat: float
    lon: float
    elev: float


@dataclass
class Route:
    name: str
    units: str
    nodes: deque[RouteNode] = field(default_factory=deque[RouteNode])


def dms_to_dd(lat:str, lon:str) -> tuple[float, float] | None:
    '''Convert DMS latitude and longitude into decimal degree coordinates'''
    lat_match = re.search(DMS_PATTERN, lat)
    lon_match = re.search(DMS_PATTERN, lon)
    
    if lat_match is None or lon_match is None: 
        return None
    
    lat_items = lat_match.groups()
    lon_items = lon_match.groups()
    
    if len(lat_items) != 4 or len(lon_items) != 4:
        return None
    
    lat_dd = int(lat_items[0]) + (int(lat_items[1]) / 60) + (float(lat_items[2]) / 3600)
    lon_dd = int(lon_items[0]) + (int(lon_items[1]) / 60) + (float(lon_items[2]) / 3600)
    
    lat_dd *= -1 if lat_items[3] in 'sS' and lat_dd > 0 else 1
    lon_dd *= -1 if lon_items[3] in 'wW' and lon_dd > 0 else 1
        
    return (lat_dd, lon_dd)


def get_route_segment(api_key, orig:tuple[float,float], dest:tuple[float,float]) -> tuple[int,str]:
    '''Get route segment encoded polyline, and segment distance (meters)'''
    gclient = routing_v2.RoutesClient(client_options={'api_key': api_key})
    
    request = routing_v2.ComputeRoutesRequest(
        origin=routing_v2.Waypoint(
            location=routing_v2.Location(
                lat_lng=latlng_pb2.LatLng(latitude=orig[0], longitude=orig[1])
            )
        ),
        destination=routing_v2.Waypoint(
            location=routing_v2.Location(
                lat_lng=latlng_pb2.LatLng(latitude=dest[0], longitude=dest[1])
            )
        ),
        polyline_quality=routing_v2.PolylineQuality.HIGH_QUALITY,
        polyline_encoding=routing_v2.PolylineEncoding.ENCODED_POLYLINE
    )
    
    field_mask = 'routes.distanceMeters,routes.polyline.encodedPolyline'
    response = gclient.compute_routes(request=request, metadata=[('x-goog-fieldmask', field_mask)])
    
    return (response.routes[0].distance_meters, response.routes[0].polyline.encoded_polyline)


def decode_linestring(encoded_polyline:str) -> LineString:
    '''Get a GeoJSON LineString object from encoded polyline'''
    decoded = polyline.decode(encoded_polyline)
    coords = [(lat, lon) for lat, lon in decoded]
    linestring = LineString(coords)
    
    return linestring
    

if __name__ == "__main__":
    print('pave-the-planet')
    
    TEST_ORIGIN = dms_to_dd('''32°18'33.5"N''', '''110°44'37.9"W''')
    TEST_DEST   = dms_to_dd('''32°18'36.3"N''', '''110°43'59.5"W''')
    
    if TEST_ORIGIN is None or TEST_DEST is None:
        print("INVALID ORIG/DEST")
        exit()
    
    test_res = get_route_segment(
        api_key=ROUTES_API_KEY,
        orig=(TEST_ORIGIN),
        dest=(TEST_DEST)
    )
    
    print(decode_linestring(test_res[1]))
    
    