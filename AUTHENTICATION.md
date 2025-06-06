# Microsoft Authentication Setup for Power Apps Testing

This guide explains how to set up Microsoft Office 365 authentication with 2FA support for testing Power Apps forms using FormGenius.

## Overview

FormGenius supports automated testing of Microsoft Power Apps forms that require Office 365 authentication. The system handles:

- ✅ Microsoft Office 365 login
- ✅ Two-Factor Authentication (2FA)
- ✅ Authentication state persistence
- ✅ Automatic token refresh
- ✅ Secure credential storage

## Quick Start

### 1. Initial Authentication Setup

Run the authentication setup script:

```bash
python setup_auth.py
```

This will:
- Prompt for your Microsoft email and password
- Open a browser window for authentication
- Handle 2FA automatically (you'll complete it manually)
- Save authentication state for future use

### 2. Test Power Apps Forms

After authentication is set up, you can test Power Apps forms:

```bash
# Test a specific Power Apps form
python main.py power-apps --url "https://apps.powerapps.com/play/your-app-id"

# Or use the example script
python test_power_apps_auth.py
```

## Detailed Setup Process

### Prerequisites

1. **Microsoft Office 365 Account**: You need a valid Office 365 account
2. **Access to Power Apps**: Your account must have access to the Power Apps you want to test
3. **2FA Device**: Have your authenticator app or phone ready for 2FA
4. **FormGenius Installation**: Ensure FormGenius is properly installed

### Step-by-Step Authentication

1. **Start the setup**:
   ```bash
   python setup_auth.py
   ```

2. **Enter your credentials**:
   - Microsoft email address
   - Microsoft password

3. **Complete 2FA in the browser**:
   - The script will open a browser window
   - Complete the 2FA process as you normally would
   - Don't close the browser window during this process

4. **Wait for completion**:
   - The script will automatically detect when authentication is complete
   - Authentication state will be saved for future use

### Authentication Files

After successful authentication, these files are created:

- `auth_state.json` - Browser authentication state (cookies, local storage, etc.)
- `auth_cache.json` - Authentication metadata and expiry information

⚠️ **Important**: These files contain sensitive authentication data and are automatically added to `.gitignore`.

## Using Authentication

### Automatic Authentication

Once set up, FormGenius automatically handles authentication:

```python
from formgenius.core.config import Config
from formgenius.core.agent import FormGeniusAgent

# Load configuration
config = Config.from_yaml('config.yaml')

# Create agent
agent = FormGeniusAgent(config)

# Test Power Apps form (authentication handled automatically)
result = await agent.fill_power_apps_form(
    app_url="https://apps.powerapps.com/play/your-app-id",
    test_scenarios=['valid']
)
```

### Manual Authentication Control

For advanced use cases, you can manually control authentication:

```python
from formgenius.auth.microsoft_auth import MicrosoftAuthenticator
from formgenius.integrations.playwright_mcp import PlaywrightMCPClient

# Initialize Playwright client
playwright_client = PlaywrightMCPClient(config)
await playwright_client.initialize()

# Initialize authenticator
authenticator = MicrosoftAuthenticator(config, playwright_client)

# Check authentication status
status = await authenticator.get_auth_status()
print(f"Authenticated: {status['authenticated']}")

# Force re-authentication if needed
if not status['authenticated']:
    result = await authenticator.authenticate("your-email@company.com", "your-password")
```

## Commands Reference

### Authentication Management

```bash
# Setup authentication (interactive)
python setup_auth.py

# Check authentication status
python setup_auth.py status

# Clear authentication cache
python setup_auth.py clear

# Show help
python setup_auth.py help
```

### Power Apps Testing

```bash
# Test a Power Apps form
python main.py power-apps --url "https://apps.powerapps.com/play/app-id"

# Test with specific scenario
python main.py power-apps --url "https://apps.powerapps.com/play/app-id" --scenario validation_test

# Run example test
python test_power_apps_auth.py
```

## Configuration

Authentication settings in `config.yaml`:

```yaml
authentication:
  microsoft:
    enabled: true
    cache_duration: 30  # Days
    login_timeout: 300  # Seconds
    two_fa_timeout: 300  # Seconds
    retry_attempts: 3
```

## Troubleshooting

### Common Issues

#### 1. Authentication Fails

**Symptoms**: Login redirects back to login page
**Solutions**:
- Verify email and password are correct
- Ensure 2FA was completed successfully
- Check if account has access to Power Apps
- Try clearing cache: `python setup_auth.py clear`

#### 2. 2FA Timeout

**Symptoms**: "2FA timeout" error message
**Solutions**:
- Ensure you complete 2FA within 5 minutes
- Don't close the browser window during authentication
- Check your internet connection
- Try the setup again

#### 3. Authentication Expired

**Symptoms**: "Authentication may have expired" error
**Solutions**:
- Re-run the authentication setup: `python setup_auth.py`
- Check if your Office 365 account is still active
- Verify Power Apps access permissions

#### 4. Browser Issues

**Symptoms**: Browser doesn't open or crashes
**Solutions**:
- Ensure Playwright browsers are installed: `playwright install`
- Try running in non-headless mode (default)
- Check if Chrome/Chromium is properly installed

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python setup_auth.py --verbose
python main.py power-apps --url "your-url" --verbose
```

### Manual Cache Cleanup

If you need to manually clean authentication:

```bash
# Remove authentication files
rm -f auth_state.json auth_cache.json

# Or use the built-in command
python setup_auth.py clear
```

## Security Considerations

### Data Protection

- Authentication files are stored locally and never transmitted
- Files are automatically excluded from version control
- Sensitive data is encrypted by Playwright's storage system

### Best Practices

1. **Regular Re-authentication**: Set up authentication to expire after 30 days
2. **Secure Environment**: Run authentication setup on a secure machine
3. **Account Separation**: Use a dedicated test account if possible
4. **Access Control**: Ensure only authorized users can access authentication files

### What's Stored

The authentication system stores:
- Browser cookies and session data
- Local storage contents
- Authentication tokens (encrypted)
- Metadata about authentication state

The system does NOT store:
- Plain text passwords
- Personal information
- Business data from Power Apps

## Advanced Usage

### Custom Authentication Flow

For organizations with custom authentication requirements:

```python
# Custom authentication with specific settings
authenticator = MicrosoftAuthenticator(config, playwright_client)

# Set custom timeouts
authenticator.login_timeout = 600  # 10 minutes
authenticator.two_fa_timeout = 900  # 15 minutes

# Perform authentication
result = await authenticator.authenticate(email, password, force_reauth=True)
```

### Batch Testing with Authentication

For testing multiple Power Apps with the same authentication:

```python
# Authenticate once
authenticator = MicrosoftAuthenticator(config, playwright_client)
await authenticator.authenticate(email, password)

# Test multiple apps
apps = [
    "https://apps.powerapps.com/play/app1-id",
    "https://apps.powerapps.com/play/app2-id",
    "https://apps.powerapps.com/play/app3-id"
]

for app_url in apps:
    result = await agent.fill_power_apps_form(app_url=app_url)
    print(f"App {app_url}: {'✅' if result['success'] else '❌'}")
```

## Support

If you encounter issues:

1. Check this documentation first
2. Enable debug logging for more details
3. Verify your Office 365 account access
4. Ensure FormGenius is up to date

For additional help, refer to the main FormGenius documentation or create an issue in the project repository.
