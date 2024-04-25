import enum
import re
from collections import defaultdict
from pathlib import Path
from typing import Annotated, Callable, NamedTuple, TypedDict

import attrs
import diskcache
import docx
import docx.document
import docx.text.hyperlink
import docx.text.paragraph
import httpx
import rich
import simplekml
import typer
import urllib3

from trip_planner import document_parser
from trip_planner.document_parser import iter_links_with_headings
from trip_planner.google_maps_helpers import DEFAULT_ICON_COLOR, create_stylemap


class Coords(NamedTuple):
    lon: float
    lat: float


@attrs.frozen(order=True)
class Point:
    name: str
    coords: Coords
    headings: list[str] = attrs.field(factory=list, eq=False, order=False)


@attrs.frozen
class Line:
    name: str
    coords: tuple[Coords] = attrs.field(converter=tuple)


def resolve_maps_link(url: str) -> str:
    response = httpx.get(url)

    # Should always be true for shortened URLs
    assert response.is_redirect and response.has_redirect_location

    return response.headers["location"]


def get_data_from_url(url) -> str:
    path = urllib3.util.parse_url(url).path
    assert path is not None, "a path should always exist"
    data = path.rpartition("/")[-1]
    return data


def parse_directions_url(url: str) -> list[Coords] | None:
    """
    https://www.google.com/maps/dir/Magome,+Nakatsugawa,+Gifu,+Japan/Tsumago-juku,+Azuma,+Nagiso,+Kiso+District,+Nagano+399-5302,+Japan/@35.5541856,137.5632207,14z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x601cb71add823007:0x7d766e65361116fa!2m2!1d137.5717516!2d35.5315174!1m5!1m1!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!2m2!1d137.5956667!2d35.5775876!3e2?entry=ttu
    https://www.google.com/maps/dir/Magome,+Nakatsugawa,+Gifu,+Japan/Tsumago-juku,+Azuma,+Nagiso,+Kiso+District,+Nagano+399-5302,+Japan/Tadachi+%E7%94%B0%E7%AB%8B/@35.5541856,137.5632207,14z/data=!4m20!4m19!1m5!1m1!1s0x601cb71add823007:0x7d766e65361116fa!2m2!1d137.5717516!2d35.5315174!1m5!1m1!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!2m2!1d137.5956667!2d35.5775876!1m5!1m1!1s0x601cc9bd3ccb26ed:0x1b1560620d4ac8d0!2m2!1d137.5489597!2d35.5882476!3e2?entry=ttu
    """
    if not is_dir_url(url):
        return None

    data = get_data_from_url(url)
    tagged_data = parse_maps_url_data(data)

    def _iter():
        lat: float | None = None
        lon: float | None = None
        for tag, value in tagged_data:
            if tag == "1d":
                lon = float(value)
            elif tag == "2d":
                lat = float(value)

            if None not in (lat, lon):
                yield Coords(lat=lat, lon=lon)
                lat, lon = None, None

    return list(_iter())


class MapTaggedData(NamedTuple):
    tag: str
    value: str


def parse_maps_url_data(data: str) -> list[MapTaggedData]:
    """
    data=!4m20!4m19!1m5!1m1!1s0x601cb71add823007:0x7d766e65361116fa!2m2!1d137.5717516!2d35.5315174!1m5!1m1!1s0x601cb7e4a598bb33:0x87bc2c35315036f6!2m2!1d137.5956667!2d35.5775876!1m5!1m1!1s0x601cc9bd3ccb26ed:0x1b1560620d4ac8d0!2m2!1d137.5489597!2d35.5882476!3e2
    """
    if not data.startswith("data=!"):
        raise ValueError(f"invalid data {data}")

    def _iter():
        for match in re.finditer(r"!(?P<tag>\d[a-z])(?P<value>[^!]+)", data):
            yield MapTaggedData(tag=match.group("tag"), value=match.group("value"))

    return list(_iter())


def coords_from_data(data: str):
    tagged_data = parse_maps_url_data(data)
    tag_dict = dict(tagged_data)
    return Coords(lat=float(tag_dict["3d"]), lon=float(tag_dict["4d"]))


def is_place_url(url: str) -> bool:
    return bool(re.match("https://www.google.com/maps/place/.*", url))


def is_short_map_url(url: str) -> bool:
    return bool(re.match("https://goo.gl/maps/.*", url))


def is_long_map_url(url: str) -> bool:
    return bool(re.match("https://www.google.com/maps/.*", url))


def is_maps_url(url: str) -> bool:
    return is_short_map_url(url) or is_long_map_url(url)


def is_dir_url(url: str) -> bool:
    return bool(re.match("https://www.google.com/maps/dir/.*", url))


def get_coords_from_url(url: str) -> Coords:
    data = get_data_from_url(url)
    return coords_from_data(data)


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
        if not is_short_map_url(url):
            raise ValueError(f"requires shortened google-maps url, got {url}")

        return self._cached_resolver(url)

    def _point_from_link(self, link: document_parser.Link) -> Point | None:
        url = link.address
        if is_short_map_url(url):
            url = self._resolve_gmaps_url(url)
        if not is_place_url(url):
            return None
        coords = get_coords_from_url(url)

        return Point(name=link.text, coords=coords, headings=link.headings)

    def _points_from_links(self, links: list[document_parser.Link]) -> list[Point]:
        return list(filter(None, map(self._point_from_link, links)))

    def map_from_docx(
        self,
        doc: docx.document.Document,
        output: Path,
    ):
        links = list(iter_links_with_headings(doc))
        for link in links:
            rich.print(link)
        kml = simplekml.Kml()

        stylemaps: dict[str, simplekml.StyleMap] = {}

        def _stylemap(name: str, color: str = DEFAULT_ICON_COLOR):
            new_stylemap = create_stylemap(name=name, color=color)
            stylemap = stylemaps.get(name, new_stylemap)
            if stylemap is new_stylemap:
                # Styles and stylemaps must reside at the top-level of the document for Google Maps
                # to use them.
                kml.stylemaps.append(stylemap)
            return stylemap

        points = self._points_from_links(links)

        groups: defaultdict[Category, set[Point]] = defaultdict(set)
        for point in points:
            groups[categorize_point(point)].add(point)

        for category, grouped_points in groups.items():
            folder: simplekml.Folder = kml.newfolder(name=category.name)

            for point in sorted(grouped_points):
                kml_point: simplekml.Point = folder.newpoint(
                    name=point.name, coords=[point.coords]
                )
                kml_point.stylemap = _stylemap(**category.icon_info)

        kml.save(str(output))

    def __enter__(self):
        self._cache.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cache.__exit__(None, None, None)
        return False


class IconInfo(TypedDict):
    name: str
    color: str


class Category(enum.Enum):
    Travel = enum.auto()
    Hotel = enum.auto()
    Default = enum.auto()

    @property
    def icon_info(self) -> IconInfo:
        match self:
            case Category.Travel:
                return IconInfo(name="Train", color="1a237e")
            case Category.Hotel:
                return IconInfo(name="Hotel", color="795548")
            case Category.Default:
                return IconInfo(name="Pin", color="c2185b")


def categorize_point(point: Point) -> Category:
    if "station" in point.name.lower():
        return Category.Travel
    elif "bookings" in " ".join(point.headings).lower():
        return Category.Hotel
    return Category.Default


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
        doc: docx.document.Document = docx.Document(f)

    with MapMaker.with_cache(cache) as map_maker:
        map_maker.map_from_docx(doc, out)


if __name__ == "__main__":
    app()
