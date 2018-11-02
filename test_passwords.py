
from passlib.hash import sha256_crypt

password = 'birb'

hashed_password = sha256_crypt.encrypt(password) # registered password
print(hashed_password)
# this is the password the user enters (when logging in, apply same idea):
entered_password = sha256_crypt.encrypt(password)
print(entered_password)

# Above code are not identical

print(sha256_crypt.verify(password, hashed_password))
# Verify that the string entered as the password matches the hashed version