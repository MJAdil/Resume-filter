"""Ranking service for multi-criteria candidate evaluation"""
import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


class RankingService:
    """Service for calculating platform scores and adaptive ranking"""
    
    # Default weights for each platform
    DEFAULT_WEIGHTS = {
        "github": 0.25,
        "leetcode": 0.20,
        "codeforces": 0.15,
        "linkedin": 0.15,
        "resume": 0.25
    }
    
    @staticmethod
    def calculate_github_score(data: Dict) -> float:
        """
        Calculate GitHub score based on repos, stars, and followers
        
        Formula: min(100, (public_repos * 2) + (total_stars * 0.5) + (followers * 0.3))
        
        Args:
            data: GitHub profile data with keys: public_repos, total_stars, followers
        
        Returns:
            Score normalized to 0-100 range
        """
        if not data:
            return 0.0
        
        public_repos = data.get("public_repos", 0) or 0
        total_stars = data.get("total_stars", 0) or 0
        followers = data.get("followers", 0) or 0
        
        score = (public_repos * 2) + (total_stars * 0.5) + (followers * 0.3)
        normalized_score = min(100.0, score)
        
        logger.debug(f"GitHub score: {normalized_score:.2f} (repos={public_repos}, stars={total_stars}, followers={followers})")
        
        return normalized_score
    
    @staticmethod
    def calculate_leetcode_score(data: Dict) -> float:
        """
        Calculate LeetCode score based on problems solved
        
        Formula: min(100, (easy_solved * 0.2) + (medium_solved * 0.5) + (hard_solved * 1.0))
        
        Args:
            data: LeetCode profile data with keys: easy_solved, medium_solved, hard_solved
        
        Returns:
            Score normalized to 0-100 range
        """
        if not data:
            return 0.0
        
        easy_solved = data.get("easy_solved", 0) or 0
        medium_solved = data.get("medium_solved", 0) or 0
        hard_solved = data.get("hard_solved", 0) or 0
        
        score = (easy_solved * 0.2) + (medium_solved * 0.5) + (hard_solved * 1.0)
        normalized_score = min(100.0, score)
        
        logger.debug(f"LeetCode score: {normalized_score:.2f} (easy={easy_solved}, medium={medium_solved}, hard={hard_solved})")
        
        return normalized_score
    
    @staticmethod
    def calculate_codeforces_score(data: Dict) -> float:
        """
        Calculate Codeforces score based on rating and contests
        
        Formula: min(100, (max_rating / 30) + (contests_participated * 0.5))
        
        Args:
            data: Codeforces profile data with keys: max_rating, contests_participated
        
        Returns:
            Score normalized to 0-100 range
        """
        if not data:
            return 0.0
        
        max_rating = data.get("max_rating", 0) or 0
        contests_participated = data.get("contests_participated", 0) or 0
        
        score = (max_rating / 30) + (contests_participated * 0.5)
        normalized_score = min(100.0, score)
        
        logger.debug(f"Codeforces score: {normalized_score:.2f} (rating={max_rating}, contests={contests_participated})")
        
        return normalized_score
    
    @staticmethod
    def calculate_linkedin_score(data: Dict) -> float:
        """
        Calculate LinkedIn score based on profile completeness
        
        Formula:
        - Base score: 70 (for having a profile)
        - +15 if has experience
        - +15 if has education
        - Max: 100
        
        Args:
            data: LinkedIn profile data with keys: has_experience, has_education
        
        Returns:
            Score normalized to 0-100 range
        """
        if not data:
            return 0.0
        
        base_score = 70.0  # Base score for having a profile
        
        has_experience = data.get("has_experience", False)
        has_education = data.get("has_education", False)
        
        if has_experience:
            base_score += 15.0
        if has_education:
            base_score += 15.0
        
        normalized_score = min(100.0, base_score)
        
        logger.debug(f"LinkedIn score: {normalized_score:.2f} (experience={has_experience}, education={has_education})")
        
        return normalized_score
    
    @staticmethod
    def calculate_resume_score(data: Dict) -> float:
        """
        Calculate resume score based on skills, education, and experience
        
        Formula: min(100, (skills_count * 3) + (education_count * 10) + (experience_count * 5))
        
        Args:
            data: Resume data with keys: skills, education, experience (arrays)
        
        Returns:
            Score normalized to 0-100 range
        """
        if not data:
            return 0.0
        
        skills = data.get("skills", []) or []
        education = data.get("education", []) or []
        experience = data.get("experience", []) or []
        
        skills_count = len(skills) if isinstance(skills, list) else 0
        education_count = len(education) if isinstance(education, list) else 0
        experience_count = len(experience) if isinstance(experience, list) else 0
        
        score = (skills_count * 3) + (education_count * 10) + (experience_count * 5)
        normalized_score = min(100.0, score)
        
        logger.debug(f"Resume score: {normalized_score:.2f} (skills={skills_count}, education={education_count}, experience={experience_count})")
        
        return normalized_score
    
    @classmethod
    def compute_final_score(
        cls,
        platform_scores: Dict[str, float],
        weights: Dict[str, float] = None
    ) -> Tuple[float, Dict[str, float], float]:
        """
        Compute final score with adaptive weight redistribution
        
        Args:
            platform_scores: Dictionary of platform names to scores (0-100)
            weights: Optional custom weights (defaults to DEFAULT_WEIGHTS)
        
        Returns:
            Tuple of (final_score, adjusted_weights, confidence_score)
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS.copy()
        
        # Identify available platforms (non-zero scores)
        available_platforms = [p for p, score in platform_scores.items() if score > 0]
        
        if not available_platforms:
            logger.warning("No platform scores available")
            return 0.0, {}, 0.0
        
        # Calculate completeness ratio and confidence
        completeness_ratio = len(available_platforms) / len(cls.DEFAULT_WEIGHTS)
        confidence = 0.70 + (0.30 * completeness_ratio)
        
        # Adaptive weight redistribution
        available_weight = sum(weights.get(p, 0) for p in available_platforms)
        
        if available_weight == 0:
            logger.warning("No weights available for platforms")
            return 0.0, {}, confidence
        
        adjusted_weights = {
            p: weights.get(p, 0) / available_weight
            for p in available_platforms
        }
        
        # Calculate final weighted score
        final_score = sum(
            platform_scores[p] * adjusted_weights[p]
            for p in available_platforms
        )
        
        logger.debug(f"Final score: {final_score:.2f}, Confidence: {confidence:.2f}, Available platforms: {available_platforms}")
        
        return final_score, adjusted_weights, confidence


# Global ranking service instance
ranking_service = RankingService()
