from pathlib import Path
from typing import Iterator, NamedTuple, Callable

import attrs
import diskcache
import docx
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

def coords_from_data(data:str):
    if not data.startswith("data=!"):
        raise ValueError(f"invalid data: {data}")

    data_parts = data.split("!")
    for part in data_parts:
        if part.startswith("3d"):
            lat = float(part[2:])
        elif part.startswith("4d"):
            lon = float(part[2:])

    return Coords(lat=lat,lon=lon)


def is_place_url(url:str)->bool:
    return bool(re.match("https://www.google.com/maps/place/.*", url))
def is_short_map_url(url:str)->bool:
    return bool(re.match("https://goo.gl/maps/.*", url))

def is_long_map_url(url:str)->bool:
    return bool(re.match("https://www.google.com/maps/.*", url))
def is_maps_url(url:str)->bool:
    return is_short_map_url(url) or is_long_map_url(url)
def parse_link(url:str)->Location:
    if is_short_map_url(url):
        full_link = resolve_maps_link(url)
    elif is_long_map_url(url):
        full_link = url
    else:
        raise ValueError(f"not a maps URL: {url}")

    path = urllib3.util.parse_url(full_link).path

    if path.startswith("/maps/place/"):
        _, _maps, _place, name, coords, data = path.split("/")

        # return Location(name=name, coords=parse_coords(coords), maps_link = url)

        coords = coords_from_data(data)
        return Location(name=name, coords=coords, maps_link=url)

    raise ValueError(f"unsupported path: {path}")

def get_coords_from_url(url:str)->Coords:
    data= urllib3.util.parse_url(url).path.rpartition("/")[-1]
    return coords_from_data(data)

def get_links(doc:docx.Document)->Iterator[docx.text.hyperlink.Hyperlink]:
    for paragraph in doc.paragraphs:
        yield from paragraph.hyperlinks


def get_gmaps_links(doc:docx.Document)->list[docx.text.hyperlink.Hyperlink]:
    def _iter():
        for link in get_links(doc):
            if is_maps_url(link.address):
                yield link

    return list(_iter())

@attrs.frozen
class Point:
    name:str
    coords: Coords

@attrs.define
class MapMaker:
    _cache: diskcache.Cache
    _cached_resolver: Callable[[str], str]

    @classmethod
    def with_cache(cls, cache_dir:Path)->"MapMaker":
        cache = diskcache.Cache(directory=str(cache_dir))
        resolver = cache.memoize()(resolve_maps_link)
        return MapMaker(cache=cache, cached_resolver=resolver)

    def _resolve_gmaps_url(self, url:str)->str:
        if not re.match("https://goo.gl/maps/.*", url):
            raise ValueError(f"requires shortened google-maps url, got {url}")

        return self._cached_resolver(url)

    def _points_from_links(self, links:list[docx.text.hyperlink.Hyperlink])->list[Point]:
        def _iter():
            for link in links:
                url = link.address
                if is_short_map_url(url):
                    url = self._resolve_gmaps_url(url)
                if not is_place_url(url):
                    continue
                coords = get_coords_from_url(url)

                yield Point(name=link.text, coords=coords)
        return list(_iter())


    def map_from_docx(self, doc:docx.Document, output:Path):
        links = get_gmaps_links(doc)
        points = self._points_from_links(links)

        kml = simplekml.Kml()
        folder: simplekml.Folder = kml.newfolder(name="From document")
        for point in points:
            folder.newpoint(name=point.name, coords=[point.coords])

        kml.save(str(output))

    def __enter__(self):
        self._cache.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cache.__exit__(None, None, None)
        return False



def main(input_path:Path):

    with input_path.open("rb") as f:
        doc:Document = Document(f)
    #
    # kml = simplekml.Kml()
    # folder:simplekml.Folder = kml.newfolder(name="From document")
    #
    # for link in get_links(doc):
    #     if not is_maps_url(link.address):
    #         continue
    #
    #     try:
    #         coords = parse_link(link.address).coords
    #         print(link.text, coords)
    #
    #         folder.newpoint(name=link.text, coords=[coords])
    #     except Exception:
    #         pass
    #
    #
    # kml.save("../../data/lisbon.kml")

    with MapMaker.with_cache(Path("../../cache")) as map_maker:
        map_maker.map_from_docx(doc, Path("../../data/lisbon2.kml"))

if __name__ == "__main__":
    main(Path("../../data/Lisbon 2023.docx"))
    # rich.print(parse_link("https://goo.gl/maps/WyoUHrqEoLR3MiJa6"))