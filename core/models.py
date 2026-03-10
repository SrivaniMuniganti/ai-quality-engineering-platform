from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import JSON

Base = declarative_base()


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    feature = Column(String(100))
    priority = Column(String(50))
    acceptance_criteria = Column(Text)
    test_types = Column(String(200))
    raw_input = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_cases = relationship("TestCase", back_populates="requirement", cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="requirement", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    feature = Column(String(100))
    test_type = Column(String(100))
    priority = Column(String(50))
    preconditions = Column(Text)
    steps = Column(Text)
    expected_result = Column(Text)
    test_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="test_cases")
    scripts = relationship("Script", back_populates="test_case", cascade="all, delete-orphan")


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    feature = Column(String(100))
    script_content = Column(Text, nullable=False)
    script_path = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="scripts")
    test_case = relationship("TestCase", back_populates="scripts")
    test_runs = relationship("TestRun", back_populates="script", cascade="all, delete-orphan")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(500))
    feature = Column(String(100))
    status = Column(String(50))
    output = Column(Text)
    error_message = Column(Text)
    duration_seconds = Column(Float)
    script_path = Column(String(1000))
    screenshot_path = Column(String(1000))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    script = relationship("Script", back_populates="test_runs")
    analyses = relationship("Analysis", back_populates="test_run", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(500))
    failure_output = Column(Text)
    root_cause = Column(Text)
    failure_category = Column(String(100))
    suggested_fix = Column(Text)
    fixed_script = Column(Text)
    severity = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="analyses")


class HealingAttempt(Base):
    __tablename__ = "healing_attempts"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(500))
    original_locator = Column(Text)
    suggested_locators = Column(Text)  # stored as string repr of list
    healing_strategy = Column(String(100))
    healed_script = Column(Text)
    status = Column(String(50))  # healed / failed / skipped
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun")
