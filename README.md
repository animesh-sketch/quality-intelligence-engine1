# 🎨 Modern Sales Intelligence Dashboard

**AI-Powered, Beautiful, Feature-Rich Analytics Platform**

![Dashboard Preview](https://via.placeholder.com/1200x600/1e293b/ffffff?text=Sales+Intelligence+Dashboard)

## ✨ Features

### 🎯 Core Features
- ✅ **Glassmorphism UI** - Modern, classy design with blur effects
- ✅ **AI Chat Assistant** - Ask questions about your data in natural language
- ✅ **Real-time Analytics** - Interactive charts and visualizations
- ✅ **Health Scoring** - 0-100 campaign health with component breakdowns
- ✅ **Revenue Leakage Analysis** - Identify where money is being lost
- ✅ **Smart Recommendations** - AI-powered action items with impact estimates
- ✅ **Drag & Drop Upload** - Easy CSV/Excel file uploads
- ✅ **Responsive Design** - Works beautifully on all devices

### 📊 Visualizations
- Line charts for conversion trends
- Radar charts for health components
- Pie charts for revenue leakage breakdown
- Bar charts for escalation analysis
- Real-time metric cards

### 🤖 LLM Integration
- Natural language querying
- Contextual insights
- Automated report generation
- Smart pattern detection

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Python 3.12+ (for backend)
- Anthropic API key (for AI features)

### Step 1: Install Frontend

```bash
cd modern-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

Dashboard will open at `http://localhost:3000`

### Step 2: Start Backend API

```bash
cd ../voice_bot_intelligence

# Install Python dependencies
pip install flask flask-cors pandas openpyxl anthropic

# Start API server
python api_enhanced.py
```

API will run at `http://localhost:5000`

### Step 3: Configure AI Assistant

Edit `src/Dashboard.jsx` and add your Anthropic API key:

```javascript
// Line ~715 in AIChat component
headers: {
  'x-api-key': 'YOUR_ANTHROPIC_API_KEY_HERE',  // Add your key here
  // ...
}
```

Get your API key from: https://console.anthropic.com/

---

## 📁 Project Structure

```
modern-ui/
├── src/
│   ├── Dashboard.jsx       # Main dashboard component
│   ├── App.jsx             # App wrapper
│   ├── main.jsx            # React entry point
│   └── index.css           # Global styles with Tailwind
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── postcss.config.js       # PostCSS configuration
```

---

## 🎨 UI Components

### 1. Upload Section
Beautiful drag-and-drop file upload with progress indicator

```jsx
<UploadSection 
  onFileUpload={handleFileUpload}
  loading={loading}
/>
```

### 2. Health Score Card
Circular progress with component breakdowns

```jsx
<HealthScoreCard score={report.health_score} />
```

### 3. Metric Cards
Animated cards with trends

```jsx
<MetricCard 
  icon={Phone}
  label="Total Calls"
  value={1400}
  trend={+5.2}
  color="blue"
/>
```

### 4. Chart Cards
Interactive Recharts visualizations

```jsx
<ChartCard title="Conversion Trends">
  <ConversionTrendChart data={trends} />
</ChartCard>
```

### 5. AI Chat Assistant
Floating chat widget with Claude integration

```jsx
<AIChat 
  messages={messages}
  report={report}
  onClose={() => setShowChat(false)}
/>
```

---

## 🔌 API Integration

### Upload & Analyze Endpoint

```javascript
POST http://localhost:5000/api/sales-intelligence/analyze

// Form Data:
{
  file: File,                    // CSV or Excel file
  campaign_name: string,         // Optional
  target_conversion_rate: number, // Optional (default: 0.15)
  avg_deal_value: number         // Optional (default: 500)
}

// Response:
{
  success: true,
  health_score: {
    overall: 67,
    status: "Good",
    components: { ... }
  },
  metrics: { ... },
  issues: [ ... ],
  recommendations: [ ... ],
  conversion_trends: [ ... ]
}
```

### AI Chat Endpoint

The AI chat uses Anthropic's Claude API directly from the frontend:

```javascript
POST https://api.anthropic.com/v1/messages

{
  model: "claude-3-5-sonnet-20241022",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "What's my biggest issue?"
    }
  ]
}
```

---

## 🎯 Usage Examples

### Example 1: Basic Analysis

```javascript
// Upload file and get analysis
const result = await uploadAndAnalyze(file);

console.log(`Health Score: ${result.health_score.overall}/100`);
console.log(`Revenue Leakage: $${result.metrics.revenue_leakage}`);
```

### Example 2: AI Chat Queries

```javascript
// Ask AI about specific metrics
"What's causing my low conversion rate?"
"How much revenue can I recover?"
"What should I fix first?"
"Show me trend analysis"
```

### Example 3: Export Reports

```javascript
// Export full report as PDF
const exportReport = () => {
  // Implementation in Dashboard component
  generatePDFReport(report);
};
```

---

## 🎨 Customization

### Change Color Scheme

Edit `src/Dashboard.jsx`:

```javascript
const COLORS = [
  '#3b82f6',  // Blue
  '#8b5cf6',  // Purple
  '#ec4899',  // Pink
  '#f59e0b',  // Orange
  '#10b981',  // Green
  '#06b6d4'   // Cyan
];
```

### Modify Health Score Weights

Edit backend `health_scorer.py`:

```python
WEIGHTS = {
    "conversion": 0.40,  # Increase conversion importance
    "revenue": 0.30,     # Increase revenue importance
    "compliance": 0.15,
    "efficiency": 0.10,
    "quality": 0.05
}
```

### Add Custom Charts

```jsx
<ChartCard title="My Custom Chart">
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={myData}>
      <Bar dataKey="value" fill="#8b5cf6" />
    </BarChart>
  </ResponsiveContainer>
</ChartCard>
```

---

## 📊 Sample Data Format

Your CSV should have these columns:

```csv
call_id,campaign_id,timestamp,duration_seconds,status,conversion_value,actual_revenue,sentiment_score,drop_off_stage,escalation_reason,compliance_flags,script_version
CALL_001,Q1_SALES,2025-02-20T09:15:00,245,completed,500,500,0.7,,,,,v1.0
CALL_002,Q1_SALES,2025-02-20T09:45:00,125,dropped,500,0,-0.3,pitch,,,,v1.0
CALL_003,Q1_SALES,2025-02-20T10:15:00,315,escalated,500,500,0.4,,pricing_question,,v1.0
```

**Required Columns:**
- `call_id` - Unique identifier
- `timestamp` - ISO format datetime
- `duration_seconds` - Call length
- `status` - completed/dropped/escalated/failed
- `actual_revenue` - Revenue generated (0 if no sale)

**Optional Columns:**
- `conversion_value` - Expected value
- `sentiment_score` - -1 to 1
- `drop_off_stage` - Where call dropped
- `escalation_reason` - Why escalated
- `compliance_flags` - Violations

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized build in `/dist`.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --dir=dist --prod
```

### Docker Deployment

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

---

## 🔧 Troubleshooting

### Issue: API Not Connecting

**Solution:**
- Check backend is running on `http://localhost:5000`
- Verify CORS is enabled in `api_enhanced.py`
- Check browser console for errors

### Issue: AI Chat Not Working

**Solution:**
- Add your Anthropic API key in `Dashboard.jsx`
- Verify API key is valid at console.anthropic.com
- Check network tab for API errors

### Issue: Charts Not Rendering

**Solution:**
- Ensure data format matches expected structure
- Check console for Recharts errors
- Verify data is not null/undefined

### Issue: File Upload Fails

**Solution:**
- Check file format (CSV or XLSX)
- Verify file size < 200MB
- Ensure all required columns are present

---

## 📈 Performance Optimization

### 1. Code Splitting

```javascript
// Lazy load heavy components
const AIChat = React.lazy(() => import('./AIChat'));

<Suspense fallback={<Loading />}>
  <AIChat />
</Suspense>
```

### 2. Memoization

```javascript
const MemoizedChart = React.memo(ConversionTrendChart);
```

### 3. Virtual Scrolling

For large datasets, use react-window:

```bash
npm install react-window
```

---

## 🎓 Advanced Features

### Custom AI Prompts

Modify the AI assistant context in `sendMessage()`:

```javascript
const systemPrompt = `You are a sales analytics expert specializing in:
- Revenue optimization
- Conversion rate improvement
- Call quality analysis

Provide actionable insights with specific numbers.`;
```

### Real-time Updates

Add WebSocket support for live data:

```javascript
const ws = new WebSocket('ws://localhost:5000/live');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  setReport(prev => ({ ...prev, ...update }));
};
```

### Multi-Campaign Comparison

```javascript
const [campaigns, setCampaigns] = useState([]);

// Compare multiple campaigns
<CampaignComparison campaigns={campaigns} />
```

---

## 📝 License

MIT License - Feel free to use in your projects!

---

## 🤝 Support

Having issues? Here's how to get help:

1. Check the troubleshooting section above
2. Review console errors in browser dev tools
3. Verify backend API is running
4. Check API key configuration

---

## 🎉 You're Ready!

Run these commands to start:

```bash
# Terminal 1: Frontend
cd modern-ui
npm install
npm run dev

# Terminal 2: Backend  
cd ../voice_bot_intelligence
python api_enhanced.py
```

Then open http://localhost:3000 and upload your data! 🚀
