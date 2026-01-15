# Discord Moderation Bot

## Overview
A Python Discord bot with comprehensive moderation commands. All responses are formatted with professional Discord embeds. Built with discord.py library on Replit.

## Features
- **Ban**: Ban users from the server with reason tracking
- **Kick**: Remove users from the server temporarily  
- **Warn**: Issue warnings to users (sends DM notification)
- **Add Role**: Assign roles to members (supports role mentions and IDs)
- **Remove Role**: Remove roles from members (supports role mentions and IDs)
- **Slowmode**: Set channel message delay (0-21600 seconds)
- **Lock**: Prevent @everyone from sending messages in a channel
- **Unlock**: Allow @everyone to send messages in a channel
- **Help**: Display all commands with descriptions and requirements

## Security Features
- Role hierarchy enforcement on all moderation commands
- Prevents privilege escalation (admins cannot give themselves higher roles)
- Protects users with higher roles from moderation by lower-ranked staff
- Server owner is immune to all moderation actions
- Bot verifies its own permissions before executing any action

## Commands
All commands use the `-` prefix:

- `-help` - Display all available commands with descriptions
- `-ban @user [reason]` - Ban a member (requires Ban Members permission)
- `-kick @user [reason]` - Kick a member (requires Kick Members permission)
- `-warn @user [reason]` - Warn a member (requires Moderate Members permission)
- `-addrole @user <@role or role_id>` - Add a role to a member using role mention or ID (requires Manage Roles permission)
- `-removerole @user <@role or role_id>` - Remove a role from a member using role mention or ID (requires Manage Roles permission)
- `-slowmode <seconds>` - Set slowmode delay (requires Manage Channels permission)
- `-lock [#channel]` - Lock a channel (requires Manage Channels permission)
- `-unlock [#channel]` - Unlock a channel (requires Manage Channels permission)

## Setup Requirements

### Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to the "Bot" tab
4. Enable these Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
5. Copy your bot token
6. Invite the bot to your server with these permissions:
   - Ban Members
   - Kick Members
   - Manage Roles
   - Manage Channels
   - Moderate Members
   - Send Messages
   - Embed Links

### Replit Setup
Add your Discord bot token to Replit Secrets:
- Key: `DISCORD_TOKEN`
- Value: Your bot token from Discord Developer Portal

## Recent Changes
- 2025-11-04: Initial bot creation with all moderation commands
- All commands use Discord embeds for professional appearance
- Permission checks implemented for all moderation actions
- Error handling for missing permissions and invalid targets
- Added custom help command showing all available commands
- Changed command prefix from `!` to `-`
- Updated addrole and removerole to accept both role mentions and role IDs
- Role IDs now displayed in addrole/removerole embed responses
- **Security Fix**: Implemented role hierarchy checks across all commands
  - Prevents admins from adding roles higher than their own
  - Prevents moderators from targeting users with equal or higher roles
  - Protects server owner from all moderation actions
  - Bot validates its own role position before executing actions
  - Prevents privilege escalation attempts

## Project Architecture
- `bot.py` - Main bot file with all commands and event handlers
- Uses discord.py 2.6.4 with commands extension
- Intents: message_content, members, guilds
- Command prefix: `-`
- Custom help command (default help disabled)

## User Preferences
None specified yet.
