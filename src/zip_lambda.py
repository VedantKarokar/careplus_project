from zipfile import ZipFile
from io import BytesIO

def create_zip():
    with ZipFile(file=r"tickets_silver.zip", mode="w") as zpf:
        zpf.write(filename=r"src/tickets_pipeline/silver.py")
    check = zpf.testzip()
    return check
create_zip()