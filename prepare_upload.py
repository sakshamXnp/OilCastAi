import os
import zipfile
import shutil

# Directories and files to exclude
EXCLUDE_DIRS = {'node_modules', 'venv', '.next', '__pycache__', '.git'}
EXCLUDE_EXTS = {'.db', '.sqlite', '.exe'}

def create_clean_zip(source_path, zip_name):
    print(f"Creating clean zip: {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                
                file_path = os.path.join(root, file)
                # Archive name is the path relative to the source_path
                arc_name = os.path.relpath(file_path, source_path)
                zipf.write(file_path, arc_name)
                # print(f"Added: {arc_name}")

    print(f"\nDone! Created {zip_name}")
    print("You can now upload this ZIP file to GitHub.")

if __name__ == "__main__":
    project_root = os.getcwd() # Assumes running from e:\Oil\oilcast-ai
    zip_output = os.path.join(os.path.dirname(project_root), "OilCastAi_Upload.zip")
    create_clean_zip(project_root, zip_output)
