def generate_token(value):
    return value[::-1]  # Reverse string just for simple "encryption"

def check_file_type(filename):
    return filename.endswith(('.pptx', '.docx', '.xlsx'))
