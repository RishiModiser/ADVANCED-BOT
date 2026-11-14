# License configuration

The Windows application uses the production PHP verification endpoint by
default:

`https://adsenseloadingmethod.com/license_system/check_license.php`

No environment variable or customer-side configuration is required. For
development or staging builds only, an HTTPS endpoint may be supplied through
the following per-user file:

- Windows: `%APPDATA%\HumanexBot\license_config.json`
- Linux/macOS: `~/.humanexbot/HumanexBot/license_config.json`

```json
{
  "api_url": "https://your-development-license-server.example/check_license.php"
}
```

The `HUMANEX_LICENSE_API_URL` environment variable is also supported for
development diagnostics. The application remains locked when the endpoint is
unavailable or the API rejects the key. License keys and API responses are
never written to the startup log.
