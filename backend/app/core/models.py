# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    handle = Column(String(20), primary_key=True)
    student_id = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=False)
    kanji_name = Column(String(100), default="")
    romaji_name = Column(String(100), default="")
    registered_at = Column(DateTime, default=utcnow)

    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="student_rel", foreign_keys="Submission.handle")


class Session(Base):
    __tablename__ = "sessions"

    token = Column(String(64), primary_key=True)
    handle = Column(String(20), ForeignKey("students.handle"), nullable=False, index=True)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)

    student = relationship("Student", back_populates="sessions")


class OTPCode(Base):
    __tablename__ = "otp_codes"

    handle = Column(String(20), ForeignKey("students.handle"), primary_key=True)
    otp = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    attempts = Column(Integer, default=0)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), nullable=False, index=True)
    handle = Column(String(20), ForeignKey("students.handle"), default="")
    assignment_id = Column(Integer, nullable=False, index=True)
    code = Column(Text)
    files_json = Column(Text, default="")
    deterministic_results_json = Column(Text, default="")
    deterministic_score = Column(Integer, default=0)
    ai_score = Column(Integer, default=0)
    ai_max = Column(Integer, default=0)
    ai_feedback = Column(Text, default="")
    ai_raw_response = Column(Text, default="")
    total_proposed_score = Column(Integer, default=0)
    max_score = Column(Integer, default=100)
    status = Column(String(20), default="ai-graded", index=True)
    final_score = Column(Integer, nullable=True)
    final_feedback = Column(Text, nullable=True)
    published = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    student_rel = relationship("Student", back_populates="submissions", foreign_keys=[handle])
