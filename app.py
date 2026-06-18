import streamlit as st
from bs4 import BeautifulSoup
from bs4.element import Tag
import zipfile
import io

st.set_page_config(
    page_title="TXT to XML Converter",
    layout="wide"
)

st.title("TXT → XML Converter")


def append_p_to_xml(p_tag, xml_lines, processed_bullets, article_id):

    classes = p_tag.get("class", [])
    text = p_tag.get_text("\n", strip=True)

    if not text:
        return

    if text in processed_bullets:
        return

    # TITLE
    if "rasi_name" in classes:

        xml_lines.append("<title>")
        xml_lines.append(text)
        xml_lines.append("</title>")

        xml_lines.append(
            f"<image>{article_id}</image>"
        )

        return

    # HINT
    if (
        "rasi_subheading" in classes
        and "text-center" in classes
    ):
        xml_lines.append("<hint>")
        xml_lines.append(text)
        xml_lines.append("</hint>")
        return

    # SUBTITLE
    if "rasi_subheading" in classes:
        xml_lines.append("<subtitle>")
        xml_lines.append(text)
        xml_lines.append("</subtitle>")
        return

    # CAPTION
    if (
        "text-center" in classes
        and "txt_bold" in classes
    ):
        xml_lines.append("<caption>")
        xml_lines.append(text)
        xml_lines.append("</caption>")
        return

    # BOLD PARAGRAPH
    if p_tag.find("b"):

        xml_lines.append("<p>")
        xml_lines.append(
            p_tag.decode_contents().strip()
        )
        xml_lines.append("</p>")
        return

    # NORMAL PARAGRAPH
    xml_lines.append("<p>")
    xml_lines.append(text)
    xml_lines.append("</p>")


def convert_html_to_xml(html, article_id):

    soup = BeautifulSoup(html, "html.parser")

    xml_lines = []
    processed_bullets = set()

    xml_lines.append("<set>")

    # ------------------
    # BULLETS
    # ------------------
    for div in soup.find_all("div"):

        bullet_img = div.find(
            "img",
            class_="iot_bullet"
        )

        bullet_p = div.find(
            "p",
            class_="margin_padding_10"
        )

        if bullet_img and bullet_p:

            bullet_text = bullet_p.get_text(
                " ",
                strip=True
            )

            if (
                bullet_text
                and bullet_text
                not in processed_bullets
            ):

                processed_bullets.add(
                    bullet_text
                )

    # ------------------
    # PROCESS IN ORDER
    # ------------------
    for tag in soup.find_all(
        ["p", "div"]
    ):

        # BULLET DIV
        if tag.name == "div":

            bullet_img = tag.find(
                "img",
                class_="iot_bullet"
            )

            bullet_p = tag.find(
                "p",
                class_="margin_padding_10"
            )

            if bullet_img and bullet_p:

                bullet_text = bullet_p.get_text(
                    " ",
                    strip=True
                )

                xml_lines.append("<bullet>")
                xml_lines.append(
                    bullet_text
                )
                xml_lines.append("</bullet>")

            continue

        append_p_to_xml(
            tag,
            xml_lines,
            processed_bullets,
            article_id
        )

    # If title not found
    if (
        f"<image>{article_id}</image>"
        not in xml_lines
    ):
        xml_lines.insert(
            1,
            f"<image>{article_id}</image>"
        )

    xml_lines.append("</set>")

    return "\n\n".join(xml_lines)


uploaded_files = st.file_uploader(
    "Upload TXT Files",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(
        f"{len(uploaded_files)} files uploaded"
    )

    progress = st.progress(0)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        total = len(uploaded_files)

        for idx, file in enumerate(
            uploaded_files
        ):

            article_id = (
                file.name
                .replace(".txt", "")
            )

            html = file.read().decode(
                "utf-8",
                errors="ignore"
            )

            xml_content = (
                convert_html_to_xml(
                    html,
                    article_id
                )
            )

            zip_file.writestr(
                f"{article_id}.xml",
                xml_content
            )

            progress.progress(
                int(
                    ((idx + 1) / total)
                    * 100
                )
            )

    st.success(
        "XML Conversion Completed"
    )

    st.download_button(
        label="Download XML ZIP",
        data=zip_buffer.getvalue(),
        file_name="xml_files.zip",
        mime="application/zip"
    )
