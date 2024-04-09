import re
from pathlib import Path
from typing import Annotated, Callable, Iterator, NamedTuple

import attrs
import diskcache
import docx.text.hyperlink
import httpx
import simplekml
import typer
import urllib3
from docx import Document


class Coords(NamedTuple):
    lon: float
    lat: float


@attrs.frozen
class Point:
    name: str
    coords: Coords


def resolve_maps_link(url: str) -> str:
    response = httpx.get(url)

    # Should always be true for shortened URLs
    assert response.is_redirect and response.has_redirect_location

    return response.headers["location"]


def coords_from_data(data: str):
    if not data.startswith("data=!"):
        raise ValueError(f"invalid data: {data}")

    data_parts = data.split("!")
    for part in data_parts:
        if part.startswith("3d"):
            lat = float(part[2:])
        elif part.startswith("4d"):
            lon = float(part[2:])

    return Coords(lat=lat, lon=lon)


def is_place_url(url: str) -> bool:
    return bool(re.match("https://www.google.com/maps/place/.*", url))


def is_short_map_url(url: str) -> bool:
    return bool(re.match("https://goo.gl/maps/.*", url))


def is_long_map_url(url: str) -> bool:
    return bool(re.match("https://www.google.com/maps/.*", url))


def is_maps_url(url: str) -> bool:
    return is_short_map_url(url) or is_long_map_url(url)


def get_coords_from_url(url: str) -> Coords:
    path = urllib3.util.parse_url(url).path
    assert path is not None, "a path should always exist"
    data = path.rpartition("/")[-1]
    return coords_from_data(data)


def get_links(doc: docx.Document) -> Iterator[docx.text.hyperlink.Hyperlink]:
    for paragraph in doc.paragraphs:
        yield from paragraph.hyperlinks


def get_gmaps_links(doc: docx.Document) -> list[docx.text.hyperlink.Hyperlink]:
    def _iter():
        for link in get_links(doc):
            if is_maps_url(link.address):
                yield link

    return list(_iter())


@attrs.define
class MapMaker:
    _cache: diskcache.Cache
    _cached_resolver: Callable[[str], str]

    @classmethod
    def with_cache(cls, cache_dir: Path) -> "MapMaker":
        cache = diskcache.Cache(directory=str(cache_dir))
        resolver = cache.memoize()(resolve_maps_link)
        return MapMaker(cache=cache, cached_resolver=resolver)

    def _resolve_gmaps_url(self, url: str) -> str:
        if not re.match("https://goo.gl/maps/.*", url):
            raise ValueError(f"requires shortened google-maps url, got {url}")

        return self._cached_resolver(url)

    def _points_from_links(
        self, links: list[docx.text.hyperlink.Hyperlink]
    ) -> list[Point]:
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

    def map_from_docx(self, doc: docx.Document, output: Path):
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


app = typer.Typer()


@app.command()
def main(
    document: Annotated[
        Path, typer.Argument(help="The document to get map links from")
    ],
    out: Annotated[Path, typer.Option(help="The output map")],
    cache: Annotated[Path, typer.Option(help="Cache directory")],
):

    with document.open("rb") as f:
        doc: Document = Document(f)

    with MapMaker.with_cache(cache) as map_maker:
        map_maker.map_from_docx(doc, out)


if __name__ == "__main__":
    app()
