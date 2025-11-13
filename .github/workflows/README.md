# PR Test Suggestions Action

Generates test suggestions for pull requests using GitHub Copilot API.

## Workflow

1. Triggers on PR events (opened, synchronize, reopened) against configured branches
2. Extracts diff between base and head commits
3. Calls GitHub Copilot API with diff and changed files
4. Posts test suggestions as PR review comment

## Configuration

### Target Branch

Edit `.github/workflows/pr-test-suggestions.yml`:

```yaml
on:
  pull_request:
    branches:
      - main
```

### Authentication

Default `GITHUB_TOKEN` works for public repos. For private repos or Copilot API access:

1. Create token with `contents: read` and `pull-requests: write` permissions
2. Add as repository secret `COPILOT_TOKEN`
3. Update workflow:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.COPILOT_TOKEN }}
```

### Model Selection

Edit `.github/scripts/generate-tests.py`:

```python
'model': 'gpt-4o',  # or 'gpt-4', 'gpt-3.5-turbo'
```

### Using OpenAI API

Replace GitHub Copilot endpoint in `generate-tests.py`:

```python
req = urllib.request.Request(
    'https://api.openai.com/v1/chat/completions',
    data=data,
    headers={
        'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}',
        'Content-Type': 'application/json',
        'User-Agent': 'GitHub-Actions-Test-Generator'
    },
    method='POST'
)
```

Add `OPENAI_API_KEY` as repository secret.

## File Analysis

Includes: `.php`, `.js`, `.ts` files  
Excludes: Files in `/tests/`, files matching `.test.` or `.spec.`  
Diff limit: 8000 characters

## Customization

### File Patterns

Edit filter in `generate-tests.py`:

```python
code_files = [
    f for f in changed_files
    if f.endswith('.php')
    and '/tests/' not in f
]
```

### Prompt

Modify `createPrompt()` function to adjust:
- Testing framework focus
- Test type emphasis
- Project-specific conventions

## Troubleshooting

**No suggestions**: Check PR contains code files, verify diff exists, review action logs  
**Auth errors**: Verify token permissions, check Copilot for Business access  
**Rate limits**: Use dedicated token, implement caching, narrow file patterns
