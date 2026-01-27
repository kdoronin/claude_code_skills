# Strava API Setup Guide

This guide explains how to obtain credentials for Strava API access.

## Prerequisites

- Strava account (free or paid)
- Web browser

## Step 1: Create Strava API Application

1. Go to https://www.strava.com/settings/api
2. Fill in the application form:
   - **Application Name**: Your app name (e.g., "My Fitness Tracker")
   - **Category**: Choose appropriate category
   - **Club**: Optional
   - **Website**: Your website or `http://localhost`
   - **Authorization Callback Domain**: `localhost` (for local development)
3. Click "Create"
4. Save the following credentials:
   - **Client ID** (numeric)
   - **Client Secret** (alphanumeric string)

## Step 2: Obtain Authorization Code

Open this URL in browser (replace `{CLIENT_ID}`):

```
https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost&scope=read,read_all,profile:read_all,profile:write,activity:read,activity:read_all,activity:write
```

### Available Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read public segments, routes, profile |
| `read_all` | Read private routes, segments |
| `profile:read_all` | Read all profile information |
| `profile:write` | Update profile weight |
| `activity:read` | Read activities visible to Everyone |
| `activity:read_all` | Read all activities (including private) |
| `activity:write` | Create and update activities |

After authorization, you'll be redirected to:
```
http://localhost/?state=&code={AUTHORIZATION_CODE}&scope=read,activity:write,...
```

Copy the `code` parameter value.

## Step 3: Exchange Code for Tokens

Make a POST request:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id={CLIENT_ID} \
  -d client_secret={CLIENT_SECRET} \
  -d code={AUTHORIZATION_CODE} \
  -d grant_type=authorization_code
```

Response:
```json
{
  "token_type": "Bearer",
  "expires_at": 1568775134,
  "expires_in": 21600,
  "refresh_token": "your_refresh_token",
  "access_token": "your_access_token",
  "athlete": {
    "id": 123456,
    "firstname": "John",
    "lastname": "Doe"
  }
}
```

Save:
- **access_token** - Use for API requests (expires in 6 hours)
- **refresh_token** - Use to get new access tokens

## Step 4: Token Refresh

Access tokens expire after 6 hours. Refresh them:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id={CLIENT_ID} \
  -d client_secret={CLIENT_SECRET} \
  -d refresh_token={REFRESH_TOKEN} \
  -d grant_type=refresh_token
```

## Environment Variables

Store credentials securely. Recommended environment variables:

```bash
export STRAVA_CLIENT_ID="your_client_id"
export STRAVA_CLIENT_SECRET="your_client_secret"
export STRAVA_ACCESS_TOKEN="your_access_token"
export STRAVA_REFRESH_TOKEN="your_refresh_token"
```

Or create `.env` file (add to .gitignore):

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_ACCESS_TOKEN=your_access_token
STRAVA_REFRESH_TOKEN=your_refresh_token
```

## Verify Setup

Test your access token:

```bash
curl -X GET "https://www.strava.com/api/v3/athlete" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

Should return your athlete profile.

## Troubleshooting

### "Authorization Error"
- Check Client ID is correct
- Verify redirect URI matches your app settings

### "Invalid Token"
- Token may be expired, use refresh token
- Check token is copied correctly without extra spaces

### "Forbidden"
- Missing required scope
- Re-authorize with correct scopes

### Rate Limit Exceeded
- 100 requests per 15 minutes
- 1000 requests per day
- Wait and retry

## Required Data Summary

To use the Strava API skill, you need:

| Credential | Where to Get | Required |
|------------|--------------|----------|
| Client ID | Strava API settings page | Yes |
| Client Secret | Strava API settings page | Yes |
| Access Token | OAuth flow (Step 3) | Yes |
| Refresh Token | OAuth flow (Step 3) | Yes (for long-term use) |
| Athlete ID | API response or profile URL | For some endpoints |
