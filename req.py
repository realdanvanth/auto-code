
import subprocess
import requests
import os

def run_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext == ".py":
        cmd = ["python3", file_path]
    elif ext == ".java":
        class_name = os.path.splitext(os.path.basename(file_path))[0]
        compile_result = subprocess.run(["javac", file_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return compile_result.stderr.strip(), None
        cmd = ["java", class_name]
    elif ext == ".c":
        exe_name = os.path.splitext(file_path)[0]
        compile_result = subprocess.run(["gcc", file_path, "-o", exe_name], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return compile_result.stderr.strip(), None
        cmd = ["./" + exe_name]
    elif ext == ".jl":
        cmd = ["julia", file_path]
    elif ext == ".rs":
        rustup_check = subprocess.run(["rustup", "show"], capture_output=True, text=True)
        if "default host" not in rustup_check.stdout:
            return "Rust toolchain is not configured. Run 'rustup default stable' to set it up.", None
        
        exe_name = os.path.splitext(file_path)[0]
        compile_result = subprocess.run(["rustc", file_path, "-o", exe_name], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return compile_result.stderr.strip(), None
        cmd = ["./" + exe_name]
    else:
        return "Unsupported file type", None
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr.strip(), None
    return None, result.stdout.strip()

def query_deepseek(api_key, api_url, user_input):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "deepseek/deepseek-chat:free",#change according to your preference
        "messages": [{"role": "user", "content": user_input}]
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        api_response = response.json()
        return api_response['choices'][0]['message']['content']
    return None

def extract_code(response_text):
    inside_code_block = False
    extracted_code = []
    
    for line in response_text.split("\n"):
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block
            continue
        if inside_code_block:
            extracted_code.append(line)
    
    return "\n".join(extracted_code)

if __name__ == "__main__":
    file_path = input("Enter the file path: ").strip()
    API_KEY = 'your api key here'
    API_URL = 'https://openrouter.ai/api/v1/chat/completions' 
    while True:
        error_output, program_output = run_file(file_path)
        
        if not error_output:
            print(f"{file_path} executed successfully.")
            print("Program Output:")
            print(program_output)
            break
        
        print(error_output)
        print("DEBUGGING PLEASE WAIT")
        with open(file_path, "r") as f:
            file_contents = f.read()
        
        response = query_deepseek(API_KEY, API_URL, error_output + "if java keep the same name for class" + "\nHere is the file contents:\n" + file_contents + "\nGive me just the final fixed code once.")
        
        if response:
            fixed_code = extract_code(response)
            
            if fixed_code:
                with open(file_path, "w") as f:
                    f.write(fixed_code)
                print("Fixed and updated the file.")
            else:
                print("Unable to debug.")
        else:
            print("Unable to authenticate API.")
            break
