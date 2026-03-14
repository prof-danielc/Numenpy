import os

def verify_separation():
    forbidden = "import pygame"
    # Files are now in parent directory relative to this test
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    target_files = ['logic.py', 'world.py', 'entities.py', 'journal.py']
    
    found_violation = False
    for filename in target_files:
        full_path = os.path.join(base_dir, filename)
        if not os.path.exists(full_path):
            print(f"WARNING: {filename} not found at {full_path}")
            continue
        with open(full_path, 'r') as f:
            content = f.read()
            if forbidden in content:
                print(f"FAILED: {filename} contains Pygame import!")
                found_violation = True
            else:
                print(f"PASSED: {filename} is clean")
                
    if found_violation:
        exit(1)
    else:
        print("SUCCESS: Strict logic separation verified.")

if __name__ == "__main__":
    verify_separation()
