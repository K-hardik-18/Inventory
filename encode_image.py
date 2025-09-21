import base64

with open("university_logo.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    with open("str_bytes.txt", "w") as file:
        file.write(encoded_string)

