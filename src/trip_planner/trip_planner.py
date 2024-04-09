from pathlib import Path
from typing import Iterator, NamedTuple

import attrs
import docx
import rich
from docx import Document
import httpx
import urllib3
import re
import docx.text.hyperlink
import simplekml


class Coords(NamedTuple):
    lon: float
    lat:float

@attrs.frozen
class Location:
    name: str
    coords: Coords
    maps_link: str

def resolve_maps_link(url:str)->str:
    response = httpx.get(url)
    if response.is_redirect and response.has_redirect_location:
        return response.headers["location"]

"""
https://www.google.com/maps/place/BouBou's/@38.7171315,-9.1507597,17z/data=!3m1!4b1!4m6!3m5!1s0xd193337c1ee5acf:0xb608000d39887dca!8m2!3d38.7171315!4d-9.1507597!16s%2Fg%2F11g0h21t0g?entry=ttu
"""
def parse_coords(coords:str)->Coords:
    if not coords.startswith("@") or not coords.endswith("z"):
        raise ValueError(f"Invalid coordinates: {coords}")
    lat, lon, _ignored = coords.removeprefix("@").removesuffix("z").split(",")

    return Coords( lon=float(lon), lat=float(lat), )

def parse_data(data:str):
    if not data.startswith("data=!"):
        raise ValueError(f"invalid data: {data}")

    data_parts = data.split("!")
    for part in data_parts:
        if part.startswith("3d"):
            lat = float(part[2:])
        elif part.startswith("4d"):
            lon = float(part[2:])

    return Coords(lat=lat,lon=lon)

def is_maps_url(url:str)->bool:
    if re.match("https://goo.gl/maps/.*", url):
        return True
    if re.match("https://www.google.com/maps/.*", url):
        return True
    return False
def parse_link(url:str)->Location:
    if re.match("https://goo.gl/maps/.*", url):
        full_link = resolve_maps_link(url)
    elif re.match("https://www.google.com/maps/.*", url):
        full_link = url
    else:
        raise ValueError(f"not a maps URL: {url}")

    path = urllib3.util.parse_url(full_link).path

    if path.startswith("/maps/place/"):
        _, _maps, _place, name, coords, data = path.split("/")

        # return Location(name=name, coords=parse_coords(coords), maps_link = url)

        coords = parse_data(data)
        return Location(name=name, coords=coords, maps_link=url)

    raise ValueError(f"unsupported path: {path}")

def get_links(doc:docx.Document)->Iterator[docx.text.hyperlink.Hyperlink]:
    for paragraph in doc.paragraphs:
        yield from paragraph.hyperlinks
def main(input_path:Path):

    with input_path.open("rb") as f:
        doc:Document = Document(f)

    kml = simplekml.Kml()
    folder:simplekml.Folder = kml.newfolder(name="From document")

    for link in get_links(doc):
        if not is_maps_url(link.address):
            continue

        try:
            coords = parse_link(link.address).coords
            print(link.text, coords)

            folder.newpoint(name=link.text, coords=[coords])
        except Exception:
            pass


    kml.save("../../data/lisbon.kml")

if __name__ == "__main__":
    main(Path("../../data/Lisbon 2023.docx"))
    # rich.print(parse_link("https://goo.gl/maps/WyoUHrqEoLR3MiJa6"))