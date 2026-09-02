# gcloud auth login

# Claude Code release channel: "stable" or "latest".
# Edit this value to switch; the script re-pins the install when it changes.
CLAUDE_CHANNEL="latest"

export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID="landing-zone-demo-341118"
export CLOUD_ML_REGION="global"
# export CLAUDE_CODE_EFFORT_LEVEL=xhigh
export CLAUDE_CODE_EFFORT_LEVEL=high
MODELS=("claude-sonnet-5[1m]" "claude-opus-5[1m]" "claude-fable-5-1[1m]")
DEFAULT_MODEL="claude-sonnet-5[1m]"
PS3="Select a model (default: $DEFAULT_MODEL): "
while true; do
  for i in "${!MODELS[@]}"; do
    printf '%d) %s\n' "$((i + 1))" "${MODELS[$i]}"
  done
  read -r -p "$PS3" REPLY
  if [ -z "$REPLY" ]; then
    ANTHROPIC_MODEL="$DEFAULT_MODEL"
    break
  elif [ "$REPLY" -ge 1 ] 2>/dev/null && [ "$REPLY" -le "${#MODELS[@]}" ] 2>/dev/null; then
    ANTHROPIC_MODEL="${MODELS[$((REPLY - 1))]}"
    break
  fi
  echo "Invalid choice, try again."
done
export ANTHROPIC_MODEL
export CLAUDE_CODE_ENABLE_AUTO_MODE=1

# Trust corporate proxy / MDM root CAs from the macOS keychain.
# Node ships its own CA store and ignores the keychain by default, so traffic
# through the corp proxy fails with "SSL certificate verification failed".
# Export the keychain roots to a bundle and point Node at it.
CA_BUNDLE="$HOME/.config/node-ca-bundle.pem"
mkdir -p "$(dirname "$CA_BUNDLE")"
{ security find-certificate -a -p /Library/Keychains/System.keychain
  security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain
} > "$CA_BUNDLE" 2>/dev/null
export NODE_EXTRA_CA_CERTS="$CA_BUNDLE"

gcloud auth application-default print-access-token >/dev/null 2>&1 || gcloud auth application-default login
"$(dirname "$0")/setup-data-sharing.sh"

# Re-pin the install only when CLAUDE_CHANNEL changed since the last launch,
# so normal starts stay fast and offline-safe.
chan_file="$HOME/.local/share/claude/.run-sh-channel"
if [ "$(cat "$chan_file" 2>/dev/null)" != "$CLAUDE_CHANNEL" ]; then
  "$HOME/.local/bin/claude" install "$CLAUDE_CHANNEL" && printf '%s' "$CLAUDE_CHANNEL" > "$chan_file"
fi

"$HOME/.local/bin/claude"