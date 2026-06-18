import streamlit as st
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import zipfile
import io

st.set_page_config(
    page_title="Tamil Content Viewer",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    max-width:900px;
    padding-top:10px;
}

.title-box{
    background:#a80f0f;
    color:white;
    padding:12px;
    text-align:center;
    font-size:18px;
    font-weight:normal;
    margin-bottom:15px;
}

.subtitle-box{
    background:#e5a0a0;
    padding:8px;
    font-size:15px;
    margin-top:10px;
    margin-bottom:10px;
}

.paragraph{
    font-size:13px;
    line-height:1.8;
    text-align:justify;
    margin-bottom:10px;
}

.bullet{
    font-size:13px;
    line-height:1.8;
    margin-left:15px;
    margin-bottom:5px;
}

.caption{
    text-align:center;
    font-size:13px;
    font-weight:bold;
}

section[data-testid="stSidebar"]{
    width:220px !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HTML → XML ----------------

def convert_html_to_xml(html, article_id):

    soup = BeautifulSoup(html, "html.parser")

    xml_lines = []
    xml_lines.append("<set>")

    title_found = False

    processed_bullets = set()

    # Find all bullet texts
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

            processed_bullets.add(
                bullet_text
            )

    # Process all paragraph tags
    for tag in soup.find_all("p"):

        text = tag.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        classes = tag.get("class", [])

        # BULLET
        if text in processed_bullets:

            xml_lines.append("<bullet>")
            xml_lines.append(text)
            xml_lines.append("</bullet>")
            continue

        # TITLE
        if "rasi_name" in classes:

            xml_lines.append("<title>")
            xml_lines.append(text)
            xml_lines.append("</title>")

            xml_lines.append(
                f"<image>{article_id}</image>"
            )

            title_found = True
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

    # If title not found add image manually
    if not title_found:

        xml_lines.insert(
            1,
            f"<image>{article_id}</image>"
        )

    xml_lines.append("</set>")

    return "\n\n".join(xml_lines)


# ---------------- UI ----------------

uploaded_files = st.file_uploader(
    "Upload TXT Files",
    type=["txt"],
    accept_multiple_files=True
)

xml_files = {}

if uploaded_files:

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in uploaded_files:

            article_id = file.name.replace(
                ".txt",
                ""
            )

            html = file.read().decode(
                "utf-8",
                errors="ignore"
            )

            xml_content = convert_html_to_xml(
                html,
                article_id
            )

            xml_name = (
                f"{article_id}.xml"
            )

            xml_files[xml_name] = (
                xml_content
            )

            zipf.writestr(
                xml_name,
                xml_content
            )

    st.sidebar.title("XML Files")

    selected_file = st.sidebar.radio(
        "Select File",
        list(xml_files.keys())
    )

    st.sidebar.download_button(
        "Download ZIP",
        zip_buffer.getvalue(),
        file_name="xml_files.zip",
        mime="application/zip"
    )

    if selected_file:

        root = ET.fromstring(
            xml_files[selected_file]
        )

        for node in root:

            tag = node.tag

            text = (
                node.text.strip()
                if node.text
                else ""
            )

            if tag == "title":

                st.markdown(
                    f"""
                    <div class="title-box">
                    {text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif tag == "subtitle":

                st.markdown(
                    f"""
                    <div class="subtitle-box">
                    {text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif tag == "bullet":

                st.markdown(
                    f"""
                    <div class="bullet">
                    • {text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif tag == "caption":

                st.markdown(
                    f"""
                    <div class="caption">
                    {text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif tag == "hint":

                st.info(text)

            elif tag == "p":

                st.markdown(
                    f"""
                    <div class="paragraph">
                    {text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.download_button(
            "Download Current XML",
            xml_files[selected_file],
            file_name=selected_file,
            mime="application/xml"
        )
