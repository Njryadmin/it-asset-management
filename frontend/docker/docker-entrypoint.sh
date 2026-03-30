#!/bin/sh
# nginx-entrypoint.sh - Generates nginx.conf from template with env substitution
# Conditional blocks: {{#VAR}}...{{/VAR}} kept only when VAR is non-empty

set -e

CONF_TEMPLATE="/etc/nginx/nginx.conf.template"
CONF_OUTPUT="/etc/nginx/conf.d/default.conf"

NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-localhost}"
SSL_CERT_PATH="${SSL_CERT_PATH:-}"
SSL_KEY_PATH="${SSL_KEY_PATH:-}"
SSL_CA_PATH="${SSL_CA_PATH:-}"

# First pass: envsubst for ${VAR} replacements
envsubst '${NGINX_SERVER_NAME} ${SSL_CERT_PATH} ${SSL_KEY_PATH} ${SSL_CA_PATH}' \
    < "$CONF_TEMPLATE" > "$CONF_OUTPUT"

# Second pass: process conditional blocks with perl
# {{#VAR}}...{{/VAR}} - keep inner only if VAR is non-empty, else remove entire block
for var in SSL_CERT_PATH SSL_CA_PATH; do
    val="$(eval "echo \$$var")"
    if [ -n "$val" ]; then
        # Keep content, strip {{#VAR}} and {{/VAR}} markers
        perl -i -0pe "s/\{\{#${var}\}\}(.*?)\{\{\/${var}\}\}/\$1/gs" "$CONF_OUTPUT"
    else
        # Remove entire block
        perl -i -0pe "s/\{\{#${var}\}\}.*?\{\{\/${var}\}\}//gs" "$CONF_OUTPUT"
    fi
done

if [ -n "$SSL_CERT_PATH" ]; then
    echo "nginx.conf generated - HTTPS ENABLED (cert=$SSL_CERT_PATH)"
else
    echo "nginx.conf generated - HTTPS DISABLED"
fi

exec "$@"
