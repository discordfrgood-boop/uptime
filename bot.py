
import discord
import asyncio
from discord.ui import View
import time
from discord.ext import commands
import os
import json

astral_locked_data = {}
LOCK_DATA_FILE = "astral_locked_data.json"

warns_data = {}
WARNS_DATA_FILE = "warns_data.json"

current_prefix = "-"
PREFIX_CONFIG_FILE = "bot_prefix.json"

def save_prefix():
    """Save current prefix to JSON file"""
    try:
        with open(PREFIX_CONFIG_FILE, 'w') as f:
            json.dump({"prefix": current_prefix}, f)
    except Exception as e:
        print(f"[ERROR] Failed to save prefix: {e}")

def load_prefix():
    """Load prefix from JSON file"""
    global current_prefix
    try:
        if not os.path.exists(PREFIX_CONFIG_FILE):
            return
        with open(PREFIX_CONFIG_FILE, 'r') as f:
            data = json.load(f)
            current_prefix = data.get("prefix", "-")
        print(f"[INFO] Loaded prefix: {current_prefix}")
    except Exception as e:
        print(f"[ERROR] Failed to load prefix: {e}")

def save_lock_data():
    """Save astral_locked_data to JSON file (convert role IDs to integers for storage)"""
    try:
        data_to_save = {}
        for user_id, roles in astral_locked_data.items():
            data_to_save[str(user_id)] = [r.id for r in roles]
        with open(LOCK_DATA_FILE, 'w') as f:
            json.dump(data_to_save, f)
    except Exception as e:
        print(f"[ERROR] Failed to save astral lock data: {e}")

def load_lock_data(guild):
    """Load astral_locked_data from JSON file (convert role IDs back to role objects)"""
    global astral_locked_data
    try:
        if not os.path.exists(LOCK_DATA_FILE):
            return
        with open(LOCK_DATA_FILE, 'r') as f:
            data = json.load(f)
        
        astral_locked_data = {}
        for user_id_str, role_ids in data.items():
            user_id = int(user_id_str)
            roles = []
            for role_id in role_ids:
                role = guild.get_role(role_id)
                if role:
                    roles.append(role)
            if roles:
                astral_locked_data[user_id] = roles
        print(f"[INFO] Loaded {len(astral_locked_data)} astral lock records")
    except Exception as e:
        print(f"[ERROR] Failed to load astral lock data: {e}")

def save_warns_data():
    """Save warns_data to JSON file"""
    try:
        with open(WARNS_DATA_FILE, 'w') as f:
            json.dump(warns_data, f)
    except Exception as e:
        print(f"[ERROR] Failed to save warns data: {e}")

def load_warns_data():
    """Load warns_data from JSON file"""
    global warns_data
    try:
        if not os.path.exists(WARNS_DATA_FILE):
            return
        with open(WARNS_DATA_FILE, 'r') as f:
            warns_data = json.load(f)
        print(f"[INFO] Loaded warns data for {len(warns_data)} users")
    except Exception as e:
        print(f"[ERROR] Failed to load warns data: {e}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Load prefix before creating bot
load_prefix()

bot = commands.Bot(command_prefix=lambda bot, msg: current_prefix, intents=intents,)
bot.remove_command("help")
def can_execute_action(ctx, target: discord.Member) -> tuple[bool, str]:
    if target.id == ctx.guild.owner_id:
        return False, "You cannot perform this action on the server owner."
    
    if ctx.author.id != ctx.guild.owner_id:
        if target.top_role >= ctx.author.top_role:
            return False, "You cannot perform this action on someone with an equal or higher role than you."
    
    if target.top_role >= ctx.guild.me.top_role:
        return False, "I cannot perform this action on someone with an equal or higher role than me."
    
    return True, ""

def can_manage_role(ctx, role: discord.Role, target: discord.Member = None) -> tuple[bool, str]:
    if ctx.author.id != ctx.guild.owner_id:
        if role >= ctx.author.top_role:
            return False, "You cannot manage a role equal to or higher than your highest role."
    
    if role >= ctx.guild.me.top_role:
        return False, "I cannot manage a role equal to or higher than my highest role."
    
    if target and target.id == ctx.guild.owner_id:
        return False, "You cannot modify roles for the server owner."
    
    if target and ctx.author.id != ctx.guild.owner_id:
        if target.top_role >= ctx.author.top_role:
            return False, "You cannot manage roles for someone with an equal or higher role than you."
    
    return True, ""

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    # Load astral lock data from file on startup
    for guild in bot.guilds:
        load_lock_data(guild)
    # Load warns data from file on startup
    load_warns_data()


class ShrineButton(discord.ui.Button):
    def __init__(self, bot, shrine_message, user_message):
        super().__init__(
            label="Enter Shrine",
            style=discord.ButtonStyle.primary,
            emoji="✨"
        )
        self.bot = bot
        self.shrine_message = shrine_message
        self.user_message = user_message

    async def callback(self, interaction: discord.Interaction):
        # Delete the old shrine interface + user ping message
        try:
            await self.shrine_message.delete()
        except:
            pass

        try:
            await self.user_message.delete()
        except:
            pass

        # Create the new shrine embed
        embed = discord.Embed(
            title="✨ Enter the Astral Shrine",
            description="Welcome, traveler.\n\nUse `-help` to explore my powers.",
            color=discord.Color.purple()
        )

        shrine_reply = await interaction.channel.send(embed=embed)

        # Fake ephemeral → Delete after 8 seconds
        await asyncio.sleep(8)
        try:
            await shrine_reply.delete()
        except:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:return

    # When bot is pinged
    if bot.user in message.mentions:
        embed = discord.Embed(
            title="🌌 Astral Shrine",
            description="You called upon the cosmic guardian?",
            color=discord.Color.purple()
        )

        # Send the shrine interface
        shrine_interface_message = await message.channel.send(embed=embed)

        # Create button view
        view = View()

        # Add the ShrineButton with references to:
        # bot, shrine interface message, and user's message
        view.add_item(ShrineButton(bot, shrine_interface_message, message))

        # Edit shrine message to include the button
        await shrine_interface_message.edit(embed=embed, view=view)

    await bot.process_commands(message)



@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🌌 You Have Entered the Astral Shrine",
        description="Welcome, traveler. These are the sacred commands available to you:",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="🔨 -ban @user [reason]",
        value="Ban a member from the server.\n*Requires: Ban Members permission*",
        inline=False
    )
    
    embed.add_field(
        name="👢 -kick @user [reason]",
        value="Kick a member from the server.\n*Requires: Kick Members permission*",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ -warn @user [reason]",
        value="Issue a warning to a member (sends DM).\n*Requires: Moderate Members permission*",
        inline=False
    )
    
    embed.add_field(
        name="✅ -addrole @user <@role or role_id>",
        value="Add a role to a member using role mention or ID.\n*Requires: Manage Roles permission*",
        inline=False
    )
    
    embed.add_field(
        name="➖ -removerole @user <@role or role_id>",
        value="Remove a role from a member using role mention or ID.\n*Requires: Manage Roles permission*",
        inline=False
    )
    
    embed.add_field(
        name="🐢 -slowmode <seconds>",
        value="Set channel slowmode delay (0-21600 seconds).\n*Requires: Manage Channels permission*",
        inline=False
    )
    
    embed.add_field(
        name="🔒 -lock [#channel]",
        value="Lock a channel to prevent messages.\n*Requires: Manage Channels permission*",
        inline=False)

    embed.add_field(
    name="-🔓 Unlock",
    value="Unlock a channel to allow everyone to chat again.\n**Requires:** Manage Channels permission.",
    inline=False
    )

    embed.add_field(
    name="💤 AFK",
    value="Set your AFK status using `-afk [reason]`. Example: `-afk eating`",
    inline=False
    )

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    can_execute, error_msg = can_execute_action(ctx, member)
    if not can_execute:
        embed = discord.Embed(
            title="❌ Hierarchy Error",
            description=error_msg,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{member.mention} has been banned from the server.",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Banned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to ban this user.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Owner allowed to give access
ACCESS_GRANTER_ID = 1376932084118982737

# used_trial already exists from the core system
# used_trial = set()

@bot.command()
async def gaccess(ctx, member: discord.Member = None):
    # Only the owner can run this command
    if ctx.author.id != ACCESS_GRANTER_ID:
        return await ctx.send("❌ You don't have permission to use this command.")

    # No user mentioned
    if member is None:
        return await ctx.send("❌ Please mention a user. Example: `-gaccess @user`")

    # If user hasn't used the trial at all
    if member.id not in used_trial:
        return await ctx.send(f"ℹ️ {member.mention} **still has unused trial access.**")

    # Reset their trial
    used_trial.remove(member.id)

    await ctx.send(
        f"✅ **Access Granted!**\n"
        f"{member.mention} can now use the **-core** command again."
    )

@bot.command()
async def raccess(ctx, member: discord.Member = None):
    # Owner-only command
    if ctx.author.id != 1376932084118982737:
        return await ctx.send("❌ You don't have permission to use this command.")

    if member is None:
        return await ctx.send("❌ Please mention a user. Example: `-raccess @user`")

    # If user was given access again by accident (they’re not blocked)
    if member.id not in used_trial:
        return await ctx.send(
            f"ℹ️ {member.mention} **currently has access to -core.**\n"
            "If you want to block them from using it, I can do that."
        )

    # Fully remove access
    used_trial.remove(member.id)

    # Save changes (if JSON system is enabled)
    try:
        save_trials()
    except:
        pass

    await ctx.send(
        f"🚫 **NebulaCore Access Removed!**\n"
        f"{member.mention} can no longer use the **-core** command."
    )

@bot.command(name="cocoapanel")
async def cocoapanel(ctx):
    # only allowed user
    ADMIN_ID = 1376932084118982737
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("❌ You cannot use this command.")

    # embed
    embed = discord.Embed(
        title="🍫 Cocoa Admin Panel",
        description="Click a button to perform an action. All responses are ephemeral to keep chat clean.",
        color=discord.Color.orange()
    )

    # ---------- helper: build options (limit 25) ----------
    def member_options(guild):
        members = [m for m in guild.members if not m.bot]
        # sort for stable order
        members.sort(key=lambda m: m.display_name.lower())
        op = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in members[:25]]
        if not op:
            op = [discord.SelectOption(label="No members available", value="0")]
        return op

    def role_options(guild):
        roles = [r for r in guild.roles if not r.managed and r != guild.default_role]
        roles.sort(key=lambda r: r.name.lower())
        op = [discord.SelectOption(label=r.name, value=str(r.id)) for r in roles[:25]]
        if not op:
            op = [discord.SelectOption(label="No roles available", value="0")]
        return op

    # ---------- ACTION HOLDER ----------
    class Action:
        def __init__(self, name):
            self.name = name  # 'ban','kick','warn','addrole','removerole'

    # ---------- SELECTS ----------
    class MemberSelect(discord.ui.Select):
        def __init__(self, action: Action):
            super().__init__(placeholder="Select a member...", min_values=1, max_values=1,
                             options=member_options(ctx.guild))
            self.action = action

        async def callback(self, interaction: discord.Interaction):
            # basic permission check for who clicked
            if interaction.user.id != ADMIN_ID:
                return await interaction.response.send_message("❌ Not allowed.", ephemeral=True)

            if self.values[0] == "0":
                return await interaction.response.send_message("❌ No valid members to select.", ephemeral=True)

            member = interaction.guild.get_member(int(self.values[0]))
            if member is None:
                return await interaction.response.send_message("❌ Member not found.", ephemeral=True)

            # BAN
            if self.action.name == "ban":
                if not interaction.guild.me.guild_permissions.ban_members:
                    return await interaction.response.send_message("❌ I don't have permission to ban.", ephemeral=True)
                try:
                    await member.ban(reason=f"Action by {interaction.user}")
                    await interaction.response.send_message(f"🔨 Banned **{member}**", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"❌ Failed to ban: {e}", ephemeral=True)

            # KICK
            elif self.action.name == "kick":
                if not interaction.guild.me.guild_permissions.kick_members:
                    return await interaction.response.send_message("❌ I don't have permission to kick.", ephemeral=True)
                try:
                    await member.kick(reason=f"Action by {interaction.user}")
                    await interaction.response.send_message(f"🦵 Kicked **{member}**", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"❌ Failed to kick: {e}", ephemeral=True)

            # WARN (send DM and ephemeral notification)
            elif self.action.name == "warn":
                dm_text = f"You have been warned in **{interaction.guild.name}** by {interaction.user}."
                sent = True
                try:
                    await member.send(dm_text)
                except Exception:
                    sent = False
                await interaction.response.send_message(
                    f"⚠️ Warned **{member}**. DM {'sent' if sent else 'failed (user DMs closed)'}",
                    ephemeral=True
                )

            # ADDROLE: open role select (for this selected member)
            elif self.action.name == "addrole":
                view = discord.ui.View(timeout=60)
                view.add_item(RoleSelect(member, "add"))
                await interaction.response.send_message(f"Select a role to add to **{member}**", view=view, ephemeral=True)

            # REMOVEROLE: open role select (for this selected member)
            elif self.action.name == "removerole":
                view = discord.ui.View(timeout=60)
                view.add_item(RoleSelect(member, "remove"))
                await interaction.response.send_message(f"Select a role to remove from **{member}**", view=view, ephemeral=True)

    class RoleSelect(discord.ui.Select):
        def __init__(self, member: discord.Member, mode: str):
            # mode = "add" or "remove"
            self.member = member
            self.mode = mode
            super().__init__(placeholder="Select a role...", min_values=1, max_values=1, options=role_options(ctx.guild))

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                return await interaction.response.send_message("❌ Not allowed.", ephemeral=True)

            if self.values[0] == "0":
                return await interaction.response.send_message("❌ No valid roles to select.", ephemeral=True)

            role = interaction.guild.get_role(int(self.values[0]))
            if role is None:
                return await interaction.response.send_message("❌ Role not found.", ephemeral=True)

            # add role
            if self.mode == "add":
                if not interaction.guild.me.guild_permissions.manage_roles:
                    return await interaction.response.send_message("❌ I don't have permission to manage roles.", ephemeral=True)
                try:
                    await self.member.add_roles(role)
                    await interaction.response.send_message(f"➕ Added **{role.name}** to **{self.member}**", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"❌ Failed to add role: {e}", ephemeral=True)

            # remove role
            else:
                if not interaction.guild.me.guild_permissions.manage_roles:
                    return await interaction.response.send_message("❌ I don't have permission to manage roles.", ephemeral=True)
                try:
                    await self.member.remove_roles(role)
                    await interaction.response.send_message(f"➖ Removed **{role.name}** from **{self.member}**", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"❌ Failed to remove role: {e}", ephemeral=True)

    # ---------- BUTTONS ----------
    class SimpleButton(discord.ui.Button):
        def __init__(self, label, style, emoji, action_name):
            super().__init__(label=label, style=style, emoji=emoji)
            self.action = Action(action_name)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != ADMIN_ID:
                return await interaction.response.send_message("❌ Not allowed.", ephemeral=True)
            
            # For actions that need member select -> show member select view
            if self.action.name in ("ban", "kick", "warn", "addrole", "removerole"):
                view = discord.ui.View(timeout=60)
                view.add_item(MemberSelect(self.action))
                await interaction.response.send_message("Select a member:", view=view, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Unknown action.", ephemeral=True)

    v = discord.ui.View(timeout=None)
    v.add_item(SimpleButton("Ban", discord.ButtonStyle.danger, "🔨", "ban"))
    v.add_item(SimpleButton("Kick", discord.ButtonStyle.danger, "🦵", "kick"))
    v.add_item(SimpleButton("Warn", discord.ButtonStyle.primary, "⚠️", "warn"))
    v.add_item(SimpleButton("Add Role", discord.ButtonStyle.success, "➕", "addrole"))
    v.add_item(SimpleButton("Remove Role", discord.ButtonStyle.secondary, "➖", "removerole"))

    await ctx.send(embed=embed, view=v)

@bot.command()
async def add(ctx):
    embed = discord.Embed(
        title="1 inv= 3sx | Grow A Garden | Steal A Brainrot | Plants vs Brainrots server",
        color=0x2b2d31
    )

    # Banner image (animated emoji as GIF)
    embed.set_image(
        url="https://cdn.discordapp.com/emojis/1411301081920704635.gif"
    )

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="Join Server",
            url="https://discord.gg/7efyKb5W",
            style=discord.ButtonStyle.link
        )
    )

    await ctx.send(embed=embed, view=view)





@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    can_execute, error_msg = can_execute_action(ctx, member)
    if not can_execute:
        embed = discord.Embed(
            title="❌ Hierarchy Error",
            description=error_msg,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"{member.mention} has been kicked from the server.",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to kick this user.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
async def lockserver(ctx):
    ALLOWED_USER_ID = 1376932084118982737

    # Only this user can use the command
    if ctx.author.id != ALLOWED_USER_ID:
        return

    goodbye_message = (
        "**This server is discontinued by the owner**\n"
        "**My calm goodbye is with this server.**"
    )

    guild = ctx.guild
    allowed_user = guild.get_member(ALLOWED_USER_ID)

    if not allowed_user:
        return

    for channel in guild.text_channels:
        try:
            # Lock everyone
            await channel.set_permissions(
                guild.default_role,
                send_messages=False
            )

            # Allow ONLY this user
            await channel.set_permissions(
                allowed_user,
                send_messages=True
            )

            # Send message in every channel
            await channel.send(goodbye_message)

        except Exception as e:
            print(f"Failed in {channel.name}: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_input: str):
    try:
        role = None
        
        if role_input.isdigit():
            role = ctx.guild.get_role(int(role_input))
        else:
            role = await commands.RoleConverter().convert(ctx, role_input)
        
        if not role:
            embed = discord.Embed(
                title="❌ Role Not Found",
                description="Could not find the specified role. Please use a role mention or role ID.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        can_manage, error_msg = can_manage_role(ctx, role, member)
        if not can_manage:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description=error_msg,
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        await member.add_roles(role)
        
        embed = discord.Embed(
            title="✅ Role Added",
            description=f"Role has been added to {member.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Role", value=f"{role.mention}", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to manage roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
async def astrallock(ctx, member: discord.Member = None):
    # Only allow YOUR ID
    if ctx.author.id != 1376932084118982737:
        return await ctx.send("❌ You are not permitted to use Astral Lock.")

    if member is None:
        return await ctx.send("Please mention a user to Astrally Lock.")

    if member == ctx.author:
        return await ctx.send("You cannot Astrally Lock yourself.")

    # Save OLD ROLES (except @everyone)
    old_roles = [r for r in member.roles if r != ctx.guild.default_role]
    astral_locked_data[member.id] = old_roles
    save_lock_data()

    # Create or get Astral Locked role
    locked_role = discord.utils.get(ctx.guild.roles, name="Astral Locked")
    if locked_role is None:
        locked_role = await ctx.guild.create_role(name="Astral Locked")
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(locked_role, send_messages=False, speak=False)
            except:
                pass

    # Remove all roles
    for r in old_roles:
        try:
            await member.remove_roles(r)
        except:
            pass

    # Add the Astral Locked role
    await member.add_roles(locked_role)

    # DM the user
    try:
        dm_embed = discord.Embed(
            title="🌌 **Astral Lock Engaged**",
            description="Your cosmic energy has been sealed.\nYou have been **Astrally Locked**.",
            color=discord.Color.purple()
        )
        await member.send(embed=dm_embed)
    except:
        pass

    # Server confirmation
    embed = discord.Embed(
        title="🔮 Astral Lock Activated",
        description=f"{member.mention} is now **Astrally Locked**. Their cosmic flow is sealed.",
        color=discord.Color.dark_purple()
    )
    await ctx.send(embed=embed)


@bot.command()
async def rastrallock(ctx, member: discord.Member = None):
    # Only YOU can use this
    if ctx.author.id != 1376932084118982737:
        return await ctx.send("❌ You are not permitted to use Reverse Astral Lock.")

    if member is None:
        return await ctx.send("Please mention a user to release from Astral Lock.")

    # Check if user was astrally locked
    if member.id not in astral_locked_data:
        return await ctx.send("❌ This user is not Astrally Locked or has no stored data.")

    # Get stored old roles
    old_roles = astral_locked_data[member.id]

    # Remove Astral Locked role
    locked_role = discord.utils.get(ctx.guild.roles, name="Astral Locked")
    if locked_role in member.roles:
        try:
            await member.remove_roles(locked_role)
        except:
            pass

    # Restore old roles
    for r in old_roles:
        try:
            await member.add_roles(r)
        except:
            pass

    # Delete record so it cannot be restored again
    del astral_locked_data[member.id]
    save_lock_data()

    # DM the user
    try:
        dm_embed = discord.Embed(
            title="✨ Astral Seal Broken",
            description="Your cosmic energy has been restored.\nYou are **no longer Astrally Locked**.",
            color=discord.Color.purple()
        )
        await member.send(embed=dm_embed)
    except:
        pass

    # Server confirmation
    embed = discord.Embed(
        title="🌠 Astral Lock Released",
        description=f"{member.mention} has been **freed**. Their cosmic flow returns.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)
        

@bot.command()
async def portal(ctx):
    # First stage: portal forming
    embed1 = discord.Embed(
        title="🌌 Opening a Cosmic Portal...",
        description="The astral energies start to gather...",
        color=discord.Color.dark_purple()
    )
    msg = await ctx.send(embed=embed1)

    # Wait a moment
    await asyncio.sleep(1.5)

    # Second stage: portal glowing
    embed2 = discord.Embed(
        title="✨ The Portal Glows...",
        description="Nebula particles swirl around the gateway.",
        color=discord.Color.purple()
    )
    embed2.set_image(url="https://i.postimg.cc/QxDMZKhV/purple-vortex.gif")
    await msg.edit(embed=embed2)

    # Wait a moment
    await asyncio.sleep(1.5)

    # Final stage: portal opens
    embed3 = discord.Embed(
        title="🌀 Portal Activated",
        description="**Step through, traveler...**\nA new realm awaits.",
        color=discord.Color.magenta()
    )
    embed3.set_image(url="https://i.postimg.cc/bYJx7bHn/space-portal.gif")
    await msg.edit(embed=embed3)

    # Delete after 8 seconds (fake ephemeral)
    await asyncio.sleep(8)
    try:
        await msg.delete()
    except:
        pass


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_input: str):
    try:
        role = None
        
        if role_input.isdigit():
            role = ctx.guild.get_role(int(role_input))
        else:
            role = await commands.RoleConverter().convert(ctx, role_input)
        
        if not role:
            embed = discord.Embed(
                title="❌ Role Not Found",
                description="Could not find the specified role. Please use a role mention or role ID.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        can_manage, error_msg = can_manage_role(ctx, role, member)
        if not can_manage:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description=error_msg,
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        await member.remove_roles(role)
        
        embed = discord.Embed(
            title="➖ Role Removed",
            description=f"Role has been removed from {member.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Role", value=f"{role.mention} ({role.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to manage roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    can_execute, error_msg = can_execute_action(ctx, member)
    if not can_execute:
        embed = discord.Embed(
            title="❌ Hierarchy Error",
            description=error_msg,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Increment warn count for this user
        user_id_str = str(member.id)
        if user_id_str not in warns_data:
            warns_data[user_id_str] = 0
        warns_data[user_id_str] += 1
        warn_count = warns_data[user_id_str]
        
        # Ordinal suffix for warn count
        if warn_count == 1:
            ordinal = "1st"
        elif warn_count == 2:
            ordinal = "2nd"
        elif warn_count == 3:
            ordinal = "3rd"
        else:
            ordinal = f"{warn_count}th"
        
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"{member.mention} has been warned. This is their **{ordinal}** warning.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Warning Count", value=f"**{warn_count}** total warns", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"⚠️ Warning ({ordinal})",
                description=f"You have been warned in **{ctx.guild.name}**\n\nThis is your **{ordinal}** warning.",
                color=discord.Color.yellow()
            )
            dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
            dm_embed.add_field(name="Total Warns", value=str(warn_count), inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Save warns data
        save_warns_data()
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        

@bot.command(name="setprefix")
async def setprefix(ctx, new_prefix: str):
    """Change the bot's command prefix. Only the owner can use this."""
    # Only owner can use this
    if ctx.author.id != 1376932084118982737:
        embed = discord.Embed(
            title="❌ Not Allowed",
            description="Only the bot owner can change the prefix.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)
    
    if not new_prefix or len(new_prefix) > 5:
        embed = discord.Embed(
            title="❌ Invalid Prefix",
            description="Prefix must be 1-5 characters long.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)
    
    global current_prefix
    old_prefix = current_prefix
    current_prefix = new_prefix
    save_prefix()
    
    embed = discord.Embed(
        title="✅ Prefix Updated",
        description=f"Bot prefix changed from `{old_prefix}` to `{new_prefix}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Old Prefix", value=f"`{old_prefix}`", inline=True)
    embed.add_field(name="New Prefix", value=f"`{new_prefix}`", inline=True)
    embed.set_footer(text=f"Changed by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


TRIAL_ROLE_NAME = "NebulaCore"
used_trial = set()

class CoreButtons(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=60)
        self.member = member

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, emoji="☑️")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.member:
            return await interaction.response.send_message("❌ This is not for you.", ephemeral=True)

        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=TRIAL_ROLE_NAME)

        if role is None:
            return await interaction.response.send_message(
                f"❌ Role `{TRIAL_ROLE_NAME}` not found.", ephemeral=True
            )

        await self.member.add_roles(role)
        used_trial.add(self.member.id)

        await interaction.response.send_message(
            "✨ **NebulaCore has been activated!**\nYou now have access for **30 seconds.**",
            ephemeral=True
        )

        await asyncio.sleep(30)

        if role in self.member.roles:
            await self.member.remove_roles(role)

        await interaction.followup.send(
            "⏳ **Your 30-second trial has ended!**\nAsk the owner for more access.",
            ephemeral=True
        )

        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.member:
            return await interaction.response.send_message("❌ This is not for you.", ephemeral=True)

        await interaction.response.send_message("NebulaCore activation cancelled.", ephemeral=True)
        self.stop()


@bot.command()
async def core(ctx):
    member = ctx.author

    if member.id in used_trial:
        return await ctx.send(
            "❌ **Your trial has already ended. Contact the owner for more access.**"
        )

    embed = discord.Embed(
        title="🌌 Nebula Core Activation",
        description=(
            "Do you want to activate **NebulaCore**?\n"
            "You will receive exclusive benefits for **30 seconds**.\n\n"
            "Click **Yes** or **No** below."
        ),
        color=discord.Color.blue()
    )

    view = CoreButtons(member)
    await ctx.send(embed=embed, view=view)
    

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx,channel:discord.TextChannel = None):
    try:
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} has been locked.",
            color=discord.Color.red()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Status", value="Members cannot send messages", inline=False)
        embed.set_footer(text=f"Locked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to manage this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    try:
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} has been unlocked.",
            color=discord.Color.green()
        )
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Status", value="Members can send messages", inline=False)
        embed.set_footer(text=f"Unlocked by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to manage this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


start_time = time.time()  # record when bot started

@bot.command()
async def stats(ctx):
    now = time.time()
    uptime_seconds = int(now - start_time)

    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    # You can change this number depending on your host
    HOSTING_LIMIT_HOURS = 720  # 30 days

    hours_left = HOSTING_LIMIT_HOURS - hours
    if hours_left < 0:
        hours_left = 0

    embed = discord.Embed(
        title="✨ Nebula - Bot Stats",
        description="Here are the current performance stats for the bot:",
        color=discord.Color.red()
    )

    embed.add_field(name="🤖 Bot Name", value=bot.user.name, inline=False)
    embed.add_field(name="🆔 Bot ID", value=bot.user.id, inline=False)

    embed.add_field(
        name="⏳ Uptime",
        value=f"**{hours}h {minutes}m {seconds}s**",
        inline=False
    )

    embed.add_field(
        name="🔥 Hosting Time Left",
        value=f"**{hours_left} hours remaining**",
        inline=False
    )

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    embed.set_footer(text="Nebula Hosting Panel")

    await ctx.send(embed=embed)
    
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, *, value: str = None):
    """
    Usage:
      -slowmode 10    -> set 10s slowmode
      -slowmode 2m    -> set 2 minutes slowmode
      -slowmode off   -> remove slowmode
      -slowmode 0     -> remove slowmode
    """
    try:
        print(f"[DEBUG] slowmode command used by {ctx.author} with value: {value}")  # for debugging

        if value is None:
            embed = discord.Embed(
                title="⚙️ Slowmode Command",
                description="Usage: `-slowmode <seconds|10s|2m|1h|off>`",
                color=discord.Color.yellow()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=embed)

        v = value.strip().lower()

        # Check for 'off', 'disable', or '0'
        if v in ("off", "disable") or v == "0":
            await ctx.channel.edit(slowmode_delay=0)
            embed = discord.Embed(
                title="✅ Slowmode Disabled",
                description=f"Slowmode has been **turned off** by {ctx.author.mention}.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=embed)

        # Parse time suffix (s, m, h)
        multiplier = 1
        if v.endswith("s"):
            multiplier = 1
            v_num = v[:-1]
        elif v.endswith("m"):
            multiplier = 60
            v_num = v[:-1]
        elif v.endswith("h"):
            multiplier = 3600
            v_num = v[:-1]
        else:
            v_num = v

        try:
            seconds = int(v_num) * multiplier
        except ValueError:
            embed = discord.Embed(
                title="⚠️ Invalid Time Format",
                description="Use a number or include `s`, `m`, or `h`.\nExample: `-slowmode 10s`, `-slowmode 2m`, or `-slowmode off`.",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=embed)

        if seconds < 0 or seconds > 21600:
            embed = discord.Embed(
                title="⚠️ Invalid Time Range",
                description="Time must be between **0** and **21600 seconds (6 hours)**.",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
            return await ctx.send(embed=embed)

        await ctx.channel.edit(slowmode_delay=seconds)
        embed = discord.Embed(
            title="🐢 Slowmode Updated",
            description=f"Set to **{seconds} seconds** by {ctx.author.mention}.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar)
        await ctx.send(embed=embed)

    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="I don’t have permission to **Manage Channels**.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="⚠️ Error Occurred",
            description=f"An unexpected error occurred:\n```{e}```",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        print(f"[ERROR] slowmode command error: {e}")


@bot.command(name="r001")
async def r001(ctx, member: discord.Member = None):
    # Only user 1376932084118982737 can use this
    if ctx.author.id != 1376932084118982737:
        return await ctx.send("❌ You are not permitted to use this command.")

    if member is None:
        return await ctx.send("❌ Please mention a user to remove from Astral Lock. Example: `-r001 @user`")

    # Check if user was astrally locked
    if member.id not in astral_locked_data:
        embed = discord.Embed(
            title="❌ Not Locked",
            description=f"{member.mention} is not Astrally Locked or has no stored data.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Get stored old roles
    old_roles = astral_locked_data[member.id]

    # Remove Astral Locked role
    locked_role = discord.utils.get(ctx.guild.roles, name="Astral Locked")
    if locked_role and locked_role in member.roles:
        try:
            await member.remove_roles(locked_role)
        except Exception as e:
            print(f"[ERROR] Failed to remove Astral Locked role: {e}")

    # Restore old roles
    for r in old_roles:
        try:
            await member.add_roles(r)
        except Exception as e:
            print(f"[ERROR] Failed to restore role {r.name}: {e}")

    # Delete record
    del astral_locked_data[member.id]
    save_lock_data()

    # DM the user
    try:
        dm_embed = discord.Embed(
            title="✨ Astral Seal Broken",
            description="Your cosmic energy has been restored.\nYou are **no longer Astrally Locked**.",
            color=discord.Color.green()
        )
        await member.send(embed=dm_embed)
    except:
        pass

    # Server confirmation
    embed = discord.Embed(
        title="🌠 Astral Lock Released",
        description=f"{member.mention} has been **freed**. Their cosmic flow returns.",
        color=discord.Color.green()
    )
    embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
    embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

 
@ban.error
@kick.error
@addrole.error
@removerole.error
@warn.error
@slowmode.error
@lock.error
@unlock.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Member Not Found",
            description="Member not found. Please mention a valid member.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.RoleNotFound):
        embed = discord.Embed(
            title="❌ Role Not Found",
            description="Role not found. Please mention a valid role.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: {error.param.name}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)



TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
    print("❌ ERROR: DISCORD_TOKEN not found in environment variables!")
    print("Please add your Discord bot token to the Secrets panel.")
