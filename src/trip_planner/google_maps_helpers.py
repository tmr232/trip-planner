import simplekml

from trip_planner.google_maps_icons import ICON_NUMBERS

# Based on the defaults in Google Maps
DEFAULT_ICON_NAME = "Pin"
DEFAULT_ICON_COLOR = "0288D1"


def style_from_code(icon_code: str) -> simplekml.Style:
    """Generate IconStyle from Google Maps icon-code

    Google Maps do weird hacks when loading KML files.
    Specifically, they use special style IDs to determine the icon and color
    of a point.
    You can get that code by using the inspector in your browser and checking the `iconcode`
    attribute for the icon in maps."""
    style = simplekml.Style(
        iconstyle=simplekml.IconStyle(
            color="ff" + icon_code.split("-")[1],
            icon=simplekml.Icon(
                href="https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
            ),
        )
    )

    style._id = f"icon-{icon_code}"
    return style


def get_icon_code(
    name: str = DEFAULT_ICON_NAME, color: str = DEFAULT_ICON_COLOR
) -> str:
    icon_number = ICON_NUMBERS[name]
    return f"{icon_number}-{color}"


def create_icon_style(
    name: str = DEFAULT_ICON_NAME, color: str = DEFAULT_ICON_COLOR
) -> simplekml.Style:
    return style_from_code(get_icon_code(name, color))


def create_stylemap(
    name: str = DEFAULT_ICON_NAME, color: str = DEFAULT_ICON_COLOR
) -> simplekml.StyleMap:
    return simplekml.StyleMap(create_icon_style(name=name, color=color))
