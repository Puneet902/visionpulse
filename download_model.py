import os
import gdown

def download_model():
    url = "https://drive.google.com/uc?id=1u0_bmAhAPG8uuJ1HShgofo7-1z4gga3X"
    output = "lighting.pt"
    if not os.path.exists(output):
        print("Downloading lighting.pt...")
        gdown.download(url, output, quiet=False)
    else:
        print("lighting.pt already exists.")

if __name__ == "__main__":
    download_model()
