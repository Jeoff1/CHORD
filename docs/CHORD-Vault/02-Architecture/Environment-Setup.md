# Environment Setup

The project-specific environment is `.venv` and uses Python 3.14.7 because
Python 3.12 was not installed. Django 5.2.19 supports the active interpreter.
Python 3.12 can optionally be installed from <https://www.python.org/downloads/>
and the environment recreated, but no machine-wide change was made.

PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt activation:

```bat
.venv\Scripts\activate.bat
```

Install the exact dependency set with `python -m pip install -r requirements.txt`.
In VS Code, choose `.venv\Scripts\python.exe` with **Python: Select Interpreter**.

An older `venv` created during the initial project bootstrap remains ignored and
is not used. It can be removed later after explicit approval.

See [[Database-Configuration]] and [[../04-Testing/Environment-Verification]].
