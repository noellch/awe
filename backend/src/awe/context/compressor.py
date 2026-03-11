"""Context compression strategies."""

from __future__ import annotations

import re

import anthropic

# Strategies that require LLM calls
LLM_STRATEGIES = {"summary"}

# Strategies that are pure logic (no LLM)
LOCAL_STRATEGIES = {"full", "diff_only"}


async def compress(content: str, strategy: str, max_tokens: int = 500) -> str:
    """Compress content using the specified strategy."""
    if strategy == "full":
        return content
    if strategy == "summary":
        return await _compress_summary(content, max_tokens)
    if strategy == "diff_only":
        return _compress_diff_only(content)
    raise ValueError(f"Unknown compression strategy: '{strategy}'")


async def _compress_summary(content: str, max_tokens: int) -> str:
    """Use a cheap LLM to summarize content."""
    client = anthropic.AsyncAnthropic()
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Summarize the following in under {max_tokens} tokens. "
                    "Preserve key decisions, technical details, and action items. "
                    "Be concise but complete.\n\n"
                    f"{content}"
                ),
            }
        ],
    )
    return response.content[0].text


def _compress_diff_only(content: str) -> str:
    """Extract only diff/code-change sections from content.

    Looks for:
    - Unified diff blocks (lines starting with +/- after @@)
    - Markdown code blocks (```...```)
    - Lines containing file paths with changes

    If no diffs are found, returns the original content truncated.
    """
    extracted: list[str] = []

    # Extract unified diff blocks
    diff_pattern = re.compile(
        r"^(---\s+\S+.*?\n\+\+\+\s+\S+.*?\n(?:@@.*?@@.*?\n(?:[+ \-].*?\n)*))+",
        re.MULTILINE,
    )
    diffs = diff_pattern.findall(content)
    if diffs:
        extracted.append("## Code Diffs\n")
        extracted.extend(diffs)

    # Extract markdown code blocks (likely containing code changes)
    code_block_pattern = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
    code_blocks = code_block_pattern.findall(content)
    if code_blocks:
        if not diffs:
            extracted.append("## Code Blocks\n")
        for i, block in enumerate(code_blocks):
            extracted.append(f"```\n{block.strip()}\n```\n")

    # If we found structured content, return it
    if extracted:
        return "\n".join(extracted)

    # Fallback: return first 2000 chars with a note
    truncated = content[:2000]
    if len(content) > 2000:
        truncated += f"\n\n[... truncated, {len(content) - 2000} chars omitted ...]"
    return truncated
