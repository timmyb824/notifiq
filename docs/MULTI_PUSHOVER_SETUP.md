# Multi-Application Pushover Setup Guide

## Overview

Notifiq now supports routing notifications to multiple Pushover applications, allowing you to organize alerts by category (infra, CI/CD, monitoring, etc.).

## Configuration

### 1. Create Pushover Applications

In your Pushover dashboard:
1. Create separate applications for each category (e.g., "Infrastructure", "CI/CD", "Monitoring")
2. Note the API Token for each application
3. Keep your User Key handy (same for all apps)

### 2. Set Environment Variables

Use the pattern `APPRISE_PUSHOVER_{APP_ID}_URL`:

```bash
# Infrastructure alerts
export APPRISE_PUSHOVER_INFRA_URL="pover://YOUR_USER_KEY@INFRA_TOKEN"

# CI/CD alerts
export APPRISE_PUSHOVER_CICD_URL="pover://YOUR_USER_KEY@CICD_TOKEN"

# Monitoring alerts
export APPRISE_PUSHOVER_MONITORING_URL="pover://YOUR_USER_KEY@MONITORING_TOKEN"
```

**Important:** The app identifier (e.g., `INFRA`, `CICD`, `MONITORING`) will be converted to lowercase and used as the `pushover_app` value in messages.

### 3. Update Your Message Producers

Add the `pushover_app` field to your RabbitMQ messages:

```json
{
  "title": "Build Failed",
  "message": "Pipeline xyz failed on main branch",
  "channels": ["pushover-direct"],
  "pushover_app": "cicd"
}
```

```json
{
  "title": "Server Down",
  "message": "prod-web-01 is unreachable",
  "channels": ["pushover-direct"],
  "pushover_app": "infra",
  "priority": "high"
}
```

## Testing

Use the updated test script:

```bash
# Test infrastructure app
python scripts/send_test_notification.py \
  --channels pushover-direct \
  --title "Test Infrastructure Alert" \
  --message "This is a test" \
  --pushover_app infra

# Test CI/CD app
python scripts/send_test_notification.py \
  --channels pushover-direct \
  --title "Test CI/CD Alert" \
  --message "Build completed" \
  --pushover_app cicd \
  --priority high
```

## Backward Compatibility

- **Single app setup:** If you only configure one Pushover app, `pushover_app` is optional
- **Legacy setup:** `APPRISE_PUSHOVER_URL` (without app identifier) is registered as "default" app
- **Missing app:** If `pushover_app` is not specified with multiple apps, the first app will be used with a warning logged

## Example Use Cases

### Infrastructure Monitoring
```json
{
  "title": "🔴 Disk Space Critical",
  "message": "Server prod-db-01: 95% disk usage",
  "channels": ["pushover-direct"],
  "pushover_app": "infra",
  "priority": "emergency"
}
```

### CI/CD Pipeline
```json
{
  "title": "✅ Deployment Complete",
  "message": "v2.1.0 deployed to production",
  "channels": ["pushover-direct"],
  "pushover_app": "cicd",
  "priority": "normal"
}
```

### Application Monitoring
```json
{
  "title": "⚠️ High Error Rate",
  "message": "API error rate: 5% (threshold: 1%)",
  "channels": ["pushover-direct"],
  "pushover_app": "monitoring",
  "priority": "high",
  "pushover_device": ["iphone", "ipad"]
}
```

## Benefits

1. **Better Organization:** Separate notification streams in Pushover UI
2. **Custom Settings:** Different sounds, priorities, and quiet hours per category
3. **Easier Filtering:** Quickly identify alert types at a glance
4. **Flexible Routing:** Route different alert types to different devices
5. **Scalable:** Add new categories without code changes

## Troubleshooting

### Notification not received
- Check logs for: `Sent to Pushover app: {app_id}`
- Verify the app identifier matches your environment variable (case-insensitive)
- Confirm the token is correct for that application

### Warning: "No pushover_app specified"
- This means you have multiple Pushover apps configured but didn't specify which one to use
- Add `"pushover_app": "your_app_id"` to your message
- Or configure only one Pushover app if you don't need routing

### App not found
- Check that `APPRISE_PUSHOVER_{APP_ID}_URL` is set correctly
- Verify the app identifier in your message matches the environment variable
- Check logs for: `Initialized Pushover notifier for app: {app_id}`
