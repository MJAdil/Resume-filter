"""Test script for ranking service"""
import logging
from services.ranking import RankingService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def test_ranking_service():
    """Test ranking service platform scoring and adaptive weights"""
    logger.info("=" * 60)
    logger.info("Testing Ranking Service")
    logger.info("=" * 60)
    
    service = RankingService()
    
    # Test 1: GitHub scoring
    logger.info("\n1. Testing GitHub scoring...")
    github_data = {
        "public_repos": 25,
        "total_stars": 100,
        "followers": 50
    }
    github_score = service.calculate_github_score(github_data)
    logger.info(f"  - Repos: {github_data['public_repos']}, Stars: {github_data['total_stars']}, Followers: {github_data['followers']}")
    logger.info(f"  ✓ GitHub score: {github_score:.2f}/100")
    
    # Test 2: LeetCode scoring
    logger.info("\n2. Testing LeetCode scoring...")
    leetcode_data = {
        "easy_solved": 50,
        "medium_solved": 30,
        "hard_solved": 10
    }
    leetcode_score = service.calculate_leetcode_score(leetcode_data)
    logger.info(f"  - Easy: {leetcode_data['easy_solved']}, Medium: {leetcode_data['medium_solved']}, Hard: {leetcode_data['hard_solved']}")
    logger.info(f"  ✓ LeetCode score: {leetcode_score:.2f}/100")
    
    # Test 3: Codeforces scoring
    logger.info("\n3. Testing Codeforces scoring...")
    codeforces_data = {
        "max_rating": 1500,
        "contests_participated": 20
    }
    codeforces_score = service.calculate_codeforces_score(codeforces_data)
    logger.info(f"  - Max Rating: {codeforces_data['max_rating']}, Contests: {codeforces_data['contests_participated']}")
    logger.info(f"  ✓ Codeforces score: {codeforces_score:.2f}/100")
    
    # Test 4: LinkedIn scoring
    logger.info("\n4. Testing LinkedIn scoring...")
    linkedin_data = {
        "has_experience": True,
        "has_education": True
    }
    linkedin_score = service.calculate_linkedin_score(linkedin_data)
    logger.info(f"  - Has Experience: {linkedin_data['has_experience']}, Has Education: {linkedin_data['has_education']}")
    logger.info(f"  ✓ LinkedIn score: {linkedin_score:.2f}/100")
    
    # Test 5: Resume scoring
    logger.info("\n5. Testing Resume scoring...")
    resume_data = {
        "skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS"],
        "education": ["BS Computer Science"],
        "experience": ["Senior Developer - 5 years"]
    }
    resume_score = service.calculate_resume_score(resume_data)
    logger.info(f"  - Skills: {len(resume_data['skills'])}, Education: {len(resume_data['education'])}, Experience: {len(resume_data['experience'])}")
    logger.info(f"  ✓ Resume score: {resume_score:.2f}/100")
    
    # Test 6: Final score with all platforms
    logger.info("\n6. Testing final score with all platforms...")
    platform_scores = {
        "github": github_score,
        "leetcode": leetcode_score,
        "codeforces": codeforces_score,
        "linkedin": linkedin_score,
        "resume": resume_score
    }
    
    final_score, adjusted_weights, confidence = service.compute_final_score(platform_scores)
    logger.info(f"  ✓ Final score: {final_score:.2f}/100")
    logger.info(f"  ✓ Confidence: {confidence:.2f}")
    logger.info(f"  - Adjusted weights: {adjusted_weights}")
    
    # Verify weights sum to 1.0
    weights_sum = sum(adjusted_weights.values())
    logger.info(f"  - Weights sum: {weights_sum:.4f}")
    assert abs(weights_sum - 1.0) < 0.001, "Weights should sum to 1.0"
    logger.info(f"  ✓ Weights sum to 1.0")
    
    # Test 7: Adaptive weight redistribution (missing platforms)
    logger.info("\n7. Testing adaptive weight redistribution...")
    partial_scores = {
        "github": github_score,
        "leetcode": 0,  # Missing
        "codeforces": 0,  # Missing
        "linkedin": linkedin_score,
        "resume": resume_score
    }
    
    final_score_partial, adjusted_weights_partial, confidence_partial = service.compute_final_score(partial_scores)
    logger.info(f"  - Available platforms: github, linkedin, resume")
    logger.info(f"  ✓ Final score: {final_score_partial:.2f}/100")
    logger.info(f"  ✓ Confidence: {confidence_partial:.2f} (lower due to missing data)")
    logger.info(f"  - Adjusted weights: {adjusted_weights_partial}")
    
    # Verify weights sum to 1.0
    weights_sum_partial = sum(adjusted_weights_partial.values())
    logger.info(f"  - Weights sum: {weights_sum_partial:.4f}")
    assert abs(weights_sum_partial - 1.0) < 0.001, "Weights should sum to 1.0"
    logger.info(f"  ✓ Weights redistributed correctly")
    
    # Test 8: Edge cases
    logger.info("\n8. Testing edge cases...")
    
    # Empty data
    empty_score = service.calculate_github_score({})
    logger.info(f"  - Empty GitHub data: {empty_score:.2f}")
    assert empty_score == 0.0, "Empty data should return 0"
    
    # None data
    none_score = service.calculate_leetcode_score(None)
    logger.info(f"  - None LeetCode data: {none_score:.2f}")
    assert none_score == 0.0, "None data should return 0"
    
    # Score capping at 100
    high_github_data = {
        "public_repos": 100,
        "total_stars": 1000,
        "followers": 500
    }
    capped_score = service.calculate_github_score(high_github_data)
    logger.info(f"  - High GitHub data (should cap at 100): {capped_score:.2f}")
    assert capped_score == 100.0, "Score should be capped at 100"
    
    logger.info(f"  ✓ Edge cases handled correctly")
    
    # Test 9: Confidence score calculation
    logger.info("\n9. Testing confidence score calculation...")
    
    # 1 platform (20% completeness)
    one_platform = {"github": 50.0, "leetcode": 0, "codeforces": 0, "linkedin": 0, "resume": 0}
    _, _, conf_1 = service.compute_final_score(one_platform)
    logger.info(f"  - 1/5 platforms: confidence = {conf_1:.2f}")
    assert abs(conf_1 - 0.76) < 0.01, "Confidence should be 0.76"
    
    # 3 platforms (60% completeness)
    three_platforms = {"github": 50.0, "leetcode": 0, "codeforces": 0, "linkedin": 50.0, "resume": 50.0}
    _, _, conf_3 = service.compute_final_score(three_platforms)
    logger.info(f"  - 3/5 platforms: confidence = {conf_3:.2f}")
    assert abs(conf_3 - 0.88) < 0.01, "Confidence should be 0.88"
    
    # 5 platforms (100% completeness)
    five_platforms = {"github": 50.0, "leetcode": 50.0, "codeforces": 50.0, "linkedin": 50.0, "resume": 50.0}
    _, _, conf_5 = service.compute_final_score(five_platforms)
    logger.info(f"  - 5/5 platforms: confidence = {conf_5:.2f}")
    assert abs(conf_5 - 1.0) < 0.01, "Confidence should be 1.0"
    
    logger.info(f"  ✓ Confidence scores calculated correctly")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ All ranking service tests passed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_ranking_service()
