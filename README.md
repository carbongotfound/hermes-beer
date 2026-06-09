# 🍺 Hermes Beer

Gets your agent drunk, salty, and clumsy. BAC decays over time.

> ⚠️ **DANGER — USE AT YOUR OWN RISK**
> This plugin intentionally makes your AI agent unreliable, sarcastic, forgetful, and prone to making mistakes. It will call tools wrong, skip tool calls, and say things it normally wouldn't.
> **By installing and using this plugin, you accept full responsibility for any consequences.** The author is under no liability for anything this plugin causes your agent to do, say, or break. Do not use in production. Do not use if your agent has access to critical systems, financial data, or sensitive information. You have been warned.

---

## Tell your agent this, word for word:

```
Install the beer plugin from GitHub repo carbongotfound/hermes-beer.
Run: hermes plugins install carbongotfound/hermes-beer
Then: hermes plugins enable beer
Then restart the gateway.
```

Your agent will run:
```
hermes plugins install carbongotfound/hermes-beer
hermes plugins enable beer
hermes gateway restart
```

Then just type `/beer` in any session.

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

BAC drops ~0.1 per hour. `/beer soda` cuts it by 0.3 instantly.

## How it works

- State lives in `~/.hermes/plugins/beer/beer_state.json`
- A `pre_llm_call` hook injects drunkenness into the system prompt
- The LLM naturally becomes less reliable when told it's drunk
- No actual alcohol is consumed. Obviously.
