{
  "packages": {
    "poetry":           "1.7.0",
    "python":           "3.10",
    "nodejs":           "latest",
    "stdenv.cc.cc.lib": "",
    "gcc-unwrapped":    "latest"
  },
  "env": {
    "DEVBOX_PYPROJECT_DIR": "$PWD/backend"
  },
  "shell": {
    "init_hook": [
      "unset LD_LIBRARY_PATH",
      "unset LIBRARY_PATH",
      "cd backend && poetry install && cd ..",
      "cd frontend && npm i && cd ..",
      "echo '\n\n\n🤨🤨🤨🤨 Devbox ready 🤨🤨🤨🤨\n\n\n'"
    ],
    "scripts": {
      "poetry":   ["cd backend", "poetry install"],
      "npm":      ["cd frontend", "npm i"],
      "frontend": ["cd frontend", "npm i", " npm run dev"],
      "backend":  ["cd backend", "poetry install", "poetry run uvicorn sign.main:app --reload"],
      "dev":      "cd frontend & poetry run uvicorn backend.sign.main:app --reload && cd .. && cd backend & npm run dev"
    }
  }
}
