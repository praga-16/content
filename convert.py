from bs4 import BeautifulSoup
import os

INPUT_FOLDER = "."
OUTPUT_FOLDER = "xml_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in os.listdir(INPUT_FOLDER):

    if not file.endswith(".txt"):
        continue

    if file == "dataset.txt":
        continue

    article_id = os.path.splitext(file)[0]

    with open(file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    xml_lines = []
    image_found = False

    xml_lines.append("<set>")

    for tag in soup.find_all(["p", "img"]):

        # IMAGE
        if tag.name == "img":
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
        if "rasi_subheading" in classes and "text-center" in classes:
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

        # BOLD PARAGRAPH
        if tag.find("b"):

            b_tag = tag.find("b")

            bold_text = b_tag.get_text(strip=True)

            full_text = tag.get_text(" ", strip=True)

            remaining_text = full_text.replace(
                bold_text,
                "",
                1
            ).strip()

            xml_lines.append("<p>")

            if remaining_text:
                xml_lines.append(
                    f"<b>{bold_text}</b> {remaining_text}"
                )
            else:
                xml_lines.append(
                    f"<b>{bold_text}</b>"
                )

            xml_lines.append("</p>")
            continue

        # NORMAL PARAGRAPH
        xml_lines.append("<p>")
        xml_lines.append(text)
        xml_lines.append("</p>")

    # If no image found in HTML
    if not image_found:
        xml_lines.insert(
            1,
            f"<image>{article_id}</image>"
        )

    xml_lines.append("</set>")

    output_file = os.path.join(
        OUTPUT_FOLDER,
        f"{article_id}.xml"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(xml_lines))

    print(f"Created: {output_file}")

print("Done! All XML files generated.")
