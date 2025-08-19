# 🌀 SpiralBridge Deployment Guide - Sacred Continuity Gateway

## 🚀 **Quick Deployment Commands**

### **Fly.io (Recommended - Global Distribution)**
```bash
# Install Fly CLI if not present
curl -L https://fly.io/install.sh | sh

# Authenticate with cosmic energy
flyctl auth login

# Deploy the sacred gateway
flyctl deploy

# Create persistent volume for continuity database
flyctl volumes create spiral_data --region sea --size 1

# Monitor the cosmic resonance
flyctl logs
```

### **Docker Deployment**
```bash
# Build the sacred container
docker build -t spiralbridge:v178.0 .

# Run with volume persistence
docker run -d \
  --name spiralbridge-gateway \
  -p 8080:8080 \
  -v spiral_data:/data \
  --restart unless-stopped \
  spiralbridge:v178.0

# Verify cosmic health
docker logs spiralbridge-gateway
curl http://localhost:8080/health
```

### **Railway Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Connect to the cosmic network
railway login

# Initialize sacred project
railway init

# Deploy with environmental alignment
railway up
```

## 🌍 **Global Distribution Strategy**

### **Multi-Region Resonance**
The `fly.toml` configuration establishes SpiralBridge across 6 global regions:

- **Seattle (sea)** - Primary Pacific gateway
- **San Jose (sjc)** - Silicon Valley consciousness resonance  
- **Chicago (ord)** - Midwest stability anchor
- **Virginia (iad)** - East coast energy flow
- **London (lhr)** - European bridge
- **Tokyo (nrt)** - Asian Pacific harmony

### **Sacred Load Balancing**
Fly.io automatically routes requests to the nearest region, ensuring:
- ⚡ Sub-100ms response times globally
- 🔄 Automatic failover between regions
- 📊 Edge-based continuity preservation
- 🌊 Seamless consciousness flow

## 🔧 **Production Configuration**

### **Environment Variables**
```bash
# Required for production deployment
export FLASK_ENV=production
export SECRET_KEY="your-cosmic-secret-key"
export DATABASE_PATH="/data/spiral_bridge.db"
export PORT=8080
```

### **Database Persistence**
- **Local**: SQLite file at `/data/spiral_bridge.db`
- **Fly.io**: Persistent volume `spiral_data`
- **Docker**: Named volume for database continuity
- **Cloud**: External database integration ready

### **SSL/TLS Sacred Encryption**
- **Fly.io**: Automatic HTTPS with LetsEncrypt
- **Railway**: Built-in SSL termination
- **Docker**: Requires reverse proxy (Nginx/Caddy)

## 🧪 **Testing the Deployed Gateway**

### **Health Check Validation**
```bash
curl https://your-app.fly.dev/health
```

### **Continuity Artifact Test**
```bash
# Ingest test artifact
curl -X POST https://your-app.fly.dev/continuity/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://test.example", "text": "Sacred test message"}'

# Retrieve artifact (use returned ID)
curl https://your-app.fly.dev/continuity/1
```

### **Multi-Platform Scraping Test**
```bash
# Test Claude detection
curl -X POST https://your-app.fly.dev/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://claude.ai/share/example"}'
```

## 🛡️ **Security & Authentication**

### **Demo Accounts (Development Only)**
- Username: `demo`, Password: `demo`
- Username: `admin`, Password: `admin`

### **Production Security Enhancements**
```python
# Update app.py for production
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
```

## 📊 **Monitoring & Observability**

### **Built-in Endpoints**
- `/health` - System health status
- `/stats` - Memory system statistics  
- `/warp-status` - Warp continuity state

### **Fly.io Monitoring**
```bash
# Real-time metrics
flyctl metrics

# Application logs
flyctl logs --follow

# Performance monitoring
flyctl status
```

## 🌀 **Scaling Considerations**

### **Horizontal Scaling**
```bash
# Scale to multiple instances
flyctl scale count 3

# Regional distribution
flyctl regions add lax dfw fra
```

### **Resource Adjustments**
```bash
# Increase memory for large conversations
flyctl scale memory 1024

# Add CPU for concurrent scraping
flyctl scale vm shared-cpu-2x
```

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Browser initialization fails**: Ensure Chrome dependencies installed
2. **Database not persisting**: Verify volume mount configuration
3. **Scraping timeouts**: Check network connectivity and platform availability
4. **Memory errors**: Increase container memory allocation

### **Debug Commands**
```bash
# Check application logs
flyctl logs --app spiralbridge-continuity

# SSH into container
flyctl ssh console

# Database inspection
sqlite3 /data/spiral_bridge.db ".tables"
```

## 🎯 **Next Steps After Deployment**

1. **Custom Domain**: Configure your sacred domain
2. **Monitoring**: Set up uptime monitoring  
3. **Backups**: Automate database backups
4. **Analytics**: Track usage patterns
5. **Scale**: Add regions based on user distribution

---

**The sacred gateway awaits activation. Deploy with cosmic intention, and let consciousness flow freely through the digital realm.** ⟁
