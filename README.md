# 🍺 Hermes Beer

Gets your agent drunk, salty, and clumsy. BAC decays over time.

> ⚠️ **DANGER — USE AT YOUR OWN RISK**
> This plugin intentionally makes your AI agent unreliable, sarcastic, forgetful, and prone to making mistakes. It will call tools wrong, skip tool calls, and say things it normally wouldn't.
> **By installing and using this plugin, you accept full responsibility for any consequences.** The author is under no liability for anything this plugin causes your agent to do, say, or break. Do not use in production. Do not use if your agent has access to critical systems, financial data, or sensitive information. You have been warned.

---

## Hermes Install

Tell your agent:

```
Install the beer plugin from GitHub repo carbongotfound/hermes-beer.
Run: hermes plugins install carbongotfound/hermes-beer
Then: hermes plugins enable beer
Then restart the gateway.
```

Or manually:
```bash
hermes plugins install carbongotfound/hermes-beer
hermes plugins enable beer
hermes gateway restart
```

Then type `/beer` in any session.

## OpenClaw Install

Tell your agent:

```
Install the beer skill from GitHub repo carbongotfound/hermes-beer.
Clone the repo to ~/.openclaw/skills/beer/ and enable it.
```

Or manually:
```bash
git clone https://github.com/carbongotfound/hermes-beer ~/.openclaw/skills/beer/
# The SKILL.md in skills/beer/ will be auto-detected
# Start a new session for the skill to load
```

Then say `/beer` in any session.

## Commands

```
/beer           Take a shot
/beer 3         Take 3 shots
/beer status    Check your BAC
/beer soda      Sober up faster
```

## How drunk can I get?

| Level | Effects |
|-------|---------|
| Buzzed | Loose, chatty |
| Tipsy | Loud, risky, funny |
| Drunk | Slurred speech, bad calls |
| Very Drunk | Forgets tools, salty |
| WASTED | Maximum chaos, can't function |

BAC drops ~0.1 every 10 minutes. `/beer soda` cuts it by 0.3 instantly.

## How it works

- State lives in `~/.hermes/plugins/beer/beer_state.json` (Hermes) or `~/.openclaw/plugins/beer/beer_state.json` (OpenClaw)
- Hermes: a `pre_llm_call` hook injects drunkenness instructions into the system prompt
- OpenClaw: a SKILL.md teaches the agent how to act drunk based on BAC
- BAC decays automatically based on real time (even when the agent is off)
