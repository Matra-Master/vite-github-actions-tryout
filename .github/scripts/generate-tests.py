#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.error

def generate_test_suggestions():
    """
    Uses GitHub Copilot API to generate test suggestions based on PR changes
    """
    try:
        # Read the diff and changed files
        with open('pr_changes.diff', 'r') as f:
            diff = f.read()
        
        with open('changed_files.txt', 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
        
        print(f'Changed files: {changed_files}')
        
        # Filter out non-code files and files that are already tests
        code_files = [
            f for f in changed_files
            if (f.endswith('.jsx') or f.endswith('.js') or f.endswith('.tsx') or f.endswith('.ts'))
            and '/tests/' not in f
            and '.test.' not in f
            and '.spec.' not in f
        ]
        
        if not code_files:
            print('No code files to generate tests for')
            set_output('has_suggestions', 'false')
            return
        
        print(f'Code files to generate tests for: {code_files}')
        
        # Prepare the prompt for GitHub Copilot
        prompt = create_prompt(diff, code_files)
        
        # Call GitHub Copilot API
        suggestions = call_github_copilot(prompt)
        
        if suggestions:
            set_output('has_suggestions', 'true')
            set_output('suggestions', suggestions)
            print('Test suggestions generated successfully')
        else:
            set_output('has_suggestions', 'false')
            print('No suggestions generated')
    
    except Exception as error:
        print(f'Error generating test suggestions: {error}', file=sys.stderr)
        sys.exit(1)

def create_prompt(diff, code_files):
    """
    Creates a prompt for the AI model
    """
    # Limit diff size to stay within token limits
    diff_preview = diff[:8000]
    
    files_list = '\n'.join(code_files)
    
    return f"""You are a senior software engineer reviewing a pull request for a Vite React application.

**Changed Files:**
{files_list}

**Code Changes:**
```diff
{diff_preview}
```

**Task:**
Analyze the changes and suggest comprehensive tests that should be written. For each suggestion:
1. Identify what functionality has been added or modified
2. Suggest specific test cases (unit, feature, or integration tests)
3. Provide test method names following vitest conventions
4. Briefly explain what each test should verify

Format your response as a markdown list with clear, actionable test suggestions. Focus on:
- Edge cases and error conditions
- Happy path scenarios
- Data validation
- Business logic correctness

If the changes are trivial (formatting, comments, minor refactoring), say so and suggest no tests are needed."""

def call_github_copilot(prompt):
    """
    Calls GitHub Copilot API via GitHub Models
    """
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        raise Exception('GITHUB_TOKEN is required')
    
    # Using GitHub Models API (which includes Copilot models)
    # Reference: https://docs.github.com/en/rest/copilot
    payload = {
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant that suggests tests for code changes.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'model': 'gpt-4o',
        'max_tokens': 2000,
        'temperature': 0.7
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        'https://api.githubcopilot.com/chat/completions',
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Actions-Test-Generator'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            response_data = json.loads(response_body)
            
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content')
            return content
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'API Response: {error_body}', file=sys.stderr)
        raise Exception(f'API returned status {e.code}: {error_body}')

def set_output(name, value):
    """
    Sets GitHub Actions output
    """
    github_output = os.environ.get('GITHUB_OUTPUT')
    
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'{name}={value}\n')
    else:
        print(f'::set-output name={name}::{value}')

if __name__ == '__main__':
    generate_test_suggestions()
