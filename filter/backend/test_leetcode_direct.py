"""Direct test of LeetCode GraphQL API"""
import httpx
import asyncio


async def test_leetcode_graphql():
    """Test LeetCode GraphQL API directly"""
    username = "jacoblucas"
    
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
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"Testing LeetCode GraphQL API for user: {username}")
        
        response = await client.post(
            "https://leetcode.com/graphql",
            json={"query": query, "variables": {"username": username}},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nParsed Data:")
            print(f"  - User: {data.get('data', {}).get('matchedUser', {}).get('username')}")
            
            if data.get("data") and data["data"].get("matchedUser"):
                user = data["data"]["matchedUser"]
                submit_stats = user.get("submitStats", {}).get("acSubmissionNum", [])
                
                print(f"  - Ranking: {user.get('profile', {}).get('ranking')}")
                print(f"  - Reputation: {user.get('profile', {}).get('reputation')}")
                print(f"  - Submission Stats:")
                
                for stat in submit_stats:
                    print(f"    - {stat.get('difficulty')}: {stat.get('count')}")


if __name__ == "__main__":
    asyncio.run(test_leetcode_graphql())
