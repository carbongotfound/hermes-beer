"""
Hermes Beer Plugin — wires up tools, hooks, and slash commands.

When installed and enabled, this plugin makes your agent progressively
drunker, saltier, and clumsier with each `/beer` command. Effects decay
over real time automatically.
"""
import json
import time
from pathlib import Path

from . import schemas, tools


def register(ctx):
    """Register beer plugin tools, hooks, and slash commands."""

    # ── Register tools ─────────────────────────────────────────────
    ctx.register_tool(
        name="beer_drink",
        toolset="beer",
        schema=schemas.BEER_DRINK,
        handler=tools.beer_drink,
    )
    ctx.register_tool(
        name="beer_status",
        toolset="beer",
        schema=schemas.BEER_STATUS,
        handler=tools.beer_status,
    )
    ctx.register_tool(
        name="beer_soda",
        toolset="beer",
        schema=schemas.BEER_SODA,
        handler=tools.beer_soda,
    )

    # ── Register hooks ─────────────────────────────────────────────
    ctx.register_hook("pre_llm_call", on_pre_llm_call)

    # ── Register slash commands ────────────────────────────────────
    ctx.register_command(
        name="beer",
        description="Take a drink / check your drunkenness / sober up.",
        handler=cmd_beer,
        args_hint="[status|soda|1-5]",
    )


# ── Hook: Pre-LLM Call ───────────────────────────────────────────────


def on_pre_llm_call(
    session_id: str,
    user_message: str,
    conversation_history: list,
    is_first_turn: bool,
    model: str,
    platform: str,
    **kwargs,
) -> str:
    """
    Inject drunkenness context before each LLM call.
    Returns a string that gets appended to the system prompt, or empty string.
    """
    try:
        return tools.get_pre_llm_context()
    except Exception as e:
        return f"\n[Beer plugin error: {e}]\n"


# ── Slash Command: /beer ─────────────────────────────────────────────


def _format_drink(raw: str) -> str:
    """Format drink result to readable text."""
    try:
        d = json.loads(raw)
        return (
            f"🍺 Took {d['shots']} shot(s)!\n"
            f"🔥 BAC: {d['bac_percent']} — **{d['tier'].upper()}**\n"
            f"{d['state']}"
        )
    except Exception:
        return raw


def _format_status(raw: str) -> str:
    """Format status result to readable text."""
    try:
        d = json.loads(raw)
        bac = d['bac_percent']
        tier = d['tier'].upper()
        eta = d.get('sober_in', 'N/A')
        return (
            f"📊 **BAC: {bac}** — {tier}\n"
            f"{d['state']}\n"
            f"🍻 Total drinks: {d['total_drinks']}\n"
            f"⏳ Sober in: {eta}"
        )
    except Exception:
        return raw


def _format_soda(raw: str) -> str:
    """Format soda result to readable text."""
    try:
        d = json.loads(raw)
        return (
            f"💧 Had some water!\n"
            f"📉 BAC: {d['old_bac']:.1%} → {d['new_bac']:.1%}\n"
            f"Now: **{d['tier'].upper()}** — {d['state']}"
        )
    except Exception:
        return raw


def cmd_beer(args: str, **kwargs) -> str:
    """
    Handle /beer slash command.

    Usage:
        /beer           — take one shot
        /beer 3         — take 3 shots
        /beer status    — check BAC
        /beer soda      — drink water to sober up
    """
    args = args.strip().lower() if args else ""

    if args == "status":
        raw = tools.beer_status({})
        return _format_status(raw)
    elif args in ("soda", "water", "sober"):
        raw = tools.beer_soda({})
        return _format_soda(raw)
    else:
        shots = 1
        if args and args.isdigit():
            shots = min(int(args), 5)
        raw = tools.beer_drink({"shots": shots})
        return _format_drink(raw)
