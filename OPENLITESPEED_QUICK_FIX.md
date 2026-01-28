# OpenLiteSpeed WebSocket Quick Fix Commands

Run these commands directly on your Alma Linux server:

## Step 1: Check Current Configuration

```bash
# Check if WebSocket Proxy exists
grep -A 3 "wsProxy" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf

# Check for conflicting Context /ws/
grep -A 5 "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 2: Remove Conflicting Context (if exists)

If the grep above shows a `context /ws/` block, remove it:

```bash
# Backup first
cp /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf.backup.$(date +%Y%m%d_%H%M%S)

# Remove Context /ws/ block
sed -i '/context \/ws\/ {/,/^[[:space:]]*}/d' /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 3: Add WebSocket Proxy (if missing)

If `grep wsProxy` shows nothing, add it:

```bash
# Backup
cp /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf.backup.$(date +%Y%m%d_%H%M%S)

# Add wsProxy block before closing virtualhost brace
# This uses awk to insert it properly
awk '
/virtualhost/ { in_vhost=1; brace=0 }
in_vhost {
    brace += gsub(/{/, "&")
    brace -= gsub(/}/, "&")
    if (brace == 1 && /^[[:space:]]*}/ && !added) {
        print "  wsProxy {"
        print "    uri                     /ws/"
        print "    address                 127.0.0.1:9000"
        print "  }"
        added=1
    }
}
{ print }
' /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf > /tmp/vhost.conf.tmp && mv /tmp/vhost.conf.tmp /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 4: Verify Configuration

```bash
# Should show wsProxy block
grep -A 3 "wsProxy" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf

# Should show nothing (no Context /ws/)
grep "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 5: Reload LiteSpeed

```bash
/usr/local/lsws/bin/lswsctrl reload
```

## Step 6: Restart Django

```bash
pm2 restart app.crm.click2print.store
```

## All-in-One Fix Script

Or run this single command to do everything:

```bash
VHOST="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf" && \
cp "$VHOST" "${VHOST}.backup.$(date +%Y%m%d_%H%M%S)" && \
sed -i '/context \/ws\/ {/,/^[[:space:]]*}/d' "$VHOST" && \
awk '/virtualhost/ { in_vhost=1; brace=0 } in_vhost { brace += gsub(/{/, "&"); brace -= gsub(/}/, "&"); if (brace == 1 && /^[[:space:]]*}/ && !added) { print "  wsProxy {"; print "    uri                     /ws/"; print "    address                 127.0.0.1:9000"; print "  }"; added=1 } } { print }' "$VHOST" > /tmp/vhost.conf.tmp && mv /tmp/vhost.conf.tmp "$VHOST" && \
grep -A 3 "wsProxy" "$VHOST" && \
/usr/local/lsws/bin/lswsctrl reload && \
pm2 restart app.crm.click2print.store && \
echo "✓ Configuration complete!"
```

































