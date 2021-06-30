from cryptography.fernet import Fernet

def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)

def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)

# key = Fernet.generate_key()
# # print(key.decode())

# message = "Abhay"
# token = encrypt(message.encode(), key)

# print(decrypt(token, key).decode())

def getKeyToken(message):
    key = Fernet.generate_key()
    token = encrypt(message.encode(), key)
    
    return {key, token}

def validatePassword(message, key, token):
    try:
        password = decrypt(token, key).decode()
    except Exception as e:
        password = '###'


    if password == message:
        return True
    else:
        return False

'''


Send both Key and Token to Mongo users, and when a user type password..genrerate a token and match it with db token..If match ->User is authenticated else ERROR
'''
