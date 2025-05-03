import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import os
import io

# Create directory for temporary files
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Make a round passport-style image
def make_round_image(image_data):
    img = Image.open(image_data).convert("RGBA")
    size = (150, 150)
    img = img.resize(size)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    result = Image.new('RGBA', size)
    result.paste(img, (0, 0), mask)
    output = io.BytesIO()
    result.save(output, format="PNG")
    output.seek(0)
    return output

# Create pie chart and save as PNG
def create_pie_chart(region_name, forest_density, non_forest_density, path):
    labels = ['Forest', 'Non-Forest']
    sizes = [forest_density, non_forest_density]
    colors = ['#228B22', '#CCCCCC']
    explode = (0.1, 0)

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors,
           autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')
    plt.title(region_name)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# Generate the PDF document
def generate_pdf(data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1 - Student Info
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "MDP - FOREST (Class 5)", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Name: {data['name']}", ln=True)
    pdf.cell(200, 10, f"Class: {data['class']}", ln=True)
    pdf.cell(200, 10, f"Section: {data['section']}", ln=True)
    pdf.cell(200, 10, f"Roll No: {data['roll_no']}", ln=True)
    pdf.cell(200, 10, f"School: {data['school']}", ln=True)

    # Add profile image
    if data['profile']:
        image_bytes = make_round_image(data['profile'])
        profile_path = os.path.join(OUTPUT_DIR, "profile.png")
        with open(profile_path, "wb") as f:
            f.write(image_bytes.read())
        pdf.image(profile_path, x=150, y=20, w=40, h=40)

    # Page 2 - Forest Images
    if data['images']:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Forest Images", ln=True)
        positions = [(10, 30), (110, 30), (10, 120), (110, 120)]
        for idx, img_file in enumerate(data['images'][:4]):
            img = Image.open(img_file).resize((300, 200))
            path = os.path.join(OUTPUT_DIR, f"forest_{idx}.png")
            img.save(path)
            x, y = positions[idx]
            pdf.image(path, x=x, y=y, w=90, h=60)

    # Page 3 - Pie Charts
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Pie Charts - Forest Density", ln=True)
    chart_data = {
        "Sunderban": (80, 20),
        "Jalpaiguri": (70, 30),
        "Bankura": (60, 40),
        "Burdwan": (75, 25)
    }
    positions = [(10, 30), (110, 30), (10, 120), (110, 120)]
    size = 80
    for idx, (region, (f, nf)) in enumerate(chart_data.items()):
        chart_path = os.path.join(OUTPUT_DIR, f"{region}.png")
        create_pie_chart(region, f, nf, chart_path)
        x, y = positions[idx]
        pdf.image(chart_path, x=x, y=y, w=size, h=size)
        pdf.set_xy(x, y + size + 2)
        pdf.set_font("Arial", size=10)
        pdf.cell(w=size, h=5, txt=region, align='C')

    # Page 4 - English Essay
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "ENGLISH - Views on Forests", ln=True)
    pdf.set_font("Arial", size=12)
    paragraph = """\
    1. Introduction:
    Forests are the lungs of our planet. They take in harmful carbon dioxide and give us fresh oxygen to breathe. 
    Without forests, life on Earth would not be possible. They make our Earth green, healthy, and full of life.

    2. Importance of Forests:
    - Forests provide safe homes to countless animals, birds, and insects.
    - They help in bringing rain and keep our climate cool and fresh.
    - Forests are sources of wood, fruits, honey, herbs, and many useful medicines.
    - Trees prevent soil erosion and keep rivers and mountains strong and clean.

    3. Creative Additions:
    - Write a poem or story about a forest adventure where animals work together to protect nature.
    - Imagine being a tree for a day -- describe your experience standing tall and helping the planet.
    - Think of a festival called "Forest Day" where children plant trees, sing songs, and make posters.
    - Share your ideas for forest slogans like:
        * "Save Forests, Save Future!"
        * "Plant Trees, Breathe Easy!"
        * "Green Earth, Happy Earth!"
    - Describe your dream forest with colorful birds, peaceful rivers, and smiling trees.
    """
    pdf.multi_cell(0, 10, paragraph)

    # Save PDF
    pdf_path = os.path.join(OUTPUT_DIR, f"{data['name'].replace(' ', '_')}_forest_project.pdf")
    pdf.output(pdf_path)
    return pdf_path

# Streamlit UI
st.title("🌿 Forest MDP Project Generator (Class 5)")

with st.form("forest_form"):
    name = st.text_input("Student Name", "Aditya Bhoumick")
    class_name = st.text_input("Class", "V")
    section = st.text_input("Section", "B")
    roll_no = st.text_input("Roll No", "5")
    school = st.text_input("School Name", "PM SHRI KENDRIYA VIDYALAYA IIM JOKA")
    profile = st.file_uploader("Upload Passport Photo (Optional)", type=["png", "jpg", "jpeg"])
    images = st.file_uploader("Upload Up to 4 Forest Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    submitted = st.form_submit_button("Generate PDF")

if submitted:
    data = {
        "name": name,
        "class": class_name,
        "section": section,
        "roll_no": roll_no,
        "school": school,
        "profile": profile,
        "images": images
    }
    pdf_path = generate_pdf(data)
    with open(pdf_path, "rb") as f:
        st.success("✅ Your PDF is ready!")
        st.download_button("📄 Download PDF", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")
