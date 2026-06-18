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

            # Skip bullet icons
            if "iot_bullet" in tag.get("class", []):
                continue

            xml_lines.append(f"<image>{article_id}</image>")
            image_found = True
            continue

        classes = tag.get("class", [])
        text = tag.get_text("\n", strip=True)

        if not text:
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
        if tag.find("img", class_="iot_bullet"):

            bullet_text = tag.get_text(" ", strip=True)

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

    # Add image if no image exists
    if not image_found:
        xml_lines.insert(1, f"<image>{article_id}</image>")

    xml_lines.append("</set>")

    return "\n\n".join(xml_lines)
