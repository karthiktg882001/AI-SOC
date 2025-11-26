# IDE Setup Guide

This project is **IDE-agnostic** and works with any IDE or text editor. Below are setup instructions for popular IDEs.

## ✅ Universal Compatibility

All code in this project uses standard technologies:
- **Python 3.11+** (FastAPI, SQLAlchemy)
- **JavaScript/React** (ES6+, React 18+)
- **Docker & Docker Compose**
- **Standard file formats** (JSON, YAML, SQL)

## 🛠️ IDE-Specific Setup

### Visual Studio Code (Recommended)

1. **Install Extensions:**
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - ESLint (dbaeumer.vscode-eslint)
   - Prettier (esbenp.prettier-vscode)
   - Docker (ms-azuretools.vscode-docker)

2. **Open Workspace:**
   ```bash
   code .
   ```

3. **VS Code will auto-detect:**
   - Python interpreter
   - Node.js version
   - Docker containers

4. **Debugging:**
   - Use `.vscode/launch.json` for debug configurations
   - Press `F5` to start debugging

### PyCharm / IntelliJ IDEA

1. **Open Project:**
   - File → Open → Select project folder

2. **Configure Python:**
   - File → Settings → Project → Python Interpreter
   - Select Python 3.11+ interpreter

3. **Configure Docker:**
   - Settings → Build, Execution, Deployment → Docker
   - Connect to Docker Desktop

4. **Run Configurations:**
   - Create run configuration for `ml-service/main.py`
   - Use uvicorn: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### Sublime Text

1. **Install Packages:**
   - Package Control → Install Package
   - Install: `LSP`, `LSP-pylsp`, `Dockerfile`

2. **Configure:**
   - Tools → Build System → New Build System
   - Create build for Python and Docker

### Vim/Neovim

1. **Install Plugins:**
   - Use vim-plug or your plugin manager
   - Recommended: `coc.nvim`, `vim-python-pep8-indent`

2. **Language Servers:**
   - Install: `coc-python`, `coc-json`, `coc-yaml`

## 📁 Project Structure

```
AISOC/
├── ml-service/          # Python FastAPI backend
│   ├── routers/         # API routes
│   ├── services/        # Business logic
│   └── main.py         # Entry point
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── contexts/   # React contexts
│   └── package.json
├── docker-compose.yml   # Docker orchestration
└── .vscode/            # VS Code settings (optional)
```

## 🚀 Quick Start (Any IDE)

1. **Clone/Open Project:**
   ```bash
   cd AISOC
   ```

2. **Start Services:**
   ```bash
   docker compose up -d
   ```

3. **Access Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 IDE Features You Can Use

### Code Navigation
- **Go to Definition** (F12)
- **Find References** (Shift+F12)
- **Symbol Search** (Ctrl+Shift+O)

### Debugging
- Set breakpoints in Python/JavaScript
- Step through code
- Inspect variables
- View call stack

### Code Formatting
- **Python**: Black formatter
- **JavaScript**: Prettier
- **Auto-format on save** (if configured)

### IntelliSense/Autocomplete
- Works for Python, JavaScript, JSON, YAML
- Type hints and documentation

## 📝 Language-Specific Notes

### Python
- Uses type hints where possible
- Follows PEP 8 style guide
- Virtual environment recommended (but Docker handles this)

### JavaScript/React
- ES6+ syntax
- React Hooks
- Functional components
- PropTypes (optional)

### Docker
- Multi-stage builds
- Docker Compose for orchestration
- Environment variables for configuration

## 🐛 Troubleshooting

### Python Import Errors
- Ensure Python 3.11+ is installed
- Or use Docker (recommended)

### JavaScript Errors
- Run `npm install` in `frontend/` directory
- Or use Docker (recommended)

### Docker Issues
- Ensure Docker Desktop is running
- Check `docker compose ps` for service status

## 💡 Tips

1. **Use Docker** - Simplifies environment setup
2. **Enable Auto-save** - For faster development
3. **Use Git** - Track changes and collaborate
4. **Install Linters** - Catch errors early
5. **Use Debugger** - Step through code to understand flow

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Note:** This project is designed to work with any IDE. The `.vscode/` folder is optional and only provides VS Code-specific configurations. Other IDEs will work perfectly fine without it.

