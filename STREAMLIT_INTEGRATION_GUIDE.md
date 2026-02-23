# 🚀 Integration Guide - Add Sales Intelligence to Your Streamlit App

## ✅ **What You're Getting**

A complete **Sales Intelligence** module that plugs directly into your existing Quality Intelligence Engine Streamlit app at:
https://animesh-sketch-quality-intelligence-engine1-app-tysu0k.streamlit.app

---

## 📁 **Files You Need to Upload**

### **1. Main Module**
- **`streamlit_sales_intelligence.py`** → This is your new page

### **2. Backend Intelligence Engine** (from voice_bot_intelligence folder)
- `models.py`
- `intelligence_engine.py`
- `performance_analyzer.py`
- `revenue_calculator.py`
- `recommendation_engine.py`
- `health_scorer.py`
- `alert_system.py`

---

## 🔧 **Integration Steps**

### **STEP 1: Update Your Repository Structure**

Add these files to your GitHub repo:

```
your-streamlit-app/
├── app.py (your main app)
├── streamlit_sales_intelligence.py ← NEW
├── voice_bot_intelligence/ ← NEW FOLDER
│   ├── __init__.py
│   ├── models.py
│   ├── intelligence_engine.py
│   ├── performance_analyzer.py
│   ├── revenue_calculator.py
│   ├── recommendation_engine.py
│   ├── health_scorer.py
│   └── alert_system.py
├── requirements.txt
└── (your other existing files)
```

---

### **STEP 2: Create Empty __init__.py**

In the `voice_bot_intelligence/` folder, create an empty file called `__init__.py`

This makes it a Python package.

---

### **STEP 3: Update requirements.txt**

Add these lines to your `requirements.txt`:

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
```

---

### **STEP 4: Add to Your App Navigation**

In your main `app.py` file, add this to your sidebar navigation:

```python
import streamlit as st

# Your existing pages
from your_existing_pages import dashboard, audit_sheet, transcript_scanner

# NEW: Import Sales Intelligence
import streamlit_sales_intelligence

st.sidebar.title("Quality Intelligence")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Audit Sheet Analysis", 
        "Transcript Scanner",
        "Agent Scorecards",
        "Voicebot Audit",
        "Sales Intelligence"  # ← NEW PAGE
    ]
)

if page == "Sales Intelligence":
    streamlit_sales_intelligence  # This runs the module
elif page == "Dashboard":
    dashboard()
# ... your other pages
```

---

### **STEP 5: Deploy to Streamlit Cloud**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Sales Intelligence module"
   git push
   ```

2. **Streamlit Cloud will auto-deploy** (if you have auto-deploy enabled)

3. **OR manually redeploy** from Streamlit Cloud dashboard

---

## 🎨 **Design Features**

The module matches your existing **neon-noir** theme:

✅ **Glassmorphism cards** with blur effects  
✅ **Neon cyan (#00f5ff) and magenta (#ff00ff)** accents  
✅ **Dark gradient background**  
✅ **Glowing text effects**  
✅ **Interactive Plotly charts**  
✅ **Responsive layout**

---

## 📊 **Features Included**

### **Upload & Analysis**
- Drag & drop CSV/Excel files
- Automatic data validation
- Real-time processing

### **Visualizations**
- Health score radar chart
- Metric cards with trends
- Progress bars
- Interactive charts

### **Intelligence**
- Issue detection (5 types)
- AI recommendations
- Revenue leakage analysis
- Sentiment tracking
- Conversion analysis

### **Export**
- Download text reports
- Export summary CSV
- Full analysis details

---

## 🧪 **Testing**

### **Test Locally First:**

```bash
cd your-streamlit-app
streamlit run streamlit_sales_intelligence.py
```

Upload the `sample_test_data.csv` file to verify it works.

---

## 📋 **CSV Format Required**

Your users upload CSV files with these columns:

**Required:**
- `call_id` - Unique identifier
- `timestamp` - ISO format (2025-02-20T09:00:00)
- `status` - completed/dropped/escalated/failed
- `actual_revenue` - Dollar amount
- `duration_seconds` - Call length

**Optional:**
- `conversion_value` - Expected revenue
- `sentiment_score` - -1 to 1
- `escalation_reason` - Why escalated
- `campaign_id` - Campaign identifier
- `script_version` - Which script used

---

## 🎯 **User Flow**

1. User clicks "Sales Intelligence" in sidebar
2. Uploads their CSV file
3. Sees loading spinner while analyzing
4. Views beautiful dashboard with:
   - Health score
   - Key metrics
   - Issues detected
   - AI recommendations
5. Downloads reports

---

## 🔧 **Customization Options**

### **Adjust Target Metrics:**

In the sidebar, users can set:
- Target conversion rate (slider)
- Average deal value (input)

These are used to calculate:
- Revenue expectations
- Leakage amounts
- Health scores

### **Color Scheme:**

To change colors, edit the CSS in `streamlit_sales_intelligence.py`:

```python
st.markdown("""
<style>
    /* Change main accent color */
    [data-testid="stMetricValue"] {
        color: #YOUR_COLOR;  /* Change #00f5ff to your color */
    }
</style>
""", unsafe_allow_html=True)
```

---

## 🆘 **Troubleshooting**

### **Issue: Module not found**
**Solution:** Make sure `voice_bot_intelligence/` has `__init__.py` file

### **Issue: Import errors**
**Solution:** Check `requirements.txt` has all dependencies

### **Issue: Page doesn't show**
**Solution:** Verify you added it to sidebar navigation in `app.py`

### **Issue: Charts don't render**
**Solution:** Make sure `plotly>=5.17.0` is in requirements.txt

---

## 📞 **Quick Start Checklist**

- [ ] Copy `streamlit_sales_intelligence.py` to your repo
- [ ] Create `voice_bot_intelligence/` folder
- [ ] Copy all 7 backend modules to that folder
- [ ] Create empty `__init__.py` in voice_bot_intelligence/
- [ ] Update `requirements.txt`
- [ ] Add to sidebar navigation in `app.py`
- [ ] Test locally with `streamlit run`
- [ ] Push to GitHub
- [ ] Deploy on Streamlit Cloud
- [ ] Test with sample data

---

## 🎉 **You're Done!**

Your users can now:
- Upload sales call data
- Get instant AI analysis
- See beautiful visualizations
- Download reports
- Make data-driven decisions

**All integrated into your existing Quality Intelligence Engine!** 🚀
