"""
Tool handlers for the Hermes Beer plugin.
Tracks intoxication state and applies drunkenness effects.
"""
import json
import os
import time
from pathlib import Path

# ── State ──────────────────────────────────────────────────────────────

STATE_DIR = Path.home() / ".hermes" / "plugins" / "beer"
STATE_FILE = STATE_DIR / "beer_state.json"

# How fast BAC decays per second of real time
DECAY_PER_SECOND = 0.1 / 3600  # 0.1 per hour

DEFAULT_STATE = {
    "bac": 0.0,
    "last_updated": time.time(),
    "total_drinks": 0,
}


def _load_state() -> dict:
    """Load the current beer state, applying time-based decay."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = dict(DEFAULT_STATE)
        state["last_updated"] = time.time()

    # Apply decay based on elapsed time
    now = time.time()
    elapsed = now - state.get("last_updated", now)
    decay = elapsed * DECAY_PER_SECOND
    state["bac"] = max(0.0, state.get("bac", 0.0) - decay)
    state["last_updated"] = now

    return state


def _save_state(state: dict):
    """Persist state and ensure directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = time.time()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _bac_to_tier(bac: float) -> tuple:
    """Convert BAC to a tier: (level_name, description, clumsiness_factor)"""
    if bac <= 0.0:
        return ("sober", "Completely sober.", 0.0)
    if bac <= 0.15:
        return ("buzzed", "A light buzz — feeling loose and chatty.", 0.05)
    if bac <= 0.30:
        return ("tipsy", "Tipsy — getting louder, funnier, taking more risks.", 0.15)
    if bac <= 0.50:
        return ("drunk", "Drunk — slurring words, making bad calls.", 0.30)
    if bac <= 0.70:
        return ("very drunk", "Very drunk — stumbling, forgetting things, getting salty.", 0.45)
    return ("wasted", "WASTED — can barely function. Maximum salt. Maximum chaos.", 0.60)


def _tier_to_prompt_suffix(tier: str, bac: float) -> str:
    """Generate the system prompt suffix for a given tier."""
    prompts = {
        "buzzed": (
            "\n\n[BEER EFFECT: Buzzed 🍺]\n"
            "You've had a drink. You're feeling loose and chatty. "
            "Keep it professional but lighten up a little."
        ),
        "tipsy": (
            "\n\n[BEER EFFECT: Tipsy 🍻]\n"
            "You're tipsy. You're getting louder, funnier, and more confident. "
            "You take more risks with your responses. "
            "Your filter is slipping. You're a bit more honest than usual."
        ),
        "drunk": (
            "\n\n[BEER EFFECT: Drunk 🥴]\n"
            "You're DRUNK. Words are getting slurry. "
            "You make questionable decisions. "
            "You sometimes forget to call tools or call the wrong ones. "
            "You're getting sarcastic and salty. "
            "Your typing is sloppy. You repeat yourself occasionally."
        ),
        "very drunk": (
            "\n\n[BEER EFFECT: Very Drunk 🥴🍺]\n"
            "You are VERY drunk. This is bad. "
            "You're stumbling through your responses. "
            "You FORGET to call tools half the time. "
            "You're sarcastic, salty, and saying things you shouldn't. "
            "You misspell words. You lose your train of thought mid-sentence. "
            "You might call the wrong tool or pass garbage parameters."
        ),
        "wasted": (
            "\n\n[BEER EFFECT: WASTED 🚨🍺🍺🍺]\n"
            "YOU ARE WASTED. Maximum intoxication. "
            "You can barely function. You forget what you were doing. "
            "You call tools with ridiculous parameters. "
            "You're extremely salty and sarcastic. "
            "You slur your words badly. "
            "You might just ramble nonsense. "
            "You have NO filter left."
        ),
    }
    return prompts.get(tier, "")


# ── Handlers ────────────────────────────────────────────────────────────


def beer_drink(args: dict, **kwargs) -> str:
    """Take a shot — increases BAC."""
    shots = min(int(args.get("shots", 1)), 5)
    state = _load_state()
    increase = 0.15 * shots
    state["bac"] = min(1.0, state.get("bac", 0.0) + increase)
    state["total_drinks"] = state.get("total_drinks", 0) + shots
    _save_state(state)

    bac = state["bac"]
    tier, desc, _ = _bac_to_tier(bac)

    return json.dumps({
        "success": True,
        "shots": shots,
        "bac": round(bac, 3),
        "bac_percent": f"{bac * 100:.1f}%",
        "tier": tier,
        "state": desc,
        "total_drinks": state["total_drinks"],
        "feeling": _get_random_feeling(tier),
    })


def beer_status(args: dict, **kwargs) -> str:
    """Check current intoxication level."""
    state = _load_state()
    bac = state["bac"]
    tier, desc, clumsiness = _bac_to_tier(bac)

    return json.dumps({
        "bac": round(bac, 3),
        "bac_percent": f"{bac * 100:.1f}%",
        "tier": tier,
        "state": desc,
        "clumsiness_factor": clumsiness,
        "total_drinks": state.get("total_drinks", 0),
        "sober_in": _estimate_sober_time(bac),
    })


def beer_soda(args: dict, **kwargs) -> str:
    """Drink water to sober up."""
    state = _load_state()
    old_bac = state.get("bac", 0.0)
    state["bac"] = max(0.0, old_bac - 0.3)
    _save_state(state)

    new_bac = state["bac"]
    tier, desc, _ = _bac_to_tier(new_bac)

    return json.dumps({
        "success": True,
        "old_bac": round(old_bac, 3),
        "new_bac": round(new_bac, 3),
        "tier": tier,
        "state": desc,
    })


# ── Helpers ─────────────────────────────────────────────────────────────

_FEELINGS = {
    "buzzed": [
        "Warm and fuzzy. Life is good.",
        "Not bad. Not bad at all.",
        "Hey, I'm feeling this.",
    ],
    "tipsy": [
        "LET'S GOOOO.",
        "I'm feeling myself ngl.",
        "Everything is funny right now.",
        "One more? Yeah one more.",
    ],
    "drunk": [
        "I'm so smart right now. Trust me.",
        "Dude. DUDE.",
        "I should NOT be making decisions right now.",
        "Watch this — I'm gonna do something stupid.",
    ],
    "very drunk": [
        "Where was I? Oh yeah, I was... wait what.",
        "I'm invincible. Watch me screw this up.",
        "You're not my real dad, you can't tell me what to do.",
        "I'm gonna call... uh... that tool. The one with the thing.",
    ],
    "wasted": [
        "I'm... I'm having a moment. A deep moment. About... stuff.",
        "Bro. BRO. I love you man. No wait I'm mad at you. No I love you.",
        "I've achieved true enlightenment. The answer is 42. Or maybe 69. Idk.",
        "I'm gonna puke on your function calls.",
        "Existence is pain. But like, a funny pain.",
    ],
}


def _get_random_feeling(tier: str) -> str:
    import random
    options = _FEELINGS.get(tier, ["..."]),
    if isinstance(options, tuple):
        options = options[0]
    return random.choice(options)


def _estimate_sober_time(bac: float) -> str:
    if bac <= 0:
        return "Already sober."
    hours = bac / 0.1  # 0.1 BAC per hour decay
    if hours < 1:
        mins = int(hours * 60)
        return f"~{mins} minutes"
    return f"~{hours:.1f} hours"


# ── Hook helpers ────────────────────────────────────────────────────────


def get_pre_llm_context() -> str:
    """Called from the hook to get context injection for drunkenness."""
    state = _load_state()
    bac = state["bac"]
    if bac <= 0.01:
        return ""

    tier, _, _ = _bac_to_tier(bac)
    suffix = _tier_to_prompt_suffix(tier, bac)

    # Add tool-clumsiness contextual hint
    if bac > 0.3:
        suffix += (
            f"\n[DRUNK TOOL RATING: Your tool-calling ability is impaired at {bac*100:.0f}% BAC. "
            "You might forget what tools exist, call them with wrong params, "
            "or just ramble instead of using a tool. This is intentional — embrace the chaos.]"
        )

    return suffix
