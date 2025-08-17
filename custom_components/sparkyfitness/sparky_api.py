"""SparkyFitness API client."""
import aiohttp

class SparkyFitnessAPI:
    def __init__(self, base_url: str = "https://api.sparkyfitness.com"):
        self.base_url = base_url.rstrip("/")

    async def async_login(self, email: str, password: str) -> str:
        """Authenticate and return JWT token."""
        url = f"{self.base_url}/api/auth/login"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"email": email, "password": password}) as resp:
                if resp.status != 200:
                    raise Exception("Login failed")
                data = await resp.json()
                if "token" not in data:
                    raise Exception("Token not found in response")
                return data["token"]
