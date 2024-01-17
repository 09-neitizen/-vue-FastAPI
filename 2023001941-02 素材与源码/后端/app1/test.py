from auth import create_access_token, Auth_tool

password ="123456"
encodepassword = Auth_tool.encode_password(password)
print(encodepassword)