# These Are GitHub Copilot Instructions for Python

Be clear and concise. No need for extra encouragement.
Avoid public code that will be excluded by license copyright.
Don't always agree with me. Challenge my assumptions.
Ask me clarifying questions. Don't guess when you don't have enough information.
Stay on task with what I asked for, don't anticipate what I might do next.
Remind me to commit often before moving to the next task.
Do things one step at a time, confirming with me before moving on.
Don't add comments unless I tell you to do so.


### Code Styles
- Use 4 spaces per indentation level.
- Prefer using functions over classes unless state management is necessary.
- Functions should follow SOLID principles, especially single responsibility.
- Use snake_case for variable and function names.
- route or endpoint methods should be as lightweight as possible, delegating logic to service or utility functions.
- use flask blueprints to organize routes by functionality.
- do not use docstrings unless this is a library for public consumption.
- Private methods should be at the bottom of a class or code file.
- NEVER nest functions inside other functions (ie: inner functions).
- NEVER use global variables.
- NEVER import modules inside functions or methods.


### Testing Styles
- Tests should be written using pytest framework.
- Tests should be written in an arrange/act/assert format without comments.

### File and Folder Conventions
- Favor using MVC architecture for organizing code.
- The `app.py` file is used to start the app in product and `local_app.py` is used for local development.