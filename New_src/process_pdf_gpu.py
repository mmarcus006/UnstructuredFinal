import os
import sys
import subprocess
from unstructured_inference.models.base import get_model
from unstructured_inference.inference.layout import DocumentLayout
import onnxruntime as ort

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def check_cuda_installation():
    print("Checking CUDA installation:")
    cuda_version = run_command(["nvcc", "--version"])
    print(cuda_version)

def check_gpu_drivers():
    print("Checking GPU drivers:")
    nvidia_smi = run_command(["nvidia-smi"])
    print(nvidia_smi)

def check_cuda_path():
    cuda_path = os.environ.get('CUDA_PATH')
    if cuda_path:
        print(f"CUDA_PATH is set to: {cuda_path}")
        cuda_bin = os.path.join(cuda_path, 'bin')
        if cuda_bin not in os.environ['PATH']:
            print("CUDA bin directory is not in PATH. Adding it now.")
            os.environ['PATH'] = f"{cuda_bin};{os.environ['PATH']}"
    else:
        print("CUDA_PATH is not set in environment variables.")

def is_gpu_available():
    try:
        return 'CUDAExecutionProvider' in ort.get_available_providers()
    except Exception as e:
        print(f"Error checking GPU availability: {e}")
        return False

# Run diagnostic checks
check_cuda_path()
check_cuda_installation()
check_gpu_drivers()

# Check if GPU is available
if is_gpu_available():
    print("GPU is available for ONNX Runtime")
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
else:
    print("GPU is not available for ONNX Runtime. Using CPU instead.")
    providers = ['CPUExecutionProvider']

# Set up ONNX Runtime session options
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Load the YOLOX model
try:
    model = get_model("yolox")
    model.model = ort.InferenceSession(
        model.model_path,
        sess_options=sess_options,
        providers=providers
    )
except Exception as e:
    print(f"Error loading model: {e}")
    print("Attempting to fall back to CPU-only mode...")
    try:
        model = get_model("yolox")
        model.model = ort.InferenceSession(
            model.model_path,
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        print("Successfully loaded model in CPU-only mode.")
    except Exception as e:
        print(f"Error loading model in CPU-only mode: {e}")
        sys.exit(1)

# File path
file_path = r"C:\Users\Miller\PycharmProjects\UnstructuredFinal\New_src\samples\sample.pdf"

# Process the PDF document
print("Starting document processing...")
try:
    layout = DocumentLayout.from_file(file_path, detection_model=model)
    print("Document processing completed.")

    # Print the detected elements
    for i, page in enumerate(layout.pages, 1):
        print(f"\nPage {i}:")
        for element in page.elements:
            print(element.to_dict())

except Exception as e:
    print(f"Error processing document: {e}")

print("\nProcessing complete.")