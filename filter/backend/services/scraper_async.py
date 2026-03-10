"""Async social profile scraper for Codeforces, LeetCode, LinkedIn, and GitHub"""
import httpx
import json
import logging
from typing import Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SocialProfileScraper:
    """Async scraper for social coding profiles"""
    
    def __init__(self, linkedin_api_key: Optional[str] = None, linkedin_provider: str = "scrapingdog", github_token: Optional[str] = None):
        self.codeforces_api = "https://codeforces.com/api"
        self.leetcode_api = "https://leetcode-stats-api.herokuapp.com"
        self.linkedin_api_key = linkedin_api_key
        self.linkedin_provider = linkedin_provider
        self.github_token = github_token
        self.github_api = "https://api.github.com"
    
    def extract_username_from_url(self, url: str, platform: str) -> Optional[str]:
        """Extract username from profile URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if platform == "codeforces":
                if 'profile' in path_parts:
                    idx = path_parts.index('profile')
                    return path_parts[idx + 1] if idx + 1 < len(path_parts) else None
            
            elif platform == "leetcode":
                if path_parts:
                    return path_parts[-1] if path_parts[-1] != 'u' else path_parts[-2] if len(path_parts) > 1 else None
            
            elif platform == "linkedin":
                if 'in' in path_parts:
                    idx = path_parts.index('in')
                    return path_parts[idx + 1] if idx + 1 < len(path_parts) else None
            
            elif platform == "github":
                if path_parts:
                    username = path_parts[0] if path_parts else None
                    if username and username not in ['orgs', 'topics', 'collections', 'events', 'marketplace', 'explore']:
                        return username
            
            return None
        except Exception as e:
            logger.error(f"Error extracting username: {e}")
            return None
    
    async def scrape_codeforces(self, url: str) -> Dict:
        """Scrape Codeforces profile data"""
        username = self.extract_username_from_url(url, "codeforces")
        
        if not username:
            return {"error": "Invalid Codeforces URL", "platform": "codeforces"}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                user_response = await client.get(f"{self.codeforces_api}/user.info?handles={username}")
                user_data = user_response.json()
                
                if user_data.get("status") != "OK":
                    return {"error": "User not found", "platform": "codeforces", "username": username}
                
                user = user_data["result"][0]
                
                rating_response = await client.get(f"{self.codeforces_api}/user.rating?handle={username}")
                rating_data = rating_response.json()
                
                contests_participated = len(rating_data.get("result", [])) if rating_data.get("status") == "OK" else 0
                
                return {
                    "platform": "codeforces",
                    "username": user.get("handle"),
                    "rating": user.get("rating"),
                    "max_rating": user.get("maxRating"),
                    "rank": user.get("rank"),
                    "max_rank": user.get("maxRank"),
                    "contribution": user.get("contribution"),
                    "contests_participated": contests_participated,
                    "friend_count": user.get("friendOfCount"),
                    "profile_url": url
                }
        
        except Exception as e:
            logger.error(f"Codeforces scraping error: {e}")
            return {"error": str(e), "platform": "codeforces", "username": username}
    
    async def scrape_leetcode(self, url: str) -> Dict:
        """Scrape LeetCode profile data using GraphQL API"""
        username = self.extract_username_from_url(url, "leetcode")
        
        if not username:
            return {"error": "Invalid LeetCode URL", "platform": "leetcode"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use GraphQL API directly (more reliable)
                graphql_url = "https://leetcode.com/graphql"
                query = """
                query getUserProfile($username: String!) {
                    matchedUser(username: $username) {
                        username
                        profile {
                            ranking
                            reputation
                        }
                        submitStats {
                            acSubmissionNum {
                                difficulty
                                count
                            }
                        }
                    }
                }
                """
                
                graphql_response = await client.post(
                    graphql_url,
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                
                if graphql_response.status_code == 200:
                    graphql_data = graphql_response.json()
                    
                    if graphql_data.get("data") and graphql_data["data"].get("matchedUser"):
                        user = graphql_data["data"]["matchedUser"]
                        submit_stats = user.get("submitStats", {}).get("acSubmissionNum", [])
                        
                        # Parse submission stats
                        easy_solved = 0
                        medium_solved = 0
                        hard_solved = 0
                        
                        for stat in submit_stats:
                            difficulty = stat.get("difficulty", "").lower()
                            count = stat.get("count", 0)
                            
                            if difficulty == "easy":
                                easy_solved = count
                            elif difficulty == "medium":
                                medium_solved = count
                            elif difficulty == "hard":
                                hard_solved = count
                        
                        return {
                            "platform": "leetcode",
                            "username": user.get("username"),
                            "ranking": user.get("profile", {}).get("ranking"),
                            "reputation": user.get("profile", {}).get("reputation"),
                            "total_solved": easy_solved + medium_solved + hard_solved,
                            "easy_solved": easy_solved,
                            "medium_solved": medium_solved,
                            "hard_solved": hard_solved,
                            "profile_url": url
                        }
                
                return {"error": "User not found or API unavailable", "platform": "leetcode", "username": username}
        
        except Exception as e:
            logger.error(f"LeetCode scraping error: {e}")
            return {"error": str(e), "platform": "leetcode", "username": username}
    
    async def scrape_github(self, url: str) -> Dict:
        """Scrape GitHub profile data"""
        username = self.extract_username_from_url(url, "github")
        
        if not username:
            return {"error": "Invalid GitHub URL", "platform": "github"}
        
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Social-Profile-Scraper"
            }
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                user_response = await client.get(f"{self.github_api}/users/{username}")
                
                if user_response.status_code != 200:
                    return {
                        "error": f"User not found or API error (status {user_response.status_code})",
                        "platform": "github",
                        "username": username
                    }
                
                user_data = user_response.json()
                
                repos_response = await client.get(f"{self.github_api}/users/{username}/repos?sort=updated&per_page=100")
                repos_data = repos_response.json() if repos_response.status_code == 200 else []
                
                total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
                total_forks = sum(repo.get("forks_count", 0) for repo in repos_data)
                
                languages = {}
                for repo in repos_data:
                    lang = repo.get("language")
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                
                top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
                
                top_repos = sorted(
                    [r for r in repos_data if not r.get("fork", False)],
                    key=lambda x: x.get("stargazers_count", 0),
                    reverse=True
                )[:5]
                
                return {
                    "platform": "github",
                    "username": user_data.get("login"),
                    "name": user_data.get("name"),
                    "bio": user_data.get("bio"),
                    "company": user_data.get("company"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email"),
                    "blog": user_data.get("blog"),
                    "twitter_username": user_data.get("twitter_username"),
                    "public_repos": user_data.get("public_repos"),
                    "public_gists": user_data.get("public_gists"),
                    "followers": user_data.get("followers"),
                    "following": user_data.get("following"),
                    "created_at": user_data.get("created_at"),
                    "updated_at": user_data.get("updated_at"),
                    "total_stars": total_stars,  # For ranking service
                    "total_forks": total_forks,
                    "top_languages": [{"language": lang, "repo_count": count} for lang, count in top_languages],
                    "top_repositories": [
                        {
                            "name": repo.get("name"),
                            "description": repo.get("description"),
                            "stars": repo.get("stargazers_count"),
                            "forks": repo.get("forks_count"),
                            "language": repo.get("language"),
                            "url": repo.get("html_url"),
                            "topics": repo.get("topics", [])
                        }
                        for repo in top_repos
                    ],
                    "profile_url": url,
                    "avatar_url": user_data.get("avatar_url")
                }
        
        except Exception as e:
            logger.error(f"GitHub scraping error: {e}")
            return {"error": str(e), "platform": "github", "username": username}
    
    async def scrape_linkedin(self, url: str) -> Dict:
        """Scrape LinkedIn profile using ScrapingDog API"""
        if not self.linkedin_api_key:
            return {
                "platform": "linkedin",
                "error": "No API key provided",
                "url": url,
                "note": "LinkedIn scraping is optional. System works with resume + GitHub + LeetCode + Codeforces data."
            }
        
        try:
            # Extract profile ID from URL
            profile_id = self.extract_username_from_url(url, "linkedin")
            logger.info(f"Extracted LinkedIn profile ID: {profile_id} from URL: {url}")
            
            if not profile_id:
                return {
                    "platform": "linkedin",
                    "error": "Could not extract profile ID from URL",
                    "url": url
                }
            
            # ScrapingDog API endpoint
            api_url = "https://api.scrapingdog.com/profile/"
            params = {
                "api_key": self.linkedin_api_key,
                "type": "profile",
                "id": profile_id
            }
            
            logger.info(f"Calling ScrapingDog API with profile_id: {profile_id}")
            
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.get(api_url, params=params)
                
                if response.status_code != 200:
                    error_msg = f"API returned status {response.status_code}"
                    if response.status_code == 403:
                        error_msg += " - API key may be invalid, expired, or out of credits."
                    elif response.status_code == 401:
                        error_msg += " - Unauthorized. Check your API key."
                    elif response.status_code == 400:
                        error_msg += " - Bad request. The profile may not exist or isn't public."
                    
                    logger.warning(f"LinkedIn API error: {error_msg}")
                    return {
                        "platform": "linkedin",
                        "error": error_msg,
                        "url": url,
                        "profile_id": profile_id
                    }
                
                data = response.json()
                
                # ScrapingDog returns a list with one profile object
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                elif not isinstance(data, dict):
                    return {
                        "platform": "linkedin",
                        "error": "Unexpected response format from API",
                        "url": url
                    }
                
                # Check if profile has experience and education for ranking
                has_experience = bool(data.get("experience") or data.get("experiences"))
                has_education = bool(data.get("education") or data.get("educations"))
                
                # Extract profile data
                return {
                    "platform": "linkedin",
                    "has_experience": has_experience,
                    "has_education": has_education,
                    "full_name": data.get("fullName") or data.get("full_name") or data.get("name"),
                    "headline": data.get("headline"),
                    "summary": data.get("summary") or data.get("about"),
                    "location": data.get("location") or data.get("city"),
                    "connections": data.get("connections") or data.get("connectionsCount"),
                    "follower_count": data.get("followers") or data.get("followersCount"),
                    "profile_url": url,
                    "profile_id": profile_id
                }
        
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
            return {"error": str(e), "platform": "linkedin", "url": url}
    
    async def scrape_all(self, urls: Dict[str, str]) -> Dict:
        """Scrape all provided social profiles concurrently"""
        results = {}
        tasks = []
        platforms = []
        
        if "codeforces" in urls:
            logger.info(f"Scraping Codeforces: {urls['codeforces']}")
            tasks.append(self.scrape_codeforces(urls["codeforces"]))
            platforms.append("codeforces")
        
        if "leetcode" in urls:
            logger.info(f"Scraping LeetCode: {urls['leetcode']}")
            tasks.append(self.scrape_leetcode(urls["leetcode"]))
            platforms.append("leetcode")
        
        if "github" in urls:
            logger.info(f"Scraping GitHub: {urls['github']}")
            tasks.append(self.scrape_github(urls["github"]))
            platforms.append("github")
        
        if "linkedin" in urls:
            logger.info(f"Scraping LinkedIn: {urls['linkedin']}")
            tasks.append(self.scrape_linkedin(urls["linkedin"]))
            platforms.append("linkedin")
        
        # Run all scraping tasks concurrently
        if tasks:
            import asyncio
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for platform, result in zip(platforms, task_results):
                if isinstance(result, Exception):
                    results[platform] = {"error": str(result), "platform": platform}
                else:
                    results[platform] = result
        
        return results
