#!/bin/sh
# nginx-entrypoint.sh - Generates nginx.conf from template with env substitution
# Supports conditional blocks: {{#VAR}}...{{/VAR}} shown only when VAR is set

set -e

CONF_TEMPLATE="/etc/nginx/nginx.conf.template"
CONF_OUTPUT="/etc/nginx/conf.d/default.conf"

# Default values
NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-localhost}"
SSL_CERT_PATH="${SSL_CERT_PATH:-}"
SSL_KEY_PATH="${SSL_KEY_PATH:-}"
SSL_CA_PATH="${SSL_CA_PATH:-}"

# Function: process template with envsubst + conditional blocks
process_template() {
    local template="$1"
    local output="$2"

    # First pass: envsubst for simple ${VAR} replacements
    envsubst '${NGINX_SERVER_NAME} ${SSL_CERT_PATH} ${SSL_KEY_PATH} ${SSL_CA_PATH}' \
        < "$template" > "$output.tmp"

    # Second pass: handle conditional blocks {{#VAR}}...{{/VAR}}
    # Content inside block is KEPT only if the corresponding env var is non-empty
    for var in SSL_CERT_PATH SSL_CA_PATH; do
        local val
        eval "val=\"\$$var\""
        if [ -n "$val" ]; then
            # Variable is set - keep content, remove markers
            perl -i -0pe "s/\{\{#${var}\}\}(.*?)\{\{\/${var}\}\}/\$1/gs" "$output.tmp"
        else
            # Variable is not set - remove the entire block
            perl -i -0pe "s/\{\{#${var}\}\}.*?\{\{\/${var}\}\}//gs" "$output.tmp"
        fi
    done

    mv "$output.tmp" "$output"

    if [ -n "$SSL_CERT_PATH" ]; then
        echo "nginx.conf generated - HTTPS ENABLED (cert=$SSL_CERT_PATH)"
    else
        echo "nginx.conf generated - HTTPS DISABLED (SSL_CERT_PATH not set)"
    fi
}

# Process the template
if [ -f "$CONF_TEMPLATE" ]; then
    process_template "$CONF_TEMPLATE" "$CONF_OUTPUT"
else
    echo "WARNING: Template not found at $CONF_TEMPLATE"
fi

exec "$@"
