"""
Code Snippets Library Models
Reusable code patterns and solutions
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.core.db import Base


class SnippetLanguage(str, Enum):
    python = "python"
    javascript = "javascript"
    typescript = "typescript"
    java = "java"
    cpp = "cpp"
    csharp = "csharp"
    go = "go"
    rust = "rust"
    sql = "sql"
    bash = "bash"


class SnippetCategory(str, Enum):
    arrays = "arrays"
    strings = "strings"
    sorting = "sorting"
    searching = "searching"
    trees = "trees"
    graphs = "graphs"
    dynamic_programming = "dynamic_programming"
    recursion = "recursion"
    data_structures = "data_structures"
    algorithms = "algorithms"
    database = "database"
    web = "web"
    utilities = "utilities"


class CodeSnippet(Base):
    """
    Reusable code patterns and solutions
    """
    __tablename__ = "code_snippets"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)  # SnippetCategory
    
    # Code content
    language = Column(String, nullable=False)  # SnippetLanguage
    code = Column(Text, nullable=False)
    explanation = Column(Text)  # Detailed explanation of how it works
    
    # Tags and search
    tags = Column(JSON)  # ["pattern", "example"]
    keywords = Column(JSON)  # Search keywords
    
    # Relationships
    complexity = Column(String)  # O(n), O(n log n), etc.
    related_snippets = Column(JSON)  # Array of related snippet IDs
    
    # Tracking
    uses_count = Column(Integer, default=0)  # How many times copied
    helpful_count = Column(Integer, default=0)  # Upvotes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    is_community = Column(Boolean, default=False)  # User-submitted snippet


class SnippetVote(Base):
    """
    Track user votes on snippets
    """
    __tablename__ = "snippet_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    snippet_id = Column(Integer, ForeignKey("code_snippets.id"), nullable=False)
    
    vote_type = Column(String, default="helpful")  # helpful, not_helpful
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="snippet_votes")
    snippet = relationship("CodeSnippet")
    
    # Unique constraint - user can only vote once per snippet
    __table_args__ = (UniqueConstraint('user_id', 'snippet_id', name='user_snippet_vote_unique'),)


class SnippetCopy(Base):
    """
    Track when snippets are copied (for analytics)
    """
    __tablename__ = "snippet_copies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    snippet_id = Column(Integer, ForeignKey("code_snippets.id"), nullable=False)
    
    copied_at = Column(DateTime, default=datetime.utcnow)
    context = Column(String)  # Where it was copied from (e.g., "challenge_detail", "snippets_page")
    
    # Relationships
    user = relationship("User", backref="snippet_copies")
    snippet = relationship("CodeSnippet")
