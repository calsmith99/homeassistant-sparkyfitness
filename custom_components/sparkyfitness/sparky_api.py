"""SparkyFitness API client."""
import aiohttp

class SparkyFitnessAPI:
    async def async_get_water_intake(self, token: str, entry_date: str) -> dict:
        """Fetch water intake for a given date."""
        url = f"{self.base_url}/api/measurements/water-intake/{entry_date}"
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception("Failed to fetch water intake")
                return await resp.json()
    async def async_log_water_intake(self, token: str, user_id: str, entry_date: str, change_drinks: int, container_id: int) -> dict:
        """POST a water intake entry."""
        url = f"{self.base_url}/api/measurements/water-intake"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "user_id": user_id,
            "entry_date": entry_date,
            "change_drinks": change_drinks,
            "container_id": container_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to log water intake: {resp.status}")
                return await resp.json()
    async def async_get_user_info(self, token: str) -> dict:
        """Fetch user info using the JWT token."""
        url = f"{self.base_url}/api/auth/user"
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception("Failed to fetch user info")
                return await resp.json()
    async def async_get_goals_for_today(self, token: str) -> dict:
        """Fetch today's goal values."""
        from datetime import date
        today = date.today().isoformat()
        url = f"{self.base_url}/api/goals/for-date?date={today}"
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception("Failed to fetch goals")
                return await resp.json()

    async def async_get_progress_for_today(self, token: str, user_id: str) -> dict:
        """Fetch today's nutrition progress for the user."""
        from datetime import date
        today = date.today().isoformat()
        url = f"{self.base_url}/api/reports/mini-nutrition-trends?userId={user_id}&startDate={today}&endDate={today}"
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception("Failed to fetch progress")
                data = await resp.json()
                # The API returns a list; return the first entry for today if present
                if isinstance(data, list) and data:
                    return data[0]
                return {}
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
