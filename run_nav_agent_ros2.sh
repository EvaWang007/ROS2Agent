#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/Downloads/rosa-main"
WS="$ROOT/nav_ws"
CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
ROSA_PY="$HOME/miniconda3/envs/rosa/bin/python"
AGENT_BIN="$WS/install/nav_agent_ros2/lib/nav_agent_ros2/nav_agent"

export AMENT_TRACE_SETUP_FILES="${AMENT_TRACE_SETUP_FILES:-}"

source "$CONDA_SH"
conda activate rosa
source /opt/ros/humble/setup.bash

cd "$WS"
colcon build --packages-select nav_agent_ros2 --symlink-install
source "$WS/install/setup.bash"

export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"

# Local Clash-Verge HTTP mixed port (override: export ROSA_HTTP_PROXY_URL=http://127.0.0.1:PORT)
ROSA_HTTP_PROXY_URL="${ROSA_HTTP_PROXY_URL:-http://127.0.0.1:7897}"
export HTTP_PROXY="$ROSA_HTTP_PROXY_URL" HTTPS_PROXY="$ROSA_HTTP_PROXY_URL"
export http_proxy="$ROSA_HTTP_PROXY_URL" https_proxy="$ROSA_HTTP_PROXY_URL"
export ALL_PROXY="$ROSA_HTTP_PROXY_URL" all_proxy="$ROSA_HTTP_PROXY_URL"
export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1}"
export no_proxy="${no_proxy:-localhost,127.0.0.1,::1}"

exec "$ROSA_PY" "$AGENT_BIN"
