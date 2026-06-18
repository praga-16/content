
import streamlit as st
from bs4 import BeautifulSoup
import zipfile
import io

st.set_page_config(
    page_title="TXT → XML Converter",
    layout="wide"
)

st.title("TXT → XML Converter")

uploaded_files = st.file_uploader(
    "Upload TXT Files",
    type=["txt"],
    accept_multiple_files=True
)

def convert_html_to_xml(html, article_id):

    soup = BeautifulSoup(html, "html.parser")

    xml_lines = []
    image_found = False

    xml_lines.append("<set>")

    for tag in soup.find_all(["p", "img", "hr"]):

        # LINE
        if tag.name == "hr":
            xml_lines.append("<line></line>")
            continue

        # IMAGE
        if tag.name == "img":

            # Ignore bullet icon image
            if "iot_bullet" in tag.get("class", []):
                continue

            xml_lines.append(f"<image>{article_id}</image>")
            image_found = True
            continue

        classes = tag.get("class", [])
        text = tag.get_text("\n", strip=True)

        if not text and not tag.find("img", class_="iot_bullet"):
            continue

        # TITLE
        if "rasi_name" in classes:
            xml_lines.append("<title>")
            xml_lines.append(text)
            xml_lines.append("</title>")
            continue

        # HINT
        if (
            "rasi_subheading" in classes
            and "text-center" in classes
        ):
            xml_lines.append("<hint>")
            xml_lines.append(text)
            xml_lines.append("</hint>")
            continue

        # SUBTITLE
        if "rasi_subheading" in classes:
            xml_lines.append("<subtitle>")
            xml_lines.append(text)
            xml_lines.append("</subtitle>")
            continue

        # CAPTION
        if (
            "text-center" in classes
            and "txt_bold" in classes
        ):
            xml_lines.append("<caption>")
            xml_lines.append(text)
            xml_lines.append("</caption>")
            continue

        # BULLET
        # BULLET DIV
        if (
            tag.name == "div"
            and tag.find("img", class_="iot_bullet")
        ):
        
            bullet_p = tag.find("p")
        
            if bullet_p:
        
                bullet_text = bullet_p.get_text(
                    " ",
                    strip=True
                )
        
                xml_lines.append("<bullet>")
                xml_lines.append(bullet_text)
                xml_lines.append("</bullet>")
        
            continue

        # BOLD PARAGRAPH
        if tag.find("b"):

            inner_html = tag.decode_contents()

            xml_lines.append("<p>")
            xml_lines.append(inner_html)
            xml_lines.append("</p>")
            continue

        # NORMAL PARAGRAPH
        xml_lines.append("<p>")
        xml_lines.append(text)
        xml_lines.append("</p>")

    # If image not found, add image from filename
    if not image_found:
        xml_lines.insert(1, f"<image>{article_id}</image>")

    xml_lines.append("</set>")

    return "\n\n".join(xml_lines)


if uploaded_files:

    total = len(uploaded_files)

    st.success(f"{total} file(s) uploaded")

    progress = st.progress(0)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for idx, uploaded_file in enumerate(uploaded_files):

            article_id = uploaded_file.name.replace(".txt", "")

            html = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

            xml_content = convert_html_to_xml(
                html,
                article_id
            )

            zip_file.writestr(
                f"{article_id}.xml",
                xml_content
            )

            progress.progress(
                int(((idx + 1) / total) * 100)
            )

    st.success("Conversion Completed")

    st.download_button(
        label="Download XML ZIP",
        data=zip_buffer.getvalue(),
        file_name="xml_files.zip",
        mime="application/zip"
    )

