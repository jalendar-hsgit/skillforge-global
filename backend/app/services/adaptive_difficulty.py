"""
Adaptive difficulty engine for quiz questions.
Adjusts difficulty based on user performance metrics.
"""
from __future__ import annotations

from typing import Literal
import statistics


class AdaptiveDifficultyEngine:
    """
    Adjusts quiz difficulty based on user performance.
    
    Metrics considered:
    - Correctness rate (primary)
    - Average response time
    - Streak of correct/incorrect answers
    """
    
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
    
    def calculate_next_difficulty(
        self,
        current_difficulty: Literal["easy", "medium", "hard"],
        answered_questions: list[dict],
        target_correctness: float = 0.65
    ) -> Literal["easy", "medium", "hard"]:
        """
        Determine next question difficulty based on recent performance.
        
        Args:
            current_difficulty: Current difficulty level
            answered_questions: List of {correct: bool, time_ms: int, difficulty: str}
            target_correctness: Target success rate (default 65% for optimal learning)
        
        Returns:
            Next difficulty level
        """
        if not answered_questions:
            return current_difficulty
        
        # Calculate recent performance (last 3-5 questions)
        recent = answered_questions[-min(5, len(answered_questions)):]
        correctness_rate = sum(1 for q in recent if q.get("correct", False)) / len(recent)
        
        # Check for streak
        recent_streak = self._calculate_streak(recent)
        
        # Calculate average response time (normalized)
        avg_time_ms = statistics.mean([q.get("time_ms", 30000) for q in recent])
        fast_response = avg_time_ms < 15000  # Under 15 seconds
        
        # Decision logic
        current_idx = self.difficulty_levels.index(current_difficulty)
        
        # Strong performance → increase difficulty
        if correctness_rate >= 0.8 and recent_streak["correct"] >= 3:
            new_idx = min(current_idx + 1, len(self.difficulty_levels) - 1)
        # Perfect + fast → jump up
        elif correctness_rate == 1.0 and fast_response and len(recent) >= 3:
            new_idx = min(current_idx + 1, len(self.difficulty_levels) - 1)
        # Struggling → decrease difficulty
        elif correctness_rate < 0.4 or recent_streak["incorrect"] >= 3:
            new_idx = max(current_idx - 1, 0)
        # Below target → slight decrease
        elif correctness_rate < target_correctness:
            # Only decrease if consistently below target
            if len(answered_questions) >= 5:
                overall_rate = sum(1 for q in answered_questions if q.get("correct", False)) / len(answered_questions)
                if overall_rate < target_correctness:
                    new_idx = max(current_idx - 1, 0)
                else:
                    new_idx = current_idx
            else:
                new_idx = current_idx
        else:
            new_idx = current_idx
        
        return self.difficulty_levels[new_idx]
    
    def _calculate_streak(self, questions: list[dict]) -> dict:
        """Calculate current streak of correct/incorrect answers."""
        if not questions:
            return {"correct": 0, "incorrect": 0}
        
        # Count from most recent backward
        correct_streak = 0
        incorrect_streak = 0
        
        for q in reversed(questions):
            if q.get("correct", False):
                if incorrect_streak > 0:
                    break
                correct_streak += 1
            else:
                if correct_streak > 0:
                    break
                incorrect_streak += 1
        
        return {"correct": correct_streak, "incorrect": incorrect_streak}
    
    def get_performance_context(self, answered_questions: list[dict]) -> dict:
        """
        Generate performance context for LLM adaptive prompts.
        
        Returns:
            Dict with performance metrics for prompt injection
        """
        if not answered_questions:
            return {}
        
        total = len(answered_questions)
        correct = sum(1 for q in answered_questions if q.get("correct", False))
        
        return {
            "total": total,
            "correct": correct,
            "correctness_rate": correct / total if total > 0 else 0,
            "recent_streak": self._calculate_streak(answered_questions[-5:]),
            "difficulty_distribution": self._count_by_difficulty(answered_questions)
        }
    
    def _count_by_difficulty(self, questions: list[dict]) -> dict:
        """Count questions by difficulty level."""
        counts = {"easy": 0, "medium": 0, "hard": 0}
        for q in questions:
            diff = q.get("difficulty", "medium")
            if diff in counts:
                counts[diff] += 1
        return counts
    
    def should_offer_hint(self, recent_questions: list[dict]) -> bool:
        """Determine if user might benefit from a hint."""
        if len(recent_questions) < 2:
            return False
        
        recent = recent_questions[-3:]
        incorrect_count = sum(1 for q in recent if not q.get("correct", False))
        
        # Offer hint if struggling on 2+ recent questions
        return incorrect_count >= 2
    
    def calculate_optimal_time_limit(
        self,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int
    ) -> int:
        """
        Calculate optimal time limit in seconds based on difficulty.
        
        Returns:
            Time limit in seconds
        """
        base_times = {
            "easy": 30,      # 30 seconds per question
            "medium": 45,    # 45 seconds per question
            "hard": 60       # 60 seconds per question
        }
        
        per_question = base_times.get(difficulty, 45)
        total = per_question * num_questions
        
        # Add 20% buffer
        return int(total * 1.2)
