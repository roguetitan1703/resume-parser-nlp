import os, sys

project_root = os.getcwd()

print(project_root)


sys.path.append(f"{project_root}\\app")
print(sys.path)

from services import OCRProcessor, ResumeProcessor, NERProcessor