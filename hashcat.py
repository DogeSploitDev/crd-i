import os
import urllib.request
import tarfile
import shutil
import subprocess

# URL to the Hashcat package
hashcat_url = "http://http.us.debian.org/debian/pool/main/h/hashcat/hashcat_6.2.6+ds2-1+b1_arm64.deb"
package_name = "hashcat_6.2.6+ds2-1+b1_arm64.deb"

# Download the package
urllib.request.urlretrieve(hashcat_url, package_name)
print(f"Downloaded {package_name}")

# Ensure the ar command is available
def check_ar_command():
    result = subprocess.run(["which", "ar"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: 'ar' command not found. Please install the 'binutils' package.")
        exit(1)

check_ar_command()

# Create a temporary directory for extraction
extract_dir = "hashcat_extract"
os.makedirs(extract_dir, exist_ok=True)

# Move the .deb file to the extraction directory
shutil.move(package_name, os.path.join(extract_dir, package_name))

# Change the working directory to the extraction directory
os.chdir(extract_dir)

# Extract the .deb package using ar command
def extract_deb(file_path):
    result = subprocess.run(["ar", "x", file_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting {file_path}: {result.stderr}")
        exit(1)

extract_deb(package_name)

# Extract the data.tar.xz or data.tar.gz file
def extract_tar(file_path):
    if os.path.exists(file_path):
        with tarfile.open(file_path) as tar:
            tar.extractall()
        print(f"Extracted {file_path}")
    else:
        print(f"Error: {file_path} not found.")
        exit(1)

if os.path.exists("data.tar.xz"):
    extract_tar("data.tar.xz")
elif os.path.exists("data.tar.gz"):
    extract_tar("data.tar.gz")
else:
    print("Error: data.tar.xz or data.tar.gz not found in the extracted files.")
    exit(1)

# Manually copy files to their destinations
def copy_files(src_dir, dest_dir):
    if os.path.exists(src_dir):
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"Copied files from {src_dir} to {dest_dir}")
    else:
        print(f"Directory {src_dir} does not exist, skipping.")

# Define the directories to copy
copy_files("opt", "/opt")
copy_files("etc", "/etc")
copy_files("usr", "/usr")

print("Files copied to root directories")

# Run the postinst script if it exists (to complete the installation)
postinst_script = os.path.join("DEBIAN", "postinst")
if os.path.exists(postinst_script):
    os.chmod(postinst_script, 0o755)
    subprocess.run([postinst_script], shell=True)
    print("Ran postinst script")

print("Hashcat installed successfully!")
