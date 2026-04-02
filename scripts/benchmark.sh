#!/usr/bin/env bash
set -euo pipefail

# Profile ghlang startup time, import costs, and chart generation
#
# Usage:
#   ./scripts/benchmark.sh              full benchmark
#   ./scripts/benchmark.sh --imports    import profiling only
#   ./scripts/benchmark.sh --startup    startup timing only
#   ./scripts/benchmark.sh --charts     chart generation only
#
# Requires: hyperfine, python3, uv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/bench"

MODE="all"
for arg in "$@"; do
    case "$arg" in
        --imports) MODE="imports" ;;
        --startup) MODE="startup" ;;
        --charts)  MODE="charts" ;;
    esac
done

# ---------------------------------------------------------------------------
# tool checks
# ---------------------------------------------------------------------------
for tool in hyperfine python3; do
    command -v "$tool" &> /dev/null || { echo "error: $tool not found in PATH" >&2; exit 1; }
done

command -v uv &> /dev/null || { echo "error: uv not found in PATH" >&2; exit 1; }

mkdir -p "$RESULTS_DIR"

# ---------------------------------------------------------------------------
# import profiling: find which imports are slowest
# ---------------------------------------------------------------------------
run_imports() {
    echo "=== Import profiling ==="
    echo ""

    cd "$PROJECT_ROOT"

    echo "Top 20 slowest imports (cumulative):"
    uv run python -X importtime -c "from ghlang.cli import app" 2>&1 \
        | sort -t'|' -k2 -n \
        | tail -20
    echo ""

    echo "Top 20 slowest imports (self time):"
    uv run python -X importtime -c "from ghlang.cli import app" 2>&1 \
        | sort -t'|' -k1 -n \
        | tail -20
    echo ""

    echo "Matplotlib import cost:"
    uv run python -X importtime -c "import matplotlib.pyplot" 2>&1 \
        | grep "import time:.*matplotlib" \
        | tail -5
    echo ""

    echo "PIL import cost:"
    uv run python -X importtime -c "from PIL import Image" 2>&1 \
        | grep "import time:.*PIL" \
        | tail -5
    echo ""

    echo "Rich + Typer import cost:"
    uv run python -X importtime -c "import typer; from rich.console import Console" 2>&1 \
        | grep -E "import time:.*(rich|typer|click)" \
        | tail -10
    echo ""
}

# ---------------------------------------------------------------------------
# startup timing: how fast is the CLI shell
# ---------------------------------------------------------------------------
run_startup() {
    echo "=== Startup benchmarks ==="
    echo ""

    cd "$PROJECT_ROOT"

    echo "--- ghlang --version (full CLI startup) ---"
    hyperfine --warmup 3 --runs 20 \
        --export-json "$RESULTS_DIR/startup.json" \
        "uv run ghlang --version"
    echo ""

    echo "--- ghlang --help (includes command registration) ---"
    hyperfine --warmup 3 --runs 20 \
        "uv run ghlang --help"
    echo ""

    echo "--- bare python import (no CLI) ---"
    hyperfine --warmup 3 --runs 20 \
        "uv run python -c 'from ghlang.cli import app'"
    echo ""

    echo "--- python startup baseline ---"
    hyperfine --warmup 3 --runs 20 \
        "uv run python -c 'pass'"
    echo ""
}

# ---------------------------------------------------------------------------
# chart generation: time each style
# ---------------------------------------------------------------------------
run_charts() {
    echo "=== Chart generation benchmarks ==="
    echo ""

    cd "$PROJECT_ROOT"
    BENCH_TMPDIR="$(mktemp -d "/tmp/.ghlang_bench_XXXXXX")"
    trap 'rm -rf "$BENCH_TMPDIR"' EXIT

    uv run python "$SCRIPT_DIR/bench_data.py" "$BENCH_TMPDIR" > /dev/null

    for style in pixel pie bar; do
        echo "--- $style style ---"
        hyperfine --warmup 2 --runs 10 \
            --export-json "$RESULTS_DIR/chart_${style}.json" \
            "uv run python $SCRIPT_DIR/bench_chart.py $style $BENCH_TMPDIR"
        echo ""
    done

    echo "Results saved to $RESULTS_DIR/"
}

# ---------------------------------------------------------------------------
# run selected benchmarks
# ---------------------------------------------------------------------------
echo "ghlang benchmark suite"
echo "────────────────────────────────────────────────────────────"
echo ""

case "$MODE" in
    imports) run_imports ;;
    startup) run_startup ;;
    charts)  run_charts ;;
    all)
        run_imports
        echo "────────────────────────────────────────────────────────────"
        run_startup
        echo "────────────────────────────────────────────────────────────"
        run_charts
        ;;
esac

echo "────────────────────────────────────────────────────────────"
echo "Done"
