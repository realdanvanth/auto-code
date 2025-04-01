import subprocess
import requests

def run_python_file(file_path):
    try:
        result = subprocess.run(['python3', file_path], capture_output=True, text=True)
        if result.stderr:
            return result.stderr.strip(), None
        return None, result.stdout.strip()  # No errors, return output
    except Exception as e:
        return str(e), None

def query_deepseek(api_key, api_url, user_input):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "deepseek/deepseek-chat:free",
        "messages": [{"role": "user", "content": user_input}]
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        api_response = response.json()
        return api_response['choices'][0]['message']['content']
    else:
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
    file_path = "hello.py"
    API_KEY = 'your api key here '
    API_URL = 'https://openrouter.ai/api/v1/chat/completions'
    while True:
        error_output, program_output = run_python_file(file_path)
        
        if not error_output:
            print(f"{file_path} executed successfully.")
            print("Program Output:")
            print(program_output)
            break  # Exit loop when no errors remain
         
        print(error_output)
        print("DEBUGGING PLEASE WAIT")
        with open(file_path, "r") as f:
            file_contents = f.read()
        
        response = query_deepseek(API_KEY, API_URL, error_output + "\nHere is the file contents:\n" + file_contents + "\nGive me just the final fixed code once.")
        
        if response:
            fixed_code = extract_code(response)
            
            if fixed_code:
                with open(file_path, "w") as f:
                    f.write(fixed_code)
                print(f"fixed")
            else:
                print("Unable to debug")
        else:
            print("Unable to authenticate api")
            break


