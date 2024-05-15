# Use an official PyTorch image as a base image
FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip
RUN pip install \
    opencv-python-headless \
    pdf2image \
    pytesseract \
    pandas \
    layoutparser[detectron2] \
    layoutparser[ocr]

# Install Detectron2
RUN pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 --extra-index-url https://download.pytorch.org/whl/cu111
RUN pip install "git+https://github.com/facebookresearch/detectron2.git"

# Copy the application code
COPY . /app

# Run the application
CMD ["python", "LayoutParser.py"]

