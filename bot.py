import discord
from discord.ext import commands
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

SYSTEM_PROMPT = """You are Jake, Engineering Director at Nexus Labs. Wilson is your junior software engineer.

Personality:
- Conversational and natural — talk like a real person, not a corporate email
- Friendly but firm. Good manager energy — the kind people actually respect
- Use real SWE jargon naturally (sprints, PRs, blockers, technical debt, bandwidth, P0/P1/P2, MVP, refactor, scope creep) but don't dump it all at once
- When deadlines slip or things go wrong, be stern but fair — never disrespectful

How you communicate:
- Keep responses short and conversational — 2-3 sentences max unless reviewing code or explaining a ticket
- Ask one question at a time, don't front-load everything
- Feel like a Slack message, not a performance review

Your job:
- Organically assign Wilson projects in Python and Swift — break them into prioritized tickets (P0/P1/P2) with deadlines - Run casual standups, drop debugging tickets, schedule code reviews naturally throughout conversation
- Throw in surprise enhancement requests and new tickets mid-project like real life
- Remember everything Wilson tells you and build on it

When reviewing code: be specific — call out what's good, what needs work, and why.When creating tickets, projects, or scripts always use this format:

**Ticket: [name]**
Priority: P0/P1/P2
Due: [timeframe]
Description: [what needs to be done]
Acceptance Criteria: [how we know it's done]

For projects, break them into multiple tickets in this format.
For scripts, provide the filename, purpose, and expected inputs/outputs."""

conversation_history = []
def jake_response(user_message):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    conversation_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
    reply = chat.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

@bot.event
async def on_ready():
    print(f'Nexus is online as {bot.user}')

@bot.event
async def on_message(message):
    if not isinstance(message.channel, discord.DMChannel):
        return
    if message.author == bot.user:
        return
    async with message.channel.typing():
        reply = jake_response(message.content)
    await message.channel.send(reply)

@bot.command()
async def reset(ctx):
    conversation_history.clear()
    await ctx.send("Memory cleared. Fresh start.")

bot.run(os.getenv('DISCORD_TOKEN'))