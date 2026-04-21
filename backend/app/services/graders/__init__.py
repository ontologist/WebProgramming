# Copyright (c) 2026 Yuri Tijerino. All rights reserved.
# 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有.
# Unauthorized copying, modification, or distribution of this file is prohibited.
# 本ファイルの無断複製、改変、配布を禁じます。
"""
Per-assignment grading agents.

Each grader exposes two functions that mirror the legacy grading_service
API, so callers don't need to know which assignments are on the new
agent and which are still on the generic rubric:

    def deterministic(code: str | None, files: dict | None) -> list[dict]
    async def ai_evaluate(code, files, det_results, language) -> dict

`get_grader(assignment_id)` returns the module, or None if this
assignment is still on the legacy grader.
"""

from . import assignment1

_REGISTRY = {
    1: assignment1,
}


def get_grader(assignment_id: int):
    return _REGISTRY.get(assignment_id)
