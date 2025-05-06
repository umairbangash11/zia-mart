import os
import subprocess

def generate_proto():
    proto_file = "app/product.proto"
    output_dir = "app"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate Python code from proto file
    subprocess.run([
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path={os.path.dirname(proto_file)}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        proto_file
    ])

if __name__ == "__main__":
    generate_proto() 