import requests

# Base URL
base_url = "http://127.0.0.1:5000"

# Create a session to maintain cookies
session = requests.Session()

# 1. Get initial game state
print("Getting game state...")
response = session.get(f"{base_url}/api/game-state")
print(response.json())
print("-" * 50)

# 2. Start new game
print("Starting new game...")
response = session.post(f"{base_url}/api/new-game")
print(response.json())
print("-" * 50)

# 3. Make a move at position 4 (center)
print("Making move at position 4...")
response = session.post(
    f"{base_url}/api/move",
    json={"position": 4}
)
print(response.json())
print("-" * 50)

# 4. Make another move
print("Making move at position 0...")
response = session.post(
    f"{base_url}/api/move",
    json={"position": 0}
)
print(response.json())
print("-" * 50)

# 5. Check final state
print("Final game state:")
response = session.get(f"{base_url}/api/game-state")
print(response.json())