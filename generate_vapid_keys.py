from vapid import Vapid

# Генерация пары ключей
vapid_keys = Vapid.generate_keys()

# Печать приватного и публичного ключей
print(f"Private Key: {vapid_keys['private_key']}")
print(f"Public Key: {vapid_keys['public_key']}")
