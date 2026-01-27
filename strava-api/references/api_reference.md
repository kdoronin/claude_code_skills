# Strava API v3 Reference

Base URL: `https://www.strava.com/api/v3`

## Table of Contents
- [Authentication](#authentication)
- [Activities](#activities)
- [Athletes](#athletes)
- [Clubs](#clubs)
- [Gear](#gear)
- [Routes](#routes)
- [Segments](#segments)
- [Streams](#streams)
- [Uploads](#uploads)
- [Common Parameters](#common-parameters)
- [Error Handling](#error-handling)

---

## Authentication

All requests require OAuth 2.0 Bearer token:
```
Authorization: Bearer {access_token}
```

### Token Refresh
```
POST https://www.strava.com/oauth/token
Content-Type: application/x-www-form-urlencoded

client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token
```

Response:
```json
{
  "token_type": "Bearer",
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "expires_at": 1568775134,
  "expires_in": 21600
}
```

---

## Activities

### List Athlete Activities
```
GET /athlete/activities
```
Query params:
- `before` (integer) - Epoch timestamp, filter activities before this time
- `after` (integer) - Epoch timestamp, filter activities after this time
- `page` (integer) - Page number (default: 1)
- `per_page` (integer) - Items per page (default: 30, max: 200)

### Get Activity
```
GET /activities/{id}
```
Query params:
- `include_all_efforts` (boolean) - Include all segment efforts

### Create Activity (Manual)
```
POST /activities
```
Required scope: `activity:write`

Body params:
- `name` (string, required) - Activity name
- `sport_type` (string, required) - Sport type (Run, Ride, Swim, etc.)
- `start_date_local` (string, required) - ISO 8601 datetime
- `elapsed_time` (integer, required) - Seconds
- `description` (string) - Activity description
- `distance` (float) - Meters
- `trainer` (boolean) - Indoor trainer activity
- `commute` (boolean) - Commute activity

### Update Activity
```
PUT /activities/{id}
```
Required scope: `activity:write`

Body params:
- `name` (string)
- `sport_type` (string)
- `description` (string)
- `gear_id` (string)
- `trainer` (boolean)
- `commute` (boolean)
- `hide_from_home` (boolean)

### Get Activity Comments
```
GET /activities/{id}/comments
```
Query params: `page`, `per_page`, `page_size`, `after_cursor`

### Get Activity Kudoers
```
GET /activities/{id}/kudos
```
Query params: `page`, `per_page`

### Get Activity Laps
```
GET /activities/{id}/laps
```

### Get Activity Zones
```
GET /activities/{id}/zones
```
Requires Summit subscription.

---

## Athletes

### Get Authenticated Athlete
```
GET /athlete
```

### Get Athlete Stats
```
GET /athletes/{id}/stats
```
Returns recent (4 weeks), YTD, and all-time stats.

### Get Athlete Zones
```
GET /athlete/zones
```
Returns heart rate and power zones.

### Update Athlete
```
PUT /athlete
```
Required scope: `profile:write`

Body params:
- `weight` (float) - Kilograms

---

## Clubs

### Get Club
```
GET /clubs/{id}
```

### List Club Activities
```
GET /clubs/{id}/activities
```
Query params: `page`, `per_page`

### List Club Admins
```
GET /clubs/{id}/admins
```
Query params: `page`, `per_page`

### List Club Members
```
GET /clubs/{id}/members
```
Query params: `page`, `per_page`

### List Athlete Clubs
```
GET /athlete/clubs
```
Query params: `page`, `per_page`

---

## Gear

### Get Equipment
```
GET /gear/{id}
```
Returns details about bike or shoes.

---

## Routes

### Get Route
```
GET /routes/{id}
```

### List Athlete Routes
```
GET /athletes/{id}/routes
```
Query params: `page`, `per_page`

### Export Route GPX
```
GET /routes/{id}/export_gpx
```

### Export Route TCX
```
GET /routes/{id}/export_tcx
```

---

## Segments

### Get Segment
```
GET /segments/{id}
```

### Explore Segments
```
GET /segments/explore
```
Query params:
- `bounds` (string, required) - SW lat, SW lng, NE lat, NE lng (comma-separated)
- `activity_type` (string) - "running" or "riding"
- `min_cat` (integer) - Minimum climb category (0-5)
- `max_cat` (integer) - Maximum climb category (0-5)

### List Starred Segments
```
GET /segments/starred
```
Query params: `page`, `per_page`

### Star Segment
```
PUT /segments/{id}/starred
```
Body params:
- `starred` (boolean, required)

### Get Segment Efforts
```
GET /segments/{id}/all_efforts
```
Query params:
- `start_date_local` (string) - ISO 8601
- `end_date_local` (string) - ISO 8601
- `per_page` (integer)

### Get Segment Effort
```
GET /segment_efforts/{id}
```

---

## Streams

Streams return time-series data for activities, segments, and routes.

### Activity Streams
```
GET /activities/{id}/streams
```
Query params:
- `keys` (string, required) - Comma-separated: time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth
- `key_by_type` (boolean) - Default true

### Segment Streams
```
GET /segments/{id}/streams
```
Query params:
- `keys` (string, required) - latlng, distance, altitude

### Segment Effort Streams
```
GET /segment_efforts/{id}/streams
```
Query params:
- `keys` (string, required)
- `key_by_type` (boolean)

### Route Streams
```
GET /routes/{id}/streams
```

---

## Uploads

### Upload Activity
```
POST /uploads
```
Required scope: `activity:write`

Multipart form data:
- `file` (file) - Activity file (.fit, .tcx, .gpx, .fit.gz)
- `name` (string) - Activity name
- `description` (string) - Activity description
- `trainer` (boolean)
- `commute` (boolean)
- `data_type` (string, required) - fit, fit.gz, tcx, tcx.gz, gpx, gpx.gz
- `external_id` (string) - Unique identifier

### Get Upload Status
```
GET /uploads/{id}
```
Returns upload processing status and activity_id when complete.

---

## Common Parameters

### Pagination
- `page` - Page number (1-indexed)
- `per_page` - Items per page (default: 30, max: 200)

### Timestamps
- Use epoch seconds for `before`/`after` filters
- Use ISO 8601 format for date strings: `2024-01-15T10:30:00Z`

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No content (successful delete)
- `400` - Bad request
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient scope)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Server error

### Rate Limits
- 100 requests per 15 minutes
- 1000 requests per day
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Usage`

### Error Response Format
```json
{
  "message": "Error description",
  "errors": [
    {
      "resource": "Activity",
      "field": "name",
      "code": "invalid"
    }
  ]
}
```

---

## Sport Types

Valid `sport_type` values:
- Running: Run, TrailRun, VirtualRun
- Cycling: Ride, MountainBikeRide, GravelRide, EBikeRide, VirtualRide
- Swimming: Swim
- Walking: Walk, Hike
- Winter: AlpineSki, BackcountrySki, NordicSki, Snowboard, Snowshoe, IceSkate
- Water: Kayaking, Rowing, Canoeing, Surfing, Kitesurf, Windsurf, StandUpPaddling, Sail
- Other: Workout, WeightTraining, Yoga, CrossFit, Elliptical, StairStepper, Wheelchair, Handcycle, Golf, Pickleball, Racquetball, Squash, Badminton, Tennis, TableTennis, Velomobile, Skateboard, InlineSkate, RockClimbing
