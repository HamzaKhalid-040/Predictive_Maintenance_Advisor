"""
Explanation Module - Reasoning Trace and Explanation Generation

Tracks expert system execution to provide transparent reasoning:
- Which rules fired
- Evidence collected
- Conflict resolution process
- Complete reasoning chain

Used to explain to end-users why a diagnosis was made.
"""

from .tracer import Tracer, ExecutionEvent, ExecutionTracer

__all__ = ['Tracer', 'ExecutionEvent', 'ExecutionTracer']
