"""Tests for compression strategies."""

from __future__ import annotations

import pytest

from awe.context.compressor import compress, _compress_diff_only


def test_full_strategy_returns_content():
    """Full strategy returns content unchanged."""
    content = "Hello, this is the full output."
    import asyncio
    result = asyncio.run(compress(content, "full"))
    assert result == content


def test_unknown_strategy_raises():
    """Unknown strategy raises ValueError."""
    import asyncio
    with pytest.raises(ValueError, match="Unknown compression strategy"):
        asyncio.run(compress("content", "nonexistent"))


def test_diff_only_extracts_code_blocks():
    """diff_only extracts markdown code blocks."""
    content = """
Here is my analysis of the problem.

The fix is simple:

```python
def fix_email(user):
    if user.email is None:
        return ""
    return user.email
```

This should resolve the 500 error.

```python
def validate(data):
    return data is not None
```
"""
    result = _compress_diff_only(content)
    assert "def fix_email" in result
    assert "def validate" in result
    # Should not contain the prose
    assert "Here is my analysis" not in result


def test_diff_only_extracts_unified_diffs():
    """diff_only extracts unified diff format."""
    content = """
I found the issue. Here's the change needed:

--- a/src/user.py
+++ b/src/user.py
@@ -10,3 +10,5 @@
 def get_email(user):
-    return user.email
+    if user.email is None:
+        return ""
+    return user.email

That should fix it.
"""
    result = _compress_diff_only(content)
    assert "get_email" in result


def test_diff_only_fallback_truncation():
    """diff_only truncates when no structured content found."""
    content = "A" * 5000  # plain text, no diffs or code blocks
    result = _compress_diff_only(content)
    assert len(result) < len(content)
    assert "truncated" in result.lower() or len(result) <= 2000 + 100


def test_diff_only_via_compress_function():
    """diff_only strategy works through the main compress function."""
    import asyncio
    content = "```python\nprint('hello')\n```"
    result = asyncio.run(compress(content, "diff_only"))
    assert "print('hello')" in result
