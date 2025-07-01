import jwt

# Ваши JSON-данные (полезная нагрузка)
payload = {
    "user_id": 123,
    "username": "example_user",
    "permissions": ["read", "write"]
}

# Ваш секретный ключ
secret = "secret"

# Создание JWS (JWT)
encoded_jws = jwt.encode(payload, secret, algorithm="HS256")

print(f"Ваш JWS (подписанный JSON): {encoded_jws}")

# Для проверки подписи и декодирования токена:
try:
    decoded_payload = jwt.decode(encoded_jws, secret, algorithms=["HS256"])
    print(f"Проверка успешна. Исходные данные: {decoded_payload}")
except jwt.InvalidTokenError:
    print("Неверная подпись!")