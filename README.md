# Google Calendar MCP Server 📅🤖

An MCP (Model Context Protocol) server that connects Claude Desktop to Google Calendar, enabling natural language calendar management through conversation.

## Features

- 📅 **Smart Scheduling** - Schedule meetings using natural language
- 🔗 **Auto Meet Links** - Automatically generate Google Meet conference links
- 👥 **Attendee Management** - Send invites to multiple participants
- ⏰ **Availability Checking** - Check calendar availability for any date range
- 🎯 **Free Slot Finding** - Automatically find available time slots
- ✏️ **Event Management** - Reschedule, cancel, and update calendar events
- 🔔 **Smart Notifications** - Optional attendee notifications for changes

## Demo

**You:** "Find a free slot tomorrow and schedule a 2-hour team meeting with a Meet link"

**Claude:** ✅ Checks availability → Finds optimal slot → Schedules meeting → Generates Meet link → Done!

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Claude Desktop](https://claude.ai/download)
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials from Google Cloud Console

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/google-calendar-mcp.git
cd google-calendar-mcp
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure OAuth consent screen:
   - Choose "External" user type
   - Fill required fields (app name, support email)
   - Add scope: `https://www.googleapis.com/auth/calendar`
   - Add your email as test user
4. Select "Desktop app" as application type
5. Download credentials and save as `credentials.json`

### 4. Set Up Credentials Folder

```bash
# Windows
mkdir %USERPROFILE%\.google-calendar-mcp
copy path\to\downloaded\credentials.json %USERPROFILE%\.google-calendar-mcp\

# Mac/Linux
mkdir -p ~/.google-calendar-mcp
cp path/to/downloaded/credentials.json ~/.google-calendar-mcp/
```

### 5. Build Docker Image

```bash
docker build -t google-calendar-mcp .
```

### 6. Authenticate with Google

**Windows:**
```bash
docker run -it --rm -v %USERPROFILE%\.google-calendar-mcp:/app/credentials -p 8081:8080 google-calendar-mcp python auth_setup_manual.py
```

**Mac/Linux:**
```bash
docker run -it --rm -v ~/.google-calendar-mcp:/app/credentials -p 8081:8080 google-calendar-mcp python auth_setup_manual.py
```

Follow the prompts:
1. Copy the authorization URL
2. Open in your browser
3. Sign in and authorize
4. Copy the authorization code
5. Paste back into terminal

### 7. Configure Claude Desktop

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

**Mac:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "YOUR_HOME_PATH/.google-calendar-mcp:/app/credentials",
        "-p",
        "8081:8080",
        "google-calendar-mcp"
      ]
    }
  }
}
```

**Replace `YOUR_HOME_PATH`:**
- Windows: `C:/Users/YourUsername`
- Mac/Linux: `${HOME}` or `/Users/YourUsername`

### 8. Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

## Usage Examples

### Schedule a Meeting
```
Schedule a meeting called "Team Standup" tomorrow at 10:00 AM
```

### Schedule with Attendees and Meet Link
```
Schedule a meeting called "Client Call" on January 15 at 2:00 PM with john@example.com, add a Google Meet link
```

### Check Availability
```
Check my calendar availability for next week
```

### Find Free Slots
```
Find free time slots tomorrow for a 2-hour meeting
```

### List Upcoming Events
```
Show me my upcoming calendar events
```

### Reschedule a Meeting
```
Reschedule event [event-id] to next Monday at 3:00 PM
```

### Cancel a Meeting
```
Cancel the meeting with event ID [event-id]
```

## Available Tools

| Tool | Description |
|------|-------------|
| `check_availability` | Check calendar availability between two dates |
| `schedule_meeting` | Schedule a new meeting with optional Meet link |
| `list_upcoming_events` | List upcoming calendar events |
| `find_free_slots` | Find available time slots on a specific date |
| `reschedule_meeting` | Move an existing meeting to a new time |
| `cancel_meeting` | Cancel a meeting with optional notifications |

## Configuration Options

### Default Settings
- Meeting duration: 30 minutes
- Working hours: 9:00 AM - 6:00 PM
- Timezone: Auto-detected from system
- Calendar: Primary calendar

### Customization
All tools accept parameters to customize behavior:
- Custom durations for meetings
- Include/exclude non-working hours
- Specify date ranges for availability checks

## Troubleshooting

### Server Disconnected Error
- Verify Docker is running: `docker ps`
- Check credentials folder exists and contains `credentials.json`
- Rebuild Docker image: `docker build -t google-calendar-mcp .`

### Authentication Failed
- Re-run authentication: `docker run -it --rm -v ...credentials -p 8081:8080 google-calendar-mcp python auth_setup_manual.py`
- Verify OAuth consent screen is configured correctly
- Check that your email is added as a test user

### Port Already in Use
- Change port in config from `8081:8080` to `8082:8080` or another available port
- Update authentication command to use same port

### Events Not Appearing
- Verify you're using the primary calendar
- Check timezone settings
- Refresh Google Calendar in browser

## Architecture

```
Claude Desktop
      ↓
   MCP Protocol (JSON-RPC)
      ↓
Docker Container (Python + FastMCP)
      ↓
Google Calendar API (OAuth 2.0)
      ↓
Google Calendar
```

## Tech Stack

- **FastMCP** - MCP server framework
- **Docker** - Containerization
- **Python 3.11** - Runtime environment
- **Google Calendar API** - Calendar operations
- **OAuth 2.0** - Secure authentication

## Security Notes

- Credentials are stored locally on your machine
- OAuth tokens are encrypted by Google
- No passwords are stored anywhere
- Access can be revoked anytime from Google Account settings
- Docker container runs in isolation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [Google Calendar API](https://developers.google.com/calendar)
- Powered by [Anthropic's Claude](https://www.anthropic.com/claude)

## Author

Your Name - [@yourhandle](https://twitter.com/yourhandle)

---

⭐ Star this repo if you find it helpful!

📝 Report issues or request features in the [Issues](https://github.com/yourusername/google-calendar-mcp/issues) sect
