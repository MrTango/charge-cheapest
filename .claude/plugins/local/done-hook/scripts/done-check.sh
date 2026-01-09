#!/bin/bash
set -o pipefail

# Read input from stdin (hook provides JSON context)
input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty')

# Use provided cwd or fall back to CLAUDE_PROJECT_DIR
PROJECT_DIR="${cwd:-$CLAUDE_PROJECT_DIR}"

if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
    echo '{"continue": true, "systemMessage": "Could not determine project directory"}'
    exit 0
fi

cd "$PROJECT_DIR" || exit 0

# Initialize results
results=()
has_errors=false
ran_checks=false

# =============================================================================
# Python Project Detection and Checks
# =============================================================================
run_python_checks() {
    local python_found=false

    # Check for Python project indicators
    if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ] || \
       [ -f "Pipfile" ] || [ -d ".venv" ] || [ -d "venv" ]; then
        python_found=true
    fi

    # Also check if there are any .py files
    if ! $python_found && find . -maxdepth 3 -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
        python_found=true
    fi

    if ! $python_found; then
        return 0
    fi

    ran_checks=true
    echo "Python project detected in $PROJECT_DIR" >&2

    # Check for ruff and run format + lint
    if command -v ruff &> /dev/null; then
        echo "Running ruff format check..." >&2
        if ruff format --check . 2>&1; then
            results+=("RUFF Format: PASSED")
        else
            results+=("RUFF Format: FAILED - files need formatting (run 'ruff format .')")
            has_errors=true
        fi

        echo "Running ruff lint..." >&2
        if ruff check . 2>&1; then
            results+=("RUFF Lint: PASSED")
        else
            results+=("RUFF Lint: FAILED - linting errors found (run 'ruff check --fix .')")
            has_errors=true
        fi
    elif [ -f "pyproject.toml" ] && grep -q "ruff" "pyproject.toml" 2>/dev/null; then
        results+=("RUFF: NOT INSTALLED but configured in pyproject.toml")
        has_errors=true
    fi

    # Check for pytest and run tests
    if command -v pytest &> /dev/null; then
        # Check if there are test files
        if find . -maxdepth 4 \( -name "test_*.py" -o -name "*_test.py" -o -path "*/tests/*.py" \) -type f 2>/dev/null | head -1 | grep -q .; then
            echo "Running pytest..." >&2
            if pytest --tb=short -q 2>&1; then
                results+=("Pytest: PASSED")
            else
                results+=("Pytest: FAILED - tests did not pass")
                has_errors=true
            fi
        else
            results+=("Pytest: SKIPPED - no test files found")
        fi
    elif [ -f "pyproject.toml" ] && grep -q "pytest" "pyproject.toml" 2>/dev/null; then
        results+=("Pytest: NOT INSTALLED but configured in pyproject.toml")
    fi
}

# =============================================================================
# JavaScript/TypeScript Project Detection and Checks
# =============================================================================
run_javascript_checks() {
    local js_found=false

    # Check for JS/TS project indicators
    if [ -f "package.json" ]; then
        js_found=true
    fi

    if ! $js_found; then
        return 0
    fi

    ran_checks=true
    echo "JavaScript/TypeScript project detected in $PROJECT_DIR" >&2

    # Determine package manager
    local pkg_manager="npm"
    if [ -f "pnpm-lock.yaml" ]; then
        pkg_manager="pnpm"
    elif [ -f "yarn.lock" ]; then
        pkg_manager="yarn"
    elif [ -f "bun.lockb" ]; then
        pkg_manager="bun"
    fi

    # Read package.json scripts
    local has_lint=false
    local has_format=false
    local has_test=false
    local has_typecheck=false

    if [ -f "package.json" ]; then
        has_lint=$(jq -e '.scripts.lint' package.json &>/dev/null && echo true || echo false)
        has_format=$(jq -e '.scripts.format' package.json &>/dev/null && echo true || echo false)
        has_test=$(jq -e '.scripts.test' package.json &>/dev/null && echo true || echo false)
        has_typecheck=$(jq -e '.scripts.typecheck // .scripts["type-check"]' package.json &>/dev/null && echo true || echo false)
    fi

    # Run format check (Prettier or Biome)
    if [ "$has_format" = "true" ]; then
        echo "Running format check..." >&2
        if $pkg_manager run format --check 2>&1 || $pkg_manager run format 2>&1; then
            results+=("Format: PASSED")
        else
            results+=("Format: FAILED - files need formatting")
            has_errors=true
        fi
    elif command -v prettier &> /dev/null || [ -f "node_modules/.bin/prettier" ]; then
        echo "Running prettier check..." >&2
        local prettier_cmd="prettier"
        [ -f "node_modules/.bin/prettier" ] && prettier_cmd="node_modules/.bin/prettier"
        if $prettier_cmd --check "**/*.{js,jsx,ts,tsx,json,css,md}" 2>&1; then
            results+=("Prettier: PASSED")
        else
            results+=("Prettier: FAILED - files need formatting")
            has_errors=true
        fi
    fi

    # Run linting (ESLint or Biome)
    if [ "$has_lint" = "true" ]; then
        echo "Running lint..." >&2
        if $pkg_manager run lint 2>&1; then
            results+=("Lint: PASSED")
        else
            results+=("Lint: FAILED - linting errors found")
            has_errors=true
        fi
    elif command -v eslint &> /dev/null || [ -f "node_modules/.bin/eslint" ]; then
        echo "Running eslint..." >&2
        local eslint_cmd="eslint"
        [ -f "node_modules/.bin/eslint" ] && eslint_cmd="node_modules/.bin/eslint"
        if $eslint_cmd . --ext .js,.jsx,.ts,.tsx 2>&1; then
            results+=("ESLint: PASSED")
        else
            results+=("ESLint: FAILED - linting errors found")
            has_errors=true
        fi
    fi

    # Run type checking for TypeScript projects
    if [ "$has_typecheck" = "true" ]; then
        echo "Running type check..." >&2
        if $pkg_manager run typecheck 2>&1 || $pkg_manager run type-check 2>&1; then
            results+=("TypeCheck: PASSED")
        else
            results+=("TypeCheck: FAILED - type errors found")
            has_errors=true
        fi
    elif [ -f "tsconfig.json" ]; then
        if command -v tsc &> /dev/null || [ -f "node_modules/.bin/tsc" ]; then
            echo "Running tsc type check..." >&2
            local tsc_cmd="tsc"
            [ -f "node_modules/.bin/tsc" ] && tsc_cmd="node_modules/.bin/tsc"
            if $tsc_cmd --noEmit 2>&1; then
                results+=("TypeScript: PASSED")
            else
                results+=("TypeScript: FAILED - type errors found")
                has_errors=true
            fi
        fi
    fi

    # Run tests (Jest, Vitest, or generic test script)
    if [ "$has_test" = "true" ]; then
        echo "Running tests..." >&2
        if $pkg_manager run test 2>&1; then
            results+=("Tests: PASSED")
        else
            results+=("Tests: FAILED - tests did not pass")
            has_errors=true
        fi
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

# Run checks for detected project types
run_python_checks
run_javascript_checks

# Build output message
if ! $ran_checks; then
    echo '{"continue": true, "systemMessage": "No Python or JavaScript project detected - skipping quality checks"}'
    exit 0
fi

# Format results
result_text=$(printf '%s\n' "${results[@]}")

if $has_errors; then
    # Return with blocking decision to let Claude know there are issues
    cat <<EOF
{
    "decision": "block",
    "reason": "Quality checks failed. Please fix the issues before completing.",
    "systemMessage": "Quality Check Results:\n${result_text}\n\nPlease address the failing checks before completing the task."
}
EOF
    exit 2
else
    cat <<EOF
{
    "decision": "approve",
    "systemMessage": "Quality Check Results:\n${result_text}\n\nAll checks passed!"
}
EOF
    exit 0
fi
