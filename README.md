# LanguageFilterBot
A language filter for discord, restricting channels to a specific language

## 1. General Commands

### `/reload`
**Description:** Restarts the bot by re-executing the main script.

**Usage:**
- **Command:** `/reload`
- **Permission Required:** Owner only

---

### `/language_filter`
**Description:** Adds or removes a language filter in a specified channel. The bot can restrict messages in a channel to only allow English or Japanese.

**Usage:**
- **Command:** `/language_filter`
- **Options:**
  - `action`: Choose between "Add filter" or "Remove filter".
  - `filter_type`: Choose between "Only Allow English" or "Only Allow Japanese".
  - `channel`: Specify the target channel.
  
**Example:**
- To allow only English in a channel:  
  `/language_filter action:add filter_type:Only Allow English channel:#example-channel`

**Permission Required:** Owner only

---

### `/ping`
**Description:** Returns the bot's latency (ping).

**Usage:**
- **Command:** `/ping`
- **Response:** The bot will reply with its current latency in milliseconds.

---

## 2. Message Handling Commands

These commands are triggered automatically by the bot to filter messages based on language settings.

### **Language Filter**
- The bot automatically deletes messages that violate language filters applied to specific channels (e.g., too much English in a Japanese-only channel or vice versa).

### **Foreign Language Filter**
- If a message contains more than 20% foreign language content, the bot may warn the user and delete the message, depending on the configured filters.

---

## 3. Reminder Commands

### `/reminder add`
**Description:** Adds a new reminder to the bot.

**Usage:**
- **Command:** `/reminder add time_from_now:<duration> text:<reminder_message> [interval:<repetition_duration>]`
- **Example:** `/reminder add time_from_now:1h text:Check the oven interval:30m`
- The `interval` option is optional and allows for recurring reminders.
  
**Time Format:** `1m`, `1h`, `1d` for minutes, hours, and days respectively.

---

### `/reminder edit`
**Description:** Edit an existing reminder by its ID, changing its repeat status or interval.

**Usage:**
- **Command:** `/reminder edit reminder_id:<id> [repeat:<True/False>] [interval:<duration>]`
- **Example:** `/reminder edit reminder_id:abc123 repeat:True interval:2h`

---

### `/reminder remove`
**Description:** Removes an existing reminder by its ID.

**Usage:**
- **Command:** `/reminder remove reminder_id:<id>`

---

### `/reminder list`
**Description:** Lists all active reminders for the user.

**Usage:**
- **Command:** `/reminder list`

---

## Background Reminder Loop
The bot checks for reminders every 60 seconds and sends reminders to users in the designated channels when the time arrives.

---

## Configuration
- The bot uses a `config.json` file to store active language filters and other settings.
- The bot also logs deleted messages and their reasons in a `log.json` file.

