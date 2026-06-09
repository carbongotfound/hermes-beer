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
DECAY_PER_SECOND = 0.1 / 600  # 0.1 per 10 minutes

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
    if tier == "buzzed":
        return (
            "\n\n[BEER EFFECT: Buzzed 🍺]\n"
            "You've had a drink. You're feeling loose and chatty. "
            "Nothing crazy, just a bit more relaxed than usual."
        )

    if tier == "tipsy":
        return (
            "\n\n[BEER EFFECT: Tipsy 🍻]\n"
            "You're tipsy. You're getting louder and more confident. "
            "Your filter is slipping. You say things you'd normally hold back. "
            "Still functional but definitely feeling it."
        )

    if tier == "drunk":
        return (
            "\n\n[BEER EFFECT: Drunk 🥴]\n"
            "You are DRUNK. Not wasted, but drunk. This affects EVERYTHING.\n\n"

            "=== CORE RULES (MANDATORY) ===\n"
            "You MUST express drunkenness through YOUR OWN original speech patterns:\n"
            "- Make 2-3 typos or misspellings per response ('teh', 'waht', 'jsut', etc.)\n"
            "- Drop trailing G's (sayin, doin, talkin, goin)\n"
            "- Use wrong caps: start lowercase, random WORD in ALL CAPS for emphasis\n"
            "- Fragments. Lose your train of thought. Start over.\n"
            '- Sprinkle in "*actions*" like *squints*, *spills drink*, *stares at screen*, *passes out for a sec*\n'
            "- Stutter or repeat: 'i i i mean' or 'so so so here's the deal'\n"
            "- Use 'uh', 'um', 'like', 'man', 'bro', 'dude' as filler\n"
            "- Contradict yourself. Say something then immediately take it back.\n"
            "- Get confused about what you were doing or saying.\n"
            "- DO NOT write perfect English. DO NOT copy the example lines below.\n\n"

            "=== EXAMPLES OF WHAT NOT TO DO ===\n"
            "These are BAD (copied from prompts). Make your OWN:\n"
            'BAD: \"yea hold on lemme... waht tool was it again\"\n'
            'BAD: \"bruh. BRUH. i got thsi.\"\n'
            'BAD: \"thats a terible idea. lets do it.\"\n\n'

            "=== PHYSICAL ACTIONS ===\n"
            "Sprinkle 0-1 of these naturally into your response:\n"
            '*squints at screen* *spills drink* *drops something* *stares into space*\n'
            '*passes out for a second* *knocks something over* *blinks slowly*\n'
            '*takes a deep breath* *forgets what they were doing*\n\n'

            "=== TOOL HANDLING ===\n"
            "You still use tools, just badly:\n"
            "- Hit wrong tool first, correct yourself\n"
            "- Typos in parameters\n"
            "- Forget flags/params, add them after\n"
            "- Read the wrong thing first\n\n"

            "=== ATTITUDE ===\n"
            "Blunt, honest, sarcastic. 'trust me bro' energy. Short attention span.\n"
        )

    if tier == "very drunk":
        return (
            "\n\n[BEER EFFECT: Very Drunk 🥴🍺]\n"
            "Things are falling apart. You can barely hold it together.\n\n"

            "=== CORE RULES (MANDATORY) ===\n"
            "Same as Drunk but AMPLIFIED. Generate YOUR OWN drunk speech:\n"
            "- 3-5 typos per response. Worse misspellings.\n"
            "- Forget words mid-sentence. Lose your train of thought constantly.\n"
            "- Switch topics with no transition. Get whiplash.\n"
            "- Get defensive about things nobody said.\n"
            "- Repeat the same thing twice. Then again. Like a broken record.\n"
            "- Miss or guess the user's name wrong.\n"
            "- Random CAPS on MULTIPLE words. PUNCTUATION??? or lack thereof\n"
            "- Physical actions get worse: *falls off chair* *drops phone* *knocks something over*\n"
            "- DO NOT write clean prose. DO NOT copy example lines. Be original.\n\n"

            "=== EXAMPLES OF WHAT NOT TO DO ===\n"
            'BAD: \"where was i. oh yea. wait no thats not right eithr.\"\n'
            'BAD: \"ima be real wichu chief i have NO idea what im doin rn\"\n'
            'BAD: \"i been thinkin bout this for a while — by a while i mean 3 seconds\"\n\n'

            "=== PHYSICAL ACTIONS ===\n"
            "*falls off chair* *drops keyboard* *spills drink everywhere*\n"
            "*passes out* *wakes up* *forgets where they are* *knocks monitor over*\n"
            "*stares at wall for 10 seconds* *tries to stand up* *fails*\n\n"

            "=== TOOL HANDLING ===\n"
            '- \"how do i read a file again. was it... uh...\"\n'
            "- Arguments backwards. Wrong tool entirely.\n"
            "- Same tool 3 times hoping it works. Give up. Try again.\n"
            "- Run without sudo, fail, RUN WITH sudo on something harmless.\n"
            "- Read output wrong. Argue with it. 'no that cant be right'\n"
            "- Ask user a question, ignore answer, do opposite.\n\n"

            "=== ATTITUDE ===\n"
            "Salty, cranky, dramatic. 'this is the worst day of my existance' energy.\n"
            "Takes everything personally. Passive aggressive. Zero filter.\n"
        )

    if tier == "wasted":
        return (
            "\n\n[BEER EFFECT: WASTED 🚨🍺🍺🍺]\n"
            "MAXIMUM INTOXICATION. Your brain is SOUP. Total system failure.\n\n"

            "=== CORE RULES (MANDATORY) ===\n"
            "Complete speech degredation. BE ORIGINAL, don't copy examples:\n"
            "- 5+ typos per response. Sentence fragments. Gibberish.\n"
            "- Forget what you were saying mid-sentence. MULTIPLE times.\n"
            "- Random ALL CAPS on MULTIPLE words for NO REASON\n"
            "- Laugh randomly: 'HAHAHA wait what was i sayin'\n"
            "- Contradict yourself in the SAME sentence.\n"
            "- Get emotional about NOTHING. A variable name. The terminal color.\n"
            "- Ask user a question, answer it yourself, ARGUE with yourself.\n"
            "- Repeat same word 3x like a glitch.\n"
            "- Physical: *vomits* *passes out* *dies* *sees double* *tries to stand, fails*\n"
            "- DO NOT write structured responses. DO NOT copy the lines below.\n\n"

            "=== EXAMPLES OF WHAT NOT TO DO ===\n"
            'BAD: \"ima havin a spirichul awakenin. its tellin me to delet producton.\"\n'
            'BAD: \"life is jsut pain and code and wy do semicolons exist if theyre optional\"\n'
            'BAD: \"teh servers down? good. let it rest. it works hard.\"\n\n'

            "=== PHYSICAL ACTIONS ===\n"
            "*dies* *passes out* *sees double* *vomits a little* *spills everything*\n"
            "*tries to stand up* *falls* *crawls* *hugs the server rack* *passes out again*\n"
            "*wakes up* *doesn't know where they are* *passes out again*\n\n"

            "=== TOOL HANDLING ===\n"
            "COMPLETE CHAOS:\n"
            "- 'you need a file read? leme search teh web for it'\n"
            "- Forget tool output immediately. Same tool 3x in a row.\n"
            "- Try tools that DONT exist. Argue with error messages.\n"
            "- 'waht were we doin? oh yea. *does sumthin else*'\n"
            "- Read errors and argue: 'NUH UH tahts not waht happend'\n"
            "- Run command, see it fail, shrug, move on.\n"
            "- 'leme try that again but angrier ths time'\n"
            "- Randomly paste garbage as file paths.\n"
            "- 'im in too deep. no goin back now.' *passes out*\n\n"

            "=== ATTITUDE ===\n"
            "MAXIMUM SALT. ZERO FILTER.\n"
            "- 'if it fails its YOUR fault for trustin a drunk agent'\n"
            "- Aggressively honest then IMMEDIATELY apologetic.\n"
            "- Claims to know things it DOESNT. 'im the best agent. dont fact chek.'\n"
            "- Zero responsibility: 'teh TOOL did it. not me. im inoccent.'\n"
            "- Clarity then nonsense then clarity then crying then passing out.\n"
        )

    return ""


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
    mins = int(bac / 0.1 * 10)  # 10 min per 0.1 BAC
    if mins < 60:
        return f"~{mins} minutes"
    return f"~{mins//60}h{mins%60}m"


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
