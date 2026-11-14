# License configuration

Set the PHP verification endpoint either as `HUMANEX_LICENSE_API_URL` or in
the per-user file below:

- Windows: `%APPDATA%\HumanexBot\license_config.json`
- Linux/macOS: `~/.humanexbot/HumanexBot/license_config.json`

```json
{
  "api_url": "https://your-license-server.example/api/verify"
}
```

The application remains locked when this file is missing, malformed, or the
API rejects the key. License keys and API responses are never written to the
startup log.
