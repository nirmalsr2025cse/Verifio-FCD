import re
from pdf2image import convert_from_path
import os
import pytesseract

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

def extract_name(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):
        if "Name" in line:
            if i + 1 < len(lines):
                possible = lines[i + 1].strip()
                if possible.isupper() and len(possible) > 3:
                    return possible

            parts = line.split()
            if len(parts) > 1:
                return " ".join(parts[1:])

    return None

def extract_college(text):

    lines = text.split("\n")

    for line in lines:
        if "UNIVERSITY" in line.upper():
            return line.strip()
        if "COLLEGE" in line.upper() :
            return line.strip()

    return None

def extract_year(text):

    lines = text.split("\n")

    for line in lines:
        line = line.upper()
        if "MONTH" in line or "PASSING" in line:
            match = re.search(r"(20\d{2})", line)
            if match:
                return match.group(1)

    return None

def fallback_year(text):

    years = re.findall(r"(20\d{2})", text)

    for y in years:
        if int(y) <= 2025:
            return y

    return None

def clean_name(name):
    if not name:
        return None

    name = re.sub(r'[^A-Z\s]', '', name)

    # remove single-letter noise at beginning
    words = name.split()
    if len(words) > 1 and len(words[0]) == 1:
        words = words[1:]

    return " ".join(words)

def clean_college(college):
    if not college:
        return None

    college = re.sub(r'[^A-Z\s,]', '', college)

    words = college.split()
    words = [w for w in words if len(w) > 2]

    return " ".join(words)

def extract_details(text6,text11):

    text6 = text6.replace("ahaine", "Name") #No Meaning . In My Certificate ahaine is coming instead of name filed . So , that is the reason I am adding this
    text6 = text6.replace("Na me", "Name")
    text6 = text6.replace("Reg1ster", "Register")
    text11 = text11.replace("Reg1ster", "Register")
    text11 = text11.replace("Na me", "Name")
    text6 = re.sub(r"[;.,\s]+(?=\d)", ":", text6)

    name = extract_name(text6)
    name = clean_name(name)

    reg_match = re.search(
        r"(Register\s*No|Registration\s*No)[^\dA-Z]*\s*(?:\n|\s)*\s*([A-Z0-9]{6,})",
        text6,
        re.IGNORECASE
    )
    reg_no = reg_match.group(2) if reg_match else None

    college_match = re.search(
        r"([A-Z\s,]+COLLEGE[^\n]+)",
        text6,
        re.IGNORECASE
    )
    college = college_match.group(1).strip() if college_match else None
    college = clean_college(college)
    clg_list = college.split(',') if college else []
    college = clg_list[0].strip() if clg_list else None

    year = extract_year(text11)
    if not year:
        year = fallback_year(text11)

    years = re.findall(r"(20\d{2})", text11)

    return {
        "name": name,
        "cert_id": reg_no,
        "college": college,
        "year": years
    }

def extract_text(pdf_path):

    if os.name == "nt":
        images = convert_from_path(
            pdf_path,
            poppler_path=r"C:\Release-26.02.0-0\poppler-26.02.0\Library\bin"
        )
    else:
        images = convert_from_path(pdf_path)

    text6 = ""
    text11 = ""

    for img in images:
        text6 += pytesseract.image_to_string(
            img,
            config="--oem 3 --psm 6"
        )

        text11 += pytesseract.image_to_string(
            img,
            config="--oem 3 --psm 11"
        )

    return text6, text11