def _build_12k_token_prompt() -> str:
    """Build a >=10,000-token synthetic prompt of concatenated dummy tool outputs."""
    blocks: list[str] = []
    for i in range(30):
        block_id = f"TOOL_OUTPUT_BLOCK_{i:03d}"
        anchor = "BURGUNDY_FRAME" if i < 5 else ("AMBER_FRAME" if i >= 25 else "MID_CHAIN_LINK")
        # Padding filler to force each block to ~1600 chars (~400 tokens at 4 chars/token)
        filler = " ".join([f"detail_{j}_value_{anchor.lower()}" for j in range(60)])
        blocks.append(
            f"[{block_id}] Tool: workspace_analysis\n"
            f"Input: query({anchor}_project_{i})\n"
            f"Output: Analyzed project scope for run {i}. "
            f"Detected dependencies: module_a, module_b, shared_utils_v2. "
            f"Estimated complexity: medium. Recommended action: schedule review. "
            f"Confidence score: 0.87. Processing time: 1.2s. "
            f"Cache hit: True. Anchor marker: {anchor}. "
            f"Extended context: {filler}\n"
        )
    prompt = (
        "You are a Helix Prime CEO agent. "
        "Read the following tool-output blocks carefully. "
        "After processing them, answer: which two anchor markers appeared "
        "in the earliest and latest blocks, and what were their block IDs?\n\n"
        + "\n".join(blocks)
    )
    estimated_tokens = len(prompt) // 4
    assert estimated_tokens >= 10_000, (
        f"Prompt too short: ~{estimated_tokens} tokens estimated, need >= 10 000. "
        f"Prompt length: {len(prompt)} chars"
    )
    return prompt