import qrcode
import os
from PIL import Image, ImageTk

# Absolute path to folder where this script resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE_DIR:", BASE_DIR)  # DEBUG: check path

def generate_qr_code(reg_id, student_name, event_name):
    data = f"REG_ID:{reg_id}|STUDENT:{student_name}|EVENT:{event_name}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Absolute folder path
    folder = os.path.join(BASE_DIR, "qr_codes")
    os.makedirs(folder, exist_ok=True)
    print("QR folder path:", folder)  # DEBUG

    # Safe file name
    safe_student = student_name.replace(" ", "_")
    safe_event = event_name.replace(" ", "_")
    file_path = os.path.join(folder, f"{reg_id}_{safe_student}_{safe_event}.png")
    img.save(file_path)
    print("QR saved at:", file_path)

    return file_path

# ------------------- NEW FUNCTION -------------------
# To open QR image for Tkinter display
def get_qr_image(qr_path):
    img = Image.open(qr_path)
    img = img.resize((250, 250))  # Resize for GUI
    return ImageTk.PhotoImage(img)
