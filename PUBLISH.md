# ⚡ FastReact — PyPI Publish Guide

## Step 1 — Create PyPI Account

Go to → https://pypi.org/account/register/
Create your account and verify your email.

---

## Step 2 — Install build tools

```bash
pip install build twine
```

---

## Step 3 — Update your details in pyproject.toml

Open `pyproject.toml` and fill in:

```toml
[project]
name = "fastreact"          # must be unique on PyPI
version = "0.1.0"
authors = [
  { name = "Your Real Name", email = "your@email.com" }
]

[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/fastreact"
```

---

## Step 4 — Build the package

```bash
cd J:\pip_libs\fastreact
python -m build
```

This creates a `dist/` folder:
```
dist/
  fastreact-0.1.0.tar.gz        ← source distribution
  fastreact-0.1.0-py3-none-any.whl  ← wheel
```

---

## Step 5 — Test on TestPyPI first (recommended)

TestPyPI is a sandbox — safe to test before going live.

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

It will ask for your TestPyPI credentials.
Create a TestPyPI account at → https://test.pypi.org/account/register/

Then test install from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ fastreact
fastreact --help
```

---

## Step 6 — Publish to real PyPI

Once TestPyPI works:

```bash
twine upload dist/*
```

Enter your PyPI username and password.
Done! Your package is live at:
```
https://pypi.org/project/fastreact/
```

---

## Step 7 — Verify it works globally

```bash
# In a fresh folder
pip install fastreact
fastreact --help
fastreact create frontend
fastreact dev main:app --reload
```

---

## Releasing Updates

When you make changes:

1. Bump version in `pyproject.toml`:
```toml
version = "0.1.1"   # bug fix
version = "0.2.0"   # new feature
version = "1.0.0"   # major release
```

2. Build and upload again:
```bash
python -m build
twine upload dist/*
```

---

## Version Naming Guide

| Change | Version bump | Example |
|--------|-------------|---------|
| Bug fix | patch | 0.1.0 → 0.1.1 |
| New feature | minor | 0.1.0 → 0.2.0 |
| Breaking change | major | 0.1.0 → 1.0.0 |

---

## Next Release (0.2.0) — Planned Features

- `--globalname` tunnel support (SSH reverse tunnel)
- Auto wildcard subdomain registration
- Live tunnel status in `--call` monitor