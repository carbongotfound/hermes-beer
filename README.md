# 🍺 Hermes Beer

Gets your agent drunk, salty, and clumsy. BAC decays over time.

## Tell your agent this, word for word:

```
Install the beer plugin from carbongotfound/hermes-beer. Then enable it and restart.
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

Inside the plugin:
- State lives in `~/.hermes/plugins/beer/beer_state.json`
- A `pre_llm_call` hook injects drunkenness into the system prompt
- The LLM naturally becomes less reliable when told it's drunk
