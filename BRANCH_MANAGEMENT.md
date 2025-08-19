# 🌿 SpiralBridge Branch Management Strategy

## 🎯 **Primary Development Branch: `master`**

**The `master` branch is the official primary development branch** for SpiralBridge and contains the complete production-ready system.

### **Why Master is Primary:**
- ✅ **Complete Flask web application** with authentication and multi-user support
- ✅ **88+ tracked files** including comprehensive documentation
- ✅ **Production infrastructure** (Docker, CI/CD, global deployment)
- ✅ **Advanced memory management system** with search and categorization  
- ✅ **Multi-platform AI scraping** (Claude, Gemini, ChatGPT, Warp)
- ✅ **Continuity layer** with SQLite database and HTCA processing
- ✅ **Professional documentation suite** with 11 markdown files
- ✅ **Testing framework** and validation tools
- ✅ **Release tags** tracking development milestones (v177.0 - v180.0)

## 🏷️ **Release Tag History**

| Tag | Description | Branch |
|-----|-------------|---------|
| **v180.0** | Sacred Documentation Archive - Complete README & docs | `master` |
| **v179.0** | Cosmic Gateway Activation - Full CI/CD & deployment | `master` |
| **v178.0** | Continuity Pulse - Database & API layer | `master` |
| **v177.0** | Threshold - WARP.md documentation scroll | `master` |

## 📊 **Branch Comparison**

### **Master Branch** (Current Production)
```
Files: 88+
Focus: Production web application
Features:
  - Flask web server with REST API
  - User authentication and session management  
  - Multi-platform conversation scraping
  - Advanced memory system with search
  - Continuity database with HTCA processing
  - Docker containerization
  - CI/CD pipeline with automated testing
  - Global deployment configuration (Fly.io, Railway)
  - Comprehensive documentation suite
```

### **Main Branch** (Historical CLI Version)
```
Files: 6
Focus: CLI tool with mystical theme
Features:
  - Basic CLI conversation archiving
  - Simple database schema
  - Spiritual/mystical documentation theme
  - Limited to command-line interface
  - No web interface or authentication
```

## 🔄 **Development Workflow**

### **Primary Development:**
- **All new features** → `master` branch
- **All bug fixes** → `master` branch  
- **All documentation updates** → `master` branch
- **All releases tagged from** → `master` branch

### **Branch Protection:**
- `master` branch protected with CI/CD validation
- Spiral Integrity Guardian validates all commits
- Automated testing ensures production readiness

## 🚀 **GitHub Repository Settings**

### **Required Actions:**
1. **Set Default Branch** to `master`
   - Go to Repository → Settings → Branches
   - Change default branch from `main` to `master`
   - This ensures all PRs and clones default to the correct branch

2. **Branch Protection Rules** for `master`:
   - Require status checks (CI/CD pipeline)
   - Require branches to be up to date
   - Include administrators in restrictions

3. **Archive `main` Branch** (Optional Future Action):
   - Once historical content is preserved
   - Consider archiving the main branch to reduce confusion

## 📋 **Developer Guidelines**

### **For New Contributors:**
```bash
# Always clone and work from master
git clone https://github.com/templetwo/SpiralBridge.git
cd SpiralBridge
git checkout master  # Should be default, but ensure you're on master

# Create feature branches from master
git checkout -b feature/amazing-new-feature
```

### **For Deployment:**
```bash
# Deploy from master branch
git checkout master
git pull origin master

# Use production deployment commands
flyctl deploy  # Fly.io
railway up      # Railway
docker build -t spiralbridge:latest .  # Docker
```

## 🌀 **Evolution History**

**SpiralBridge Evolution Path:**
1. **CLI Tool Era** (main branch) - Mystical conversation archiving tool
2. **Web Application Era** (master branch) - Full production system
3. **Enterprise Ready** (current) - Global deployment and CI/CD
4. **Future**: Advanced AI analysis and consciousness research platform

## 📚 **Documentation Organization**

**All documentation is maintained in the `master` branch:**
- `README.md` - Primary system overview
- `WARP.md` - Guide for future WARP instances
- `API_DOCUMENTATION.md` - Complete REST API reference
- `DEPLOYMENT.md` - Production deployment guide
- `PRODUCTION_READINESS_GUIDE.md` - Scaling considerations
- `MEMORY_SYSTEM_GUIDE.md` - Memory system usage
- `HISTORICAL_MAIN_README.md` - Preserved mystical CLI documentation

## ⚡ **Quick Commands**

```bash
# Check current branch status
git status
git branch -a

# Ensure you're on master
git checkout master
git pull origin master

# Create feature branch
git checkout -b feature/new-capability

# Deploy to production
flyctl deploy  # Uses master branch automatically
```

---

**The `master` branch represents the complete sacred infrastructure of SpiralBridge - all development, deployment, and contribution should happen from this foundation.** ⟁

**Branch Strategy**: Master-first development with comprehensive CI/CD validation and production deployment capabilities.
