"""
generate_fillable_pdf.py
Creates a printable Acupuncture SOAP Note and makes it a fillable PDF (text fields + checkboxes).

Dependencies:
  pip install reportlab pdfrw
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName, PdfObject

PAGE_SIZE = letter  # 612 x 792

def create_base_pdf(filename="acupuncture_soap_base.pdf"):
    width, height = PAGE_SIZE
    c = canvas.Canvas(filename, pagesize=PAGE_SIZE)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 40, "Acupuncture SOAP Note")

    c.setFont("Helvetica", 10)
    # Patient header fields labels
    c.drawString(40, height - 80, "Patient Name:")
    c.drawString(360, height - 80, "Date:")
    c.drawString(40, height - 100, "Diagnosis:")

    # Subjective header and labels
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 130, "S – Subjective")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 150, "Chief Complaints (describe):")
    # box for chief complaints (multiline field)
    c.rect(48, height - 320, 520, 160, stroke=1, fill=0)

    # Sleep
    c.drawString(50, height - 340, "Sleep concerns (check):")

    # ADL
    c.drawString(50, height - 380, "ADL concerns (check):")

    c.drawString(50, height - 420, "Medications:")
    c.rect(120, height - 435, 420, 18, stroke=1, fill=0)

    # Objective
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 470, "O – Objective")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 490, "Pain - Location/Scale:")
    c.rect(160, height - 505, 380, 18, stroke=1, fill=0)

    c.drawString(50, height - 525, "Pain description (check):")

    c.drawString(50, height - 600, "Aggravated by - Prolonged (check):")
    c.drawString(50, height - 645, "Aggravated by - Repetitive (check):")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 690, "A – Assessment")

    c.rect(48, height - 760, 520, 50, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 820 + 20, "P – Plan (treatment / modalities):")

    # Treatment area boxes and signature line
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 740, "Treatment areas / modalities (check):")
    c.drawString(50, 60, "Total Time Spent:")
    c.rect(140, 48, 120, 18, stroke=1, fill=0)

    c.drawString(300, 60, "Acupuncturist Signature:")
    c.rect(460, 48, 120, 18, stroke=1, fill=0)

    c.save()


# ---------- pdfrw helpers to add fields ----------
def _text_field(name, rect, multiline=False):
    ff = 4096 if multiline else 0  # multiline flag
    return PdfDict(
        FT=PdfName('Tx'),
        Type=PdfName('Annot'),
        Subtype=PdfName('Widget'),
        Rect=rect,
        T=PdfObject('({})'.format(name)),
        Ff=ff,
        V=PdfObject('()'),
        DA=PdfObject('/Helv 0 Tf 0 g')
    )

def _checkbox_field(name, rect):
    return PdfDict(
        Type=PdfName('Annot'),
        Subtype=PdfName('Widget'),
        FT=PdfName('Btn'),
        Rect=rect,
        T=PdfObject('({})'.format(name)),
        Ff=0,
        V=PdfName('Off'),
        AS=PdfName('Off'),
    )


def make_fillable_form(input_pdf="acupuncture_soap_base.pdf", output_pdf="fillable_acupuncture_soap.pdf"):
    template = PdfReader(input_pdf)
    page = template.pages[0]
    if not getattr(page, 'Annots', None):
        page.Annots = []

    fields = []
    def rect_from(x, y, w, h):
        return [x, y, x + w, y + h]

    height = PAGE_SIZE[1]

    # Patient, date, diagnosis
    fields.append(_text_field("PatientName", rect_from(120, height - 98, 240, 18)))
    fields.append(_text_field("Date", rect_from(400, height - 98, 130, 18)))
    fields.append(_text_field("Diagnosis", rect_from(120, height - 118, 380, 18)))

    # Chief complaints
    fields.append(_text_field("ChiefComplaints", rect_from(52, height - 316, 516, 152), multiline=True))

    # Sleep checkboxes
    sy = height - 346
    page.Annots.append(_checkbox_field("Sleep_FallingAsleep", rect_from(125, sy, 12, 12)))
    page.Annots.append(_checkbox_field("Sleep_WakingNight", rect_from(225, sy, 12, 12)))
    page.Annots.append(_checkbox_field("Sleep_WakesWithPain", rect_from(325, sy, 12, 12)))
    page.Annots.append(_checkbox_field("Sleep_ReducedAlertness", rect_from(425, sy, 12, 12)))
    page.Annots.append(_checkbox_field("Sleep_Fatigue", rect_from(525, sy, 12, 12)))

    # ADL checkboxes
    adl_y = height - 378
    adl_names = [
        "ADL_GetOutOfBed", "ADL_HouseholdChores", "ADL_Bathing", "ADL_Dressing",
        "ADL_PutOnSocksShoes", "ADL_Sweeping", "ADL_Cleaning", "ADL_TakingOutTrash",
        "ADL_Laundry", "ADL_GroceryShopping"
    ]
    for i, name in enumerate(adl_names):
        x = 120 + (i % 3) * 150
        y = adl_y - (i // 3) * 18
        page.Annots.append(_checkbox_field(name, rect_from(x, y, 12, 12)))

    # Medications
    page.Annots.append(_text_field("Medications", rect_from(120, height - 436, 420, 16)))

    # Pain location/scale
    page.Annots.append(_text_field("PainLocationScale", rect_from(160, height - 508, 380, 16)))

    # Pain description
    pain_desc = ["Aching", "Sore", "Burning", "Sharp", "Stabbing", "Stinging", "Shooting", "Throbbing", "Cutting", "Dull"]
    for i, p in enumerate(pain_desc):
        x = 50 + (i % 5) * 110
        y = (height - 542) - (i // 5) * 18
        page.Annots.append(_checkbox_field(f"PainDesc_{p}", rect_from(x, y, 12, 12)))

    # Aggravated - prolonged
    prolonged = ["Sitting", "Twisting", "Standing", "Walking", "Driving", "Squatting", "ClimbingStairs", "Stooping", "Bending", "Running", "Kneeling"]
    for i, p in enumerate(prolonged):
        x = 50 + (i % 4) * 130
        y = (height - 610) - (i // 4) * 18
        page.Annots.append(_checkbox_field(f"Aggravated_Prolonged_{p}", rect_from(x, y, 12, 12)))

    # Aggravated - repetitive
    repetitive = ["Lifting", "Carrying", "Pushing", "Pulling", "Gripping", "Grasping", "Reclining", "ArmMovements", "NeckBending", "TactileDistribution", "ApplyingTorque"]
    for i, p in enumerate(repetitive):
        x = 50 + (i % 4) * 130
        y = (height - 666) - (i // 4) * 18
        page.Annots.append(_checkbox_field(f"Aggravated_Repetitive_{p}", rect_from(x, y, 12, 12)))

    # Alleviating factors
    page.Annots.append(_text_field("AlleviatedBy", rect_from(140, height - 694, 420, 18)))

    # Assessment
    page.Annots.append(_text_field("Assessment", rect_from(52, height - 756, 516, 46), multiline=True))

    # Treatment areas
    areas = ["Scalp", "Face", "Ear", "Neck", "Shoulder", "Back", "Abdomen", "Arms", "Pelvis", "Hips_Buttocks", "Knee", "Foot"]
    for i, a in enumerate(areas):
        x = 50 + (i % 4) * 140
        y = 100 + (i // 4) * 18
        page.Annots.append(_checkbox_field(f"Area_{a}", rect_from(x, y, 12, 12)))

    # Modalities
    modalities = ["Acupuncture", "Acupuncture_w_Stim", "Acupuncture_wo_Stim", "ElectricalStim", "SoftTissue", "Myofascial", "HerbalMedicine", "InfraredHeat"]
    for i, m in enumerate(modalities):
        x = 50 + (i % 4) * 140
        y = 40 + (i // 4) * 18
        page.Annots.append(_checkbox_field(f"Modality_{m}", rect_from(x, y, 12, 12)))

    # Time and signature
    page.Annots.append(_text_field("TotalTimeSpent", rect_from(140, 48, 120, 18)))
    page.Annots.append(_text_field("ProviderSignature", rect_from(460, 48, 120, 18)))
    page.Annots.append(_text_field("TreatmentFrequency", rect_from(50, 16, 130, 18)))
    page.Annots.append(_text_field("GoalsForTreatment", rect_from(200, 16, 368, 18)))

    # Register all fields
    for a in page.Annots:
        fields.append(a)

    if not getattr(template.Root, 'AcroForm', None):
        template.Root.AcroForm = PdfDict()
    template.Root.AcroForm.update(
        PdfDict(Fields=fields, NeedAppearances=PdfObject('true'), DA=PdfObject('/Helv 0 Tf 0 g'))
    )

    PdfWriter().write(output_pdf, template)
    print(f"✅ Created: {output_pdf}")


if __name__ == "__main__":
    create_base_pdf()
    make_fillable_form()
