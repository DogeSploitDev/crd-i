import os
import urllib.request
import tarfile
import shutil
import subprocess
import tempfile

# List of URLs to the .deb packages for build tools and other applications (arm64 architecture)
package_urls = [
    # Build tools
    "http://ftp.us.debian.org/debian/pool/main/m/make-dfsg/make_4.3-4.1_arm64.deb",
    "http://ftp.us.debian.org/debian/pool/main/g/gcc-10/gcc-10_10.2.1-6_arm64.deb",
    "http://ftp.us.debian.org/debian/pool/main/g/gcc-10/g++-10_10.2.1-6_arm64.deb",
    "http://ftp.us.debian.org/debian/pool/main/b/build-essential/build-essential_12.9_arm64.deb",
    
    # npm
    "http://ftp.us.debian.org/debian/pool/main/n/npm/npm_7.5.2+ds-2_all.deb",
    
    # Chromium and its dependencies
    "http://ftp.us.debian.org/debian/pool/main/c/chromium/chromium_89.0.4389.114-1~deb10u1_arm64.deb",
    "http://ftp.us.debian.org/debian/pool/main/c/chromium/chromium-common_89.0.4389.114-1~deb10u1_arm64.deb",
    "http://ftp.us.debian.org/debian/pool/main/c/chromium/chromium-driver_89.0.4389.114-1~deb10u1_arm64.deb",
]

# Ensure the ar command is available
def check_ar_command():
    result = subprocess.run(["which", "ar"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: 'ar' command not found. Please install the 'binutils' package.")
        exit(1)

check_ar_command()

# Function to download and extract .deb packages
def download_and_extract_package(url):
    package_name = os.path.basename(url)
    with tempfile.TemporaryDirectory() as extract_dir:
        print(f"Using temporary directory: {extract_dir}")

        # Download the package
        try:
            urllib.request.urlretrieve(url, package_name)
            print(f"Downloaded {package_name}")
        except Exception as e:
            print(f"Error downloading {package_name}: {e}")
            exit(1)

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

        # Manually copy files to their destinations with error handling
        def copy_files(src_dir, dest_dir):
            if os.path.exists(src_dir):
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(dest_dir, item)
                    try:
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                        print(f"Copied {s} to {d}")
                    except FileNotFoundError:
                        print(f"Error: {s} does not exist, skipping.")
                    except Exception as e:
                        print(f"Error copying {s} to {d}: {e}")
            else:
                print(f"Directory {src_dir} does not exist, skipping.")

        # Define the directories to copy
        copy_files("opt", "/opt")
        copy_files("etc", "/etc")
        copy_files("usr", "/usr")
        copy_files("lib", "/lib")
        copy_files("lib64", "/lib64")

        print("Files copied to root directories")

        # Run the postinst script if it exists (to complete the installation)
        postinst_script = os.path.join("DEBIAN", "postinst")
        if os.path.exists(postinst_script):
            os.chmod(postinst_script, 0o755)
            subprocess.run([postinst_script], shell=True)
            print("Ran postinst script")

        # Move back to the original working directory for the next package
        os.chdir("..")

# Download and extract each package
for url in package_urls:
    download_and_extract_package(url)

print("Common build tools and applications installed successfully!")
