#!/bin/bash
# WSL2 Windows Toast Notification Hook
# Sends a Windows Toast notification when Claude Code completes a task

# Read task status from environment variables
# $NOTIFICATION_TITLE, $NOTIFICATION_MESSAGE etc. are expected to be set

TITLE="${1:-Claude Code}"
MESSAGE="${2:-Task completed}"

# Send Windows Toast notification via PowerShell
# Run 'powershell.exe' from WSL environment
powershell.exe -NoProfile -NonInteractive -Command "
  [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications] | Out-Null
  [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications] | Out-Null
  [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument] | Out-Null

  \$APP_ID = 'Claude Code'
  \$template = @\"
    <toast activationType='protocol' launch='app-defined-string'>
      <visual>
        <binding template='ToastText02'>
          <text id='1'>$TITLE</text>
          <text id='2'>$MESSAGE</text>
        </binding>
      </visual>
    </toast>
  \"@

  \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
  \$xml.LoadXml(\$template)
  \$toast = New-Object Windows.UI.Notifications.ToastNotification \$xml
  [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\$APP_ID).Show(\$toast)
" 2>/dev/null || true

# Continue even on failure (notifications are optional)
exit 0
