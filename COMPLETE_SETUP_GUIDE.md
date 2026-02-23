# 🚀 Complete Setup Guide - Modern Sales Intelligence Dashboard

## What You're Getting

✅ **Beautiful Modern UI** - Glassmorphism design with animations
✅ **AI-Powered Chat** - Ask questions in natural language  
✅ **Real-time Analytics** - Interactive charts and visualizations
✅ **Smart Recommendations** - AI-generated action items
✅ **Revenue Intelligence** - Track leakage and recovery opportunities
✅ **Health Monitoring** - 0-100 campaign scoring

---

## 📦 Files You Have

```
modern-ui/                          # Frontend (React + Vite)
├── src/
│   ├── Dashboard.jsx              # Main UI component
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md

voice_bot_intelligence/             # Backend (Python + Flask)
├── models.py                       # Data structures
├── intelligence_engine.py          # Core analytics
├── performance_analyzer.py
├── revenue_calculator.py
├── recommendation_engine.py
├── health_scorer.py
├── alert_system.py
├── api_enhanced.py                 # API server ⭐ NEW
└── example_usage.py
```

---

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Setup (Easiest)

**Windows:**
```cmd
# 1. Open Command Prompt in the project folder
cd modern-ui
npm install && npm run dev

# 2. Open NEW Command Prompt
cd voice_bot_intelligence
pip install flask flask-cors pandas openpyxl anthropic
python api_enhanced.py
```

**Mac/Linux:**
```bash
# Run both in parallel
cd modern-ui && npm install && npm run dev &
cd voice_bot_intelligence && pip install flask flask-cors pandas openpyxl anthropic && python api_enhanced.py &
```

### Option 2: Step by Step

**Terminal 1 - Frontend:**
```bash
cd modern-ui

# Install Node packages
npm install

# Start dev server (opens browser automatically)
npm run dev
```

**Terminal 2 - Backend:**
```bash
cd voice_bot_intelligence

# Install Python packages
pip install flask flask-cors pandas openpyxl anthropic

# Start API server
python api_enhanced.py
```

---

## 🎯 Testing the System

### 1. Verify Everything is Running

✅ Frontend: http://localhost:3000
✅ Backend: http://localhost:5000

You should see:
- Frontend: Modern dashboard with upload area
- Backend: Console showing "SALES INTELLIGENCE API SERVER"

### 2. Upload Test Data

Use the sample file from `voice_bot_intelligence/sample_calls.csv` or create your own:

```csv
call_id,campaign_id,timestamp,duration_seconds,status,conversion_value,actual_revenue,sentiment_score
CALL_001,TEST,2025-02-20T09:00:00,240,completed,500,500,0.7
CALL_002,TEST,2025-02-20T10:00:00,120,dropped,500,0,-0.3
CALL_003,TEST,2025-02-20T11:00:00,300,escalated,500,500,0.4
CALL_004,TEST,2025-02-20T12:00:00,180,completed,500,500,0.6
CALL_005,TEST,2025-02-20T13:00:00,90,dropped,500,0,-0.5
```

### 3. Interact with AI

Once data is uploaded:
1. Click "AI Assistant" button (top right)
2. Ask: "What's my biggest issue?"
3. Ask: "How can I improve conversion?"
4. Ask: "Show me revenue recovery plan"

---

## 🔧 Configuration

### Add Your Anthropic API Key (For AI Chat)

1. Get API key from: https://console.anthropic.com/
2. Edit `modern-ui/src/Dashboard.jsx`
3. Find line ~715 (in `sendMessage` function)
4. Replace `'YOUR_API_KEY'` with your actual key:

```javascript
headers: {
  'x-api-key': 'sk-ant-api03-...your-key-here...',  // ← Add here
  // ...
}
```

### Adjust Target Metrics

Edit form data sent to API (in `Dashboard.jsx`):

```javascript
formData.append('target_conversion_rate', '0.20');  // 20% target
formData.append('avg_deal_value', '1000');          // $1000 per deal
```

---

## 📊 Understanding the Dashboard

### Health Score Card
- **80-100** = Excellent (Green)
- **60-79** = Good (Blue)
- **40-59** = Fair (Yellow)
- **0-39** = Critical (Red)

### Metric Cards
- **Total Calls** - Total volume
- **Conversion Rate** - % of successful calls
- **Revenue** - Total generated
- **Trends** - Week-over-week change

### Charts
1. **Conversion Trends** - Daily performance
2. **Health Components** - Radar chart of 5 health metrics
3. **Revenue Leakage** - Where money is lost
4. **Escalations** - Top reasons for agent handoff

### Issues Panel
Shows detected problems with:
- Severity (Critical/High/Medium/Low)
- Root cause explanation
- Revenue impact
- Affected call count

### Recommendations Panel
AI-generated fixes with:
- Priority ranking
- Expected revenue recovery
- Implementation effort
- Time estimate
- Step-by-step guide

---

## 🎨 Customization

### Change Colors

Edit `modern-ui/src/Dashboard.jsx`:

```javascript
// Line ~3 - Update colors array
const COLORS = [
  '#3b82f6',  // Blue
  '#8b5cf6',  // Purple  
  '#ec4899',  // Pink
  '#f59e0b',  // Amber
  '#10b981',  // Green
  '#06b6d4'   // Cyan
];
```

### Modify Health Score Weights

Edit `voice_bot_intelligence/health_scorer.py`:

```python
WEIGHTS = {
    "conversion": 0.35,   # 35% weight
    "revenue": 0.25,      # 25% weight
    "compliance": 0.20,   # 20% weight
    "efficiency": 0.12,   # 12% weight
    "quality": 0.08       # 8% weight
}
```

### Add Custom Metrics

In `api_enhanced.py`, add to the response:

```python
'custom_metrics': {
    'avg_calls_per_day': len(calls) / 7,
    'peak_hour': calculate_peak_hour(calls),
    'best_performing_script': get_best_script(calls)
}
```

---

## 🐛 Troubleshooting

### ❌ "Cannot GET /" in browser
**Problem:** Frontend not running
**Fix:** 
```bash
cd modern-ui
npm install
npm run dev
```

### ❌ "Network Error" when uploading file
**Problem:** Backend not running or CORS issue
**Fix:**
```bash
cd voice_bot_intelligence
python api_enhanced.py

# Verify you see: "SALES INTELLIGENCE API SERVER"
```

### ❌ AI Chat returns error
**Problem:** Missing or invalid API key
**Fix:**
- Get key from https://console.anthropic.com/
- Add to `Dashboard.jsx` line ~715
- Restart frontend

### ❌ Charts not showing
**Problem:** Data format issue
**Fix:**
- Check CSV has required columns: `call_id`, `timestamp`, `status`, `actual_revenue`
- Verify dates are in ISO format: `2025-02-20T09:00:00`
- Ensure `status` is one of: completed, dropped, escalated, failed

### ❌ File upload fails
**Problem:** Missing columns or wrong format
**Fix:**
```csv
# Minimum required columns:
call_id,timestamp,status,actual_revenue,duration_seconds
CALL_001,2025-02-20T09:00:00,completed,500,240
```

---

## 🚀 Going to Production

### Build Frontend

```bash
cd modern-ui
npm run build

# Creates optimized files in /dist
```

### Deploy Options

**1. Vercel (Easiest)**
```bash
npm install -g vercel
vercel
```

**2. Netlify**
```bash
npm run build
# Drag /dist folder to netlify.app
```

**3. Docker**
```dockerfile
# Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

```bash
docker build -t sales-intelligence .
docker run -p 80:80 sales-intelligence
```

---

## 📈 Advanced Features

### Real-time Data Updates

Add WebSocket support in backend:

```python
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('subscribe_campaign')
def handle_subscribe(data):
    # Send live updates
    emit('campaign_update', {'health': 67})
```

### Multi-Campaign Comparison

```javascript
// In Dashboard.jsx
const [campaigns, setCampaigns] = useState([]);

// Upload multiple files
campaigns.forEach(c => {
  // Analyze and compare
});
```

### Export to PDF

```bash
npm install jspdf jspdf-autotable

# In Dashboard.jsx
import jsPDF from 'jspdf';

const exportPDF = () => {
  const doc = new jsPDF();
  doc.text('Sales Intelligence Report', 20, 20);
  // Add charts, metrics, recommendations
  doc.save('report.pdf');
};
```

---

## 📱 Mobile Support

The dashboard is fully responsive! Test on:
- Desktop (optimal)
- Tablet (good)
- Mobile (compact view)

Breakpoints:
- `sm`: 640px
- `md`: 768px  
- `lg`: 1024px
- `xl`: 1280px

---

## 💡 Pro Tips

1. **Use Keyboard Shortcuts**
   - Upload file: Drag & drop or click anywhere
   - Close AI chat: ESC key
   - Refresh data: F5

2. **Best Practices**
   - Upload 100+ calls for accurate analysis
   - Include sentiment scores for better insights
   - Use consistent timestamp format

3. **Performance**
   - Files < 10MB load instantly
   - 10-50MB take ~5 seconds
   - 50-200MB take ~30 seconds

4. **Data Quality**
   - More data = better insights
   - Include escalation reasons
   - Track drop-off stages
   - Add sentiment scores

---

## 🎓 Learning Resources

- **React + Vite**: https://vitejs.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **Recharts**: https://recharts.org/
- **Claude API**: https://docs.anthropic.com/
- **Flask**: https://flask.palletsprojects.com/

---

## ✅ Checklist

Before going live:

- [ ] Frontend runs on http://localhost:3000
- [ ] Backend runs on http://localhost:5000
- [ ] Can upload CSV file successfully
- [ ] See health score and metrics
- [ ] Charts render correctly
- [ ] AI chat works (with API key)
- [ ] Recommendations show up
- [ ] No console errors

---

## 🎉 You're All Set!

**Quick Start Commands:**

```bash
# Terminal 1
cd modern-ui && npm install && npm run dev

# Terminal 2  
cd voice_bot_intelligence && python api_enhanced.py
```

Then:
1. Open http://localhost:3000
2. Upload your CSV
3. Explore the insights!

**Need Help?**
- Check browser console (F12)
- Check backend terminal for errors
- Verify CSV format matches examples
- Ensure all columns are present

---

**Built with ❤️ for sales teams who want data-driven insights**
