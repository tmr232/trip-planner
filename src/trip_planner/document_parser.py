import typing

import attrs
import docx.document
import docx.table
import docx.text
import docx.text.hyperlink
import docx.text.paragraph


@attrs.frozen(kw_only=True)
class Link:
    address: str
    text: str
    headings: list[str]


@attrs.frozen(kw_only=True)
class ContentWithHierarchy:
    content: typing.Any
    headings: list[str]


def _table_cell_paragraphs(table: docx.table.Table):
    for row in table.rows:
        for cell in row.cells:
            yield from cell.paragraphs


def _iter_all(d):
    yield d
    if isinstance(d, docx.table.Table):
        for paragraph in _table_cell_paragraphs(d):
            yield from _iter_all(paragraph)
    if not hasattr(d, "iter_inner_content"):
        return
    for content in d.iter_inner_content():
        yield from _iter_all(content)


def iter_content_with_headings(
    document: docx.document.Document,
) -> typing.Iterator[ContentWithHierarchy]:
    headings = []
    levels = []

    for content in _iter_all(document):
        match content:
            case docx.text.paragraph.Paragraph(style=style, text=text):
                if style.name.startswith("Heading"):
                    heading_level = int(style.name.split(" ")[-1])

                    while levels and heading_level <= levels[-1]:
                        levels.pop()
                        headings.pop()
                    levels.append(heading_level)
                    headings.append(text)
        yield ContentWithHierarchy(content=content, headings=headings.copy())


def iter_links_with_headings(document: docx.document.Document) -> typing.Iterator[Link]:
    for item in iter_content_with_headings(document):
        match item.content:
            case docx.text.hyperlink.Hyperlink(address=address, text=text):
                yield Link(address=address, text=text, headings=item.headings)
