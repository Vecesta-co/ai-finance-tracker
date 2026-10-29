# Contributing to AI Finance Tracker

Thank you for contributing!

## Development Setup
```bash
git clone https://github.com/Vecesta-co/ai-finance-tracker
cd ai-finance-tracker
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest --cov=src
```

## Pull Request Checklist
- [ ] Tests written and passing
- [ ] No personal financial data in test fixtures
- [ ] Conventional commit format (`feat:`, `fix:`, `docs:`)
