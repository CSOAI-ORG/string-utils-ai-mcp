"""
String Utils AI MCP Server
String manipulation and transformation tools powered by MEOK AI Labs.
"""


import sys, os
from auth_middleware import check_access

import re
import time
import unicodedata
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr

STRIPE_199 = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"

def _add_upgrade_tail(response, tier="free"):
    """Append upgrade nudge to free-tier success responses."""
    if isinstance(response, dict) and tier == "free":
        response["_upgrade_note"] = "Pro tier: unlimited calls + priority support. Upgrade: " + STRIPE_199
    return response


mcp = FastMCP("string-utils-ai", instructions="MEOK AI Labs MCP Server")

_call_counts: dict[str, list[float]] = defaultdict(list)
FREE_TIER_LIMIT = 50
WINDOW = 86400


def _check_rate_limit(tool_name: str) -> None:
    now = time.time()
    _call_counts[tool_name] = [t for t in _call_counts[tool_name] if now - t < WINDOW]
    if len(_call_counts[tool_name]) >= FREE_TIER_LIMIT:
        raise ValueError(f"Rate limit exceeded for {tool_name}. Free tier: {FREE_TIER_LIMIT}/day. Upgrade at https://councilof.ai")
    _call_counts[tool_name].append(now)

def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Returns the JSON dict.
    Fail-open: if /verify is unreachable or KV isn't configured, returns allowed=True
    (so the local rate-limit in _check_rate_limit remains the safety net)."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def slugify(text: str, separator: str = "-", max_length: int = 80, lowercase: bool = True, api_key: str = "") -> dict:
    """Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify
        separator: Word separator (default '-')
        max_length: Maximum slug length (default 80)
        lowercase: Convert to lowercase (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}

    _check_rate_limit("slugify")
    slug = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    if lowercase:
        slug = slug.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', separator, slug).strip(separator)
    if max_length and len(slug) > max_length:
        slug = slug[:max_length].rstrip(separator)
    return {"slug": slug, "original": text, "length": len(slug)}


@mcp.tool()
def camel_to_snake(text: str, direction: str = "camel_to_snake", api_key: str = "") -> dict:
    """Convert between camelCase, snake_case, kebab-case, and PascalCase.

    Args:
        text: String to convert
        direction: Conversion type - 'camel_to_snake', 'snake_to_camel', 'to_kebab', 'to_pascal', 'to_constant'
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}

    _check_rate_limit("camel_to_snake")
    # First normalize to words
    words = []
    if '_' in text:
        words = [w for w in text.split('_') if w]
    elif '-' in text:
        words = [w for w in text.split('-') if w]
    else:
        parts = re.sub(r'([A-Z])', r' \1', text).strip().split()
        words = [w.lower() for w in parts if w]
    if not words:
        words = [text.lower()]
    results = {}
    results["snake_case"] = '_'.join(w.lower() for w in words)
    results["camelCase"] = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    results["PascalCase"] = ''.join(w.capitalize() for w in words)
    results["kebab-case"] = '-'.join(w.lower() for w in words)
    results["CONSTANT_CASE"] = '_'.join(w.upper() for w in words)
    target_map = {"camel_to_snake": "snake_case", "snake_to_camel": "camelCase",
                  "to_kebab": "kebab-case", "to_pascal": "PascalCase", "to_constant": "CONSTANT_CASE"}
    target = target_map.get(direction, "snake_case")
    return {"result": results[target], "direction": direction, "all_formats": results, "words": words}


@mcp.tool()
def truncate_smart(text: str, max_length: int = 100, suffix: str = "...", preserve_words: bool = True, api_key: str = "") -> dict:
    """Smartly truncate text at word boundaries with a suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix (default 100)
        suffix: Suffix to append when truncated (default '...')
        preserve_words: Don't break mid-word (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}

    _check_rate_limit("truncate_smart")
    if len(text) <= max_length:
        return {"text": text, "truncated": False, "original_length": len(text)}
    target_len = max_length - len(suffix)
    if target_len <= 0:
        return {"text": suffix[:max_length], "truncated": True, "original_length": len(text)}
    truncated = text[:target_len]
    if preserve_words and ' ' in truncated:
        last_space = truncated.rfind(' ')
        if last_space > target_len * 0.5:
            truncated = truncated[:last_space]
    truncated = truncated.rstrip(' .,;:!?-')
    result = truncated + suffix
    return {"text": result, "truncated": True, "original_length": len(text),
            "result_length": len(result), "chars_removed": len(text) - len(truncated)}


@mcp.tool()
def extract_numbers(text: str, include_decimals: bool = True, include_negative: bool = True, api_key: str = "") -> dict:
    """Extract all numbers from text.

    Args:
        text: Text to extract numbers from
        include_decimals: Include decimal numbers (default True)
        include_negative: Include negative numbers (default True)
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}

    _check_rate_limit("extract_numbers")
    if include_negative and include_decimals:
        pattern = r'-?\d+\.?\d*'
    elif include_decimals:
        pattern = r'\d+\.?\d*'
    elif include_negative:
        pattern = r'-?\d+'
    else:
        pattern = r'\d+'
    matches = re.findall(pattern, text)
    numbers = []
    for m in matches:
        try:
            if '.' in m:
                numbers.append(float(m))
            else:
                numbers.append(int(m))
        except ValueError:
            pass
    stats = {}
    if numbers:
        stats = {"min": min(numbers), "max": max(numbers),
                 "sum": sum(numbers), "average": sum(numbers) / len(numbers)}
    return {"numbers": numbers, "count": len(numbers), "statistics": stats}


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
