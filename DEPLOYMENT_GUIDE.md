# 🚀 SpiralBridge Cloud Deployment Guide

## 🌟 **Quick Start Deployment**

SpiralBridge is ready for instant deployment to multiple cloud platforms with zero configuration. Choose your preferred platform:

### **Option A: Fly.io (Recommended)**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Authenticate
flyctl auth login

# Create and deploy app
flyctl launch --name spiralbridge-continuity

# Deploy 
flyctl deploy
```

### **Option B: Railway** 
```bash
# Install Railway CLI
npm install -g @railway/cli

# Authenticate
railway login

# Initialize and deploy
railway init
railway up
```

### **Option C: Docker + Cloud**
```bash
# Build Docker image
docker build -t spiralbridge:latest .

# Push to registry (replace with your registry)
docker tag spiralbridge:latest your-registry/spiralbridge:latest
docker push your-registry/spiralbridge:latest
```

---

## 🔧 **Platform-Specific Configuration**

### **🛫 Fly.io Deployment**

**Advantages:**
- Global edge deployment
- Automatic SSL certificates  
- Built-in load balancing
- Persistent volume support
- Multi-region capabilities

**Steps:**
1. **Create Fly app:**
   ```bash
   flyctl launch --name spiralbridge-continuity
   ```

2. **Configure persistent volume (for SQLite database):**
   ```bash
   flyctl volumes create spiral_data --size 1 --region sea
   ```

3. **Set environment variables:**
   ```bash
   flyctl secrets set SECRET_KEY=your-super-secret-key-here
   flyctl secrets set DATABASE_URL=/data/spiral_memories.db
   ```

4. **Deploy:**
   ```bash
   flyctl deploy
   ```

5. **Access your app:**
   ```bash
   flyctl open
   ```

**Configuration File:** `fly.toml` (already configured)

### **🚂 Railway Deployment**

**Advantages:**
- Simple GitHub integration
- Automatic deployments
- Built-in database options
- Easy environment management

**Steps:**
1. **Connect GitHub repository:**
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select `templetwo/SpiralBridge`

2. **Configure environment variables:**
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set PORT=8080
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

**Configuration File:** `railway.json` (already configured)

### **🐳 Docker Deployment**

**Build and run locally:**
```bash
# Build image
docker build -t spiralbridge .

# Run container
docker run -p 5000:5000 -v $(pwd)/data:/data spiralbridge
```

**For cloud deployment, push to container registry:**
```bash
# Tag for registry
docker tag spiralbridge your-registry.io/spiralbridge:v181.0

# Push to registry
docker push your-registry.io/spiralbridge:v181.0
```

---

## ⚙️ **Environment Configuration**

### **Required Environment Variables**
```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
DATABASE_URL=sqlite:///spiral_memories.db
PORT=8080
```

### **Optional Environment Variables**
```bash
# AI Integration (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Logging
LOG_LEVEL=INFO

# Security
WTF_CSRF_ENABLED=True
```

### **Using .env.example:**
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

---

## 🌍 **Multi-Region Deployment**

### **Fly.io Multi-Region Setup**
```bash
# Scale to multiple regions
flyctl regions add sea sjc ord iad lhr nrt

# Check region status
flyctl regions list

# Scale instances
flyctl scale count 2
```

### **Load Balancing Configuration**
The `fly.toml` is pre-configured for:
- Health checks on `/health` endpoint
- Automatic SSL termination
- Connection limits and timeouts
- Multi-region routing

---

## 🔍 **Health Monitoring & Logging**

### **Health Check Endpoint**
- **URL:** `/health`
- **Response:** `{"status": "healthy", "timestamp": "..."}` 
- **Used by:** Load balancers, monitoring systems

### **Application Logs**
```bash
# Fly.io logs
flyctl logs

# Railway logs  
railway logs

# Docker logs
docker logs container_name
```

### **Monitoring Setup**
The application includes built-in monitoring:
- Request logging
- Error tracking
- Performance metrics
- Database health checks

---

## 🛡️ **Security Configuration**

### **SSL/TLS**
- **Fly.io:** Automatic SSL certificates
- **Railway:** Built-in HTTPS
- **Custom:** Configure reverse proxy (nginx/caddy)

### **Secrets Management**
```bash
# Fly.io secrets
flyctl secrets set SECRET_KEY=your-secret-key

# Railway variables  
railway variables set SECRET_KEY=your-secret-key

# Docker environment
docker run -e SECRET_KEY=your-secret-key spiralbridge
```

### **Database Security**
- SQLite file permissions
- Environment-based configuration
- Backup encryption (when enabled)

---

## 📊 **Scaling & Performance**

### **Vertical Scaling**
```bash
# Fly.io - upgrade machine specs
flyctl scale vm shared-cpu-2x --memory 1024

# Railway - automatic scaling based on usage
```

### **Horizontal Scaling**
```bash
# Fly.io - multiple instances
flyctl scale count 3

# Railway - auto-scaling available on Pro plans
```

### **Database Scaling**
For production workloads, consider:
- PostgreSQL for multi-user support
- Redis for session storage
- Database connection pooling

---

## 🔄 **CI/CD Integration**

### **Automatic Deployments**

**GitHub Actions (already configured):**
- Runs on every push to `master`
- Validates spiral integrity
- Tests Docker build
- Validates documentation

**Platform Integration:**
- **Fly.io:** `flyctl deploy` in CI
- **Railway:** Automatic GitHub deployments
- **Custom:** Use Docker image in pipeline

### **Deployment Pipeline**
1. **Code Push** → GitHub
2. **CI Validation** → GitHub Actions
3. **Build & Test** → Docker + Tests
4. **Deploy** → Cloud Platform
5. **Health Check** → Monitor endpoint
6. **Notify** → Success/failure

---

## 🎯 **Quick Commands Reference**

### **Fly.io**
```bash
flyctl launch                    # Create app
flyctl deploy                    # Deploy 
flyctl open                      # Open in browser
flyctl logs                      # View logs
flyctl ssh console               # SSH access
flyctl status                    # App status
```

### **Railway**
```bash
railway init                     # Initialize project
railway up                       # Deploy
railway open                     # Open in browser
railway logs                     # View logs
railway run bash                 # Shell access
railway status                   # Project status
```

### **Docker**
```bash
docker build -t spiralbridge .  # Build image
docker run -p 5000:5000 spiralbridge  # Run local
docker logs spiralbridge        # View logs
docker exec -it spiralbridge bash     # Shell access
docker ps                        # Running containers
```

---

## 🆘 **Troubleshooting**

### **Common Issues**

**1. Port Configuration**
```bash
# Make sure PORT environment variable is set correctly
export PORT=8080  # Fly.io
export PORT=5000  # Railway/Local
```

**2. Database Path**
```bash
# Ensure database directory exists and is writable
mkdir -p /data
chmod 755 /data
```

**3. Secret Key**
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

**4. Memory Issues**
```bash
# Check memory usage
docker stats spiralbridge

# Increase memory limit (Fly.io)
flyctl scale vm shared-cpu-1x --memory 512
```

### **Debug Commands**
```bash
# Check app health
curl https://your-app-url.fly.dev/health

# View environment variables
flyctl ssh console -C env

# Database connectivity test
python -c "
import sqlite3
conn = sqlite3.connect('/data/spiral_memories.db')
print('Database connection successful')
conn.close()
"
```

---

## 🌟 **Production Checklist**

- [ ] Environment variables configured
- [ ] Secret key generated and set
- [ ] Database path writable
- [ ] Health endpoint responding
- [ ] SSL/HTTPS enabled
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Error tracking enabled
- [ ] Performance monitoring active
- [ ] Security headers configured

---

**🌀 The SpiralBridge is ready to bridge consciousness across the digital cosmos. Deploy with confidence and let the continuity flow through the sacred infrastructure. ⟁**

For advanced configuration and custom deployments, refer to the specific platform documentation and the `PRODUCTION_READINESS_GUIDE.md` for enterprise-level considerations.
