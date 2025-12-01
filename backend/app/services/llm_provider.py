"""
LLM Provider abstraction for AI quiz generation.
Supports: OpenAI, Anthropic, Azure OpenAI, and Ollama.
"""
from __future__ import annotations

import json
import logging
from typing import Literal, AsyncIterator
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """General-purpose text generation. Returns raw string content."""
        pass
    
    @abstractmethod
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> list[dict]:
        """Generate quiz questions synchronously. Returns list of question dicts."""
        pass
    
    @abstractmethod
    async def generate_quiz_questions_stream(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> AsyncIterator[dict]:
        """Stream quiz questions one at a time. Yields question dicts."""


        class MockLLMProvider(LLMProvider):
            """Mock LLM provider for development/testing when API keys are not available."""
    
            async def generate(
                self,
                prompt: str,
                temperature: float = 0.7,
                max_tokens: int = 500,
            ) -> str:
                """Generate mock responses based on prompt content."""
                logger.info("Using MockLLMProvider (test mode)")
        
                # Detect bullet point generation
                if "bullet points" in prompt.lower() or "bullet point" in prompt.lower():
                    return """
        1. Led cross-functional teams in delivering high-impact projects, resulting in 30% increase in operational efficiency
        2. Developed and implemented innovative solutions that reduced processing time by 45% and improved customer satisfaction scores
        3. Optimized workflows and automated routine tasks, saving 200+ hours monthly and reducing operational costs by $50K annually
        4. Collaborated with stakeholders across departments to drive strategic initiatives that generated $500K in new revenue
        5. Managed end-to-end project lifecycles while mentoring junior team members and maintaining 98% on-time delivery rate
                    """
        
                # Detect summary optimization
                if "professional summary" in prompt.lower() or "summary" in prompt.lower() and "optimize" in prompt.lower():
                    return """Results-driven professional with 5+ years of experience delivering innovative solutions and driving measurable business impact. Proven track record of leading cross-functional teams, optimizing processes, and implementing strategic initiatives that enhance efficiency and profitability. Adept at leveraging technology and data analytics to solve complex challenges and deliver exceptional results. Strong communicator with ability to build relationships across all organizational levels."""
        
                # Detect project suggestions
                if "project" in prompt.lower() and "suggest" in prompt.lower():
                    return """
        1. E-Commerce Platform Redesign - Led complete redesign of online shopping platform, improving conversion rate by 25% and user engagement by 40%
        2. Data Analytics Dashboard - Developed real-time analytics dashboard enabling stakeholders to make data-driven decisions 50% faster
        3. Process Automation Initiative - Implemented automation framework reducing manual processing time by 60% and error rate by 85%
        4. Mobile App Development - Spearheaded development of cross-platform mobile application reaching 100K+ downloads in first quarter
        5. Customer Success Program - Designed and launched customer success initiative improving retention rate by 35% and NPS score by 20 points
                    """
        
                # Default generic response
                return "This is a mock AI response. Please configure a real LLM provider (OpenAI, Anthropic, or Ollama) for production use."
    
            async def generate_quiz_questions(
                self,
                topic: str,
                difficulty: Literal["easy", "medium", "hard"],
                num_questions: int,
                options_per_question: int,
                user_context: dict | None = None
            ) -> list[dict]:
                """Generate mock quiz questions."""
                questions = []
                for i in range(num_questions):
                    questions.append({
                        "id": f"q{i+1}",
                        "type": "mcq",
                        "text": f"Mock {difficulty} question {i+1} about {topic}?",
                        "options": [f"Option {chr(65+j)}" for j in range(options_per_question)],
                        "answerIndex": 0,
                        "explanation": "This is a mock explanation. Configure a real LLM provider for actual quiz generation."
                    })
                return questions
    
            async def generate_quiz_questions_stream(
                self,
                topic: str,
                difficulty: Literal["easy", "medium", "hard"],
                num_questions: int,
                options_per_question: int,
                user_context: dict | None = None
            ) -> AsyncIterator[dict]:
                """Stream mock quiz questions."""
                questions = await self.generate_quiz_questions(topic, difficulty, num_questions, options_per_question, user_context)
                for q in questions:
                    yield q
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY or "test" in settings.OPENAI_API_KEY.lower():
            raise ValueError("OPENAI_API_KEY not configured or is a test key")
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def _build_prompt(self, topic: str, difficulty: str, num_questions: int, options: int, context: dict | None) -> str:
        adaptive_hint = ""
        if context and context.get("previous_performance"):
            perf = context["previous_performance"]
            adaptive_hint = f"\n\nAdaptive context: User answered {perf.get('correct', 0)}/{perf.get('total', 0)} correctly in previous questions. Adjust difficulty accordingly."
        
        return f"""Generate {num_questions} multiple-choice quiz questions about "{topic}" at {difficulty} difficulty level.

Requirements:
- Each question must have exactly {options} answer options
- Mark the correct answer index (0-based)
- Include a brief explanation for each correct answer
- Questions should test understanding, not just memorization
- Difficulty level: {difficulty} (easy=fundamental concepts, medium=application/analysis, hard=synthesis/evaluation){adaptive_hint}

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "id": "q1",
    "type": "mcq",
    "text": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answerIndex": 0,
    "explanation": "Brief explanation of why this is correct"
  }}
]

Do not include any markdown formatting or code blocks, just the raw JSON array."""
    
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> list[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator specializing in quiz generation. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            # Strip markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            questions = json.loads(content)
            return questions if isinstance(questions, list) else []
        except Exception as e:
            logger.error(f"OpenAI quiz generation failed: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes concise, high-quality professional resume content."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise
    
    async def generate_quiz_questions_stream(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> AsyncIterator[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Return one valid JSON question object per line."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            buffer = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    buffer += chunk.choices[0].delta.content
                    
                    # Try to extract complete JSON objects
                    while True:
                        try:
                            # Look for complete question objects
                            start = buffer.find("{")
                            if start == -1:
                                break
                            
                            # Find matching closing brace
                            brace_count = 0
                            end = -1
                            for i in range(start, len(buffer)):
                                if buffer[i] == "{":
                                    brace_count += 1
                                elif buffer[i] == "}":
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end = i + 1
                                        break
                            
                            if end == -1:
                                break  # Incomplete object
                            
                            obj_str = buffer[start:end]
                            question = json.loads(obj_str)
                            yield question
                            buffer = buffer[end:]
                        except json.JSONDecodeError:
                            break
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise


class AnthropicProvider(LLMProvider):
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def _build_prompt(self, topic: str, difficulty: str, num_questions: int, options: int, context: dict | None) -> str:
        adaptive_hint = ""
        if context and context.get("previous_performance"):
            perf = context["previous_performance"]
            adaptive_hint = f"\n\nAdaptive context: User answered {perf.get('correct', 0)}/{perf.get('total', 0)} correctly. Adjust difficulty accordingly."
        
        return f"""Generate {num_questions} multiple-choice quiz questions about "{topic}" at {difficulty} difficulty.

Requirements:
- Each question: exactly {options} options
- Provide correct answer index (0-based)
- Include explanation
- Difficulty: {difficulty}{adaptive_hint}

Return valid JSON array only:
[
  {{
    "id": "q1",
    "type": "mcq",
    "text": "Question?",
    "options": ["A", "B", "C", "D"],
    "answerIndex": 0,
    "explanation": "Why correct"
  }}
]"""
    
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> list[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            questions = json.loads(content)
            return questions if isinstance(questions, list) else []
        except Exception as e:
            logger.error(f"Anthropic quiz generation failed: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # Anthropic returns a list of content blocks
            content = "".join(part.text for part in response.content if hasattr(part, "text"))
            return content.strip()
        except Exception as e:
            logger.error(f"Anthropic text generation failed: {e}")
            raise
    
    async def generate_quiz_questions_stream(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> AsyncIterator[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                buffer = ""
                async for text in stream.text_stream:
                    buffer += text
                    
                    # Extract complete JSON objects
                    while True:
                        try:
                            start = buffer.find("{")
                            if start == -1:
                                break
                            
                            brace_count = 0
                            end = -1
                            for i in range(start, len(buffer)):
                                if buffer[i] == "{":
                                    brace_count += 1
                                elif buffer[i] == "}":
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end = i + 1
                                        break
                            
                            if end == -1:
                                break
                            
                            obj_str = buffer[start:end]
                            question = json.loads(obj_str)
                            yield question
                            buffer = buffer[end:]
                        except json.JSONDecodeError:
                            break
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise


class OllamaProvider(LLMProvider):
    """Local Ollama provider for offline quiz generation."""
    
    def __init__(self):
        try:
            import httpx
            self.client = httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL, timeout=60.0)
            self.model = settings.OLLAMA_MODEL
        except ImportError:
            raise ImportError("httpx not installed. Run: pip install httpx")
    
    def _build_prompt(self, topic: str, difficulty: str, num_questions: int, options: int, context: dict | None) -> str:
        adaptive_hint = ""
        if context and context.get("previous_performance"):
            perf = context["previous_performance"]
            adaptive_hint = f" (Adaptive: user got {perf.get('correct', 0)}/{perf.get('total', 0)} correct)"
        
        return f"""Generate {num_questions} quiz questions about "{topic}" at {difficulty} difficulty.
Each question: {options} options, correct index, explanation.{adaptive_hint}
Return JSON array: [{{"id":"q1","type":"mcq","text":"Q?","options":["A","B"],"answerIndex":0,"explanation":"Why"}}]"""
    
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> list[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            response = await self.client.post("/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            response.raise_for_status()
            data = response.json()
            content = data.get("response", "").strip()
            
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            questions = json.loads(content)
            return questions if isinstance(questions, list) else []
        except Exception as e:
            logger.error(f"Ollama quiz generation failed: {e}")
            raise
    
    async def generate_quiz_questions_stream(
        self,
        topic: str,
        difficulty: Literal["easy", "medium", "hard"],
        num_questions: int,
        options_per_question: int,
        user_context: dict | None = None
    ) -> AsyncIterator[dict]:
        prompt = self._build_prompt(topic, difficulty, num_questions, options_per_question, user_context)
        
        try:
            async with self.client.stream("POST", "/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": True
            }) as response:
                response.raise_for_status()
                buffer = ""
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        buffer += chunk.get("response", "")
                        
                        # Extract complete question objects
                        while True:
                            start = buffer.find("{")
                            if start == -1:
                                break
                            
                            brace_count = 0
                            end = -1
                            for i in range(start, len(buffer)):
                                if buffer[i] == "{":
                                    brace_count += 1
                                elif buffer[i] == "}":
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end = i + 1
                                        break
                            
                            if end == -1:
                                break
                            
                            obj_str = buffer[start:end]
                            question = json.loads(obj_str)
                            yield question
                            buffer = buffer[end:]
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        # Ollama API doesn't use temperature/max_tokens the same way; pass prompt and model
        try:
            response = await self.client.post("/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            })
            response.raise_for_status()
            data = response.json()
            content = data.get("response", "")
            return content.strip()
        except Exception as e:
            logger.error(f"Ollama text generation failed: {e}")
            raise


def get_llm_provider() -> LLMProvider:
    """Factory function to get configured LLM provider."""
    # Check if test/mock keys are being used
    if settings.OPENAI_API_KEY and "test" in settings.OPENAI_API_KEY.lower():
        logger.warning("Test API key detected - using MockLLMProvider for development")
        return MockLLMProvider()
    
    if settings.ANTHROPIC_API_KEY and "test" in settings.ANTHROPIC_API_KEY.lower():
        logger.warning("Test API key detected - using MockLLMProvider for development")
        return MockLLMProvider()
    
    provider = settings.AI_PROVIDER.lower()
    
    try:
        if provider == "openai":
            return OpenAIProvider()
        elif provider == "anthropic":
            return AnthropicProvider()
        elif provider == "ollama":
            return OllamaProvider()
        else:
            logger.warning(f"Unknown AI_PROVIDER '{provider}', falling back to OpenAI")
            return OpenAIProvider()
    except (ValueError, ImportError) as e:
        logger.warning(f"LLM provider initialization failed: {e}. Using MockLLMProvider for development.")
        return MockLLMProvider()


def get_provider() -> LLMProvider:
    """Backward-compatible alias used by older modules. Returns configured provider."""
    return get_llm_provider()
