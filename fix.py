import glob

for file in glob.glob('*.py'):
    if file == 'fix.py': continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace escaped quotes with normal quotes
    content = content.replace('\\"', '"')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed {file}")
