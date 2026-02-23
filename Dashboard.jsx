import React, { useState, useRef, useEffect } from 'react';
import { Upload, TrendingUp, TrendingDown, AlertCircle, CheckCircle, Zap, Brain, FileText, Download, MessageSquare, X, Send, Filter, Calendar, DollarSign, Phone, Users, Target, Activity, BarChart3, PieChart, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart as RechartPie, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

// Main Dashboard Component
export default function SalesIntelligenceDashboard() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [dateRange, setDateRange] = useState('7days');
  const fileInputRef = useRef(null);

  const handleFileUpload = async (uploadedFile) => {
    setLoading(true);
    setFile(uploadedFile);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('campaign_name', 'Sales Campaign');
      formData.append('target_conversion_rate', '0.15');
      formData.append('avg_deal_value', '500');
      
      const response = await fetch('http://localhost:5000/api/sales-intelligence/analyze', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setReport(data);
      
      // Welcome message from AI
      setChatMessages([{
        role: 'assistant',
        content: `I've analyzed ${data.metrics.total_calls} calls from your campaign. Your health score is ${data.health_score.overall}/100. Ask me anything about your data!`
      }]);
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFileUpload(droppedFile);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-xl bg-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Sales Intelligence</h1>
                <p className="text-sm text-gray-400">AI-Powered Campaign Analytics</p>
              </div>
            </div>
            
            {report && (
              <div className="flex items-center gap-3">
                <button className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white flex items-center gap-2 transition-all">
                  <Download className="w-4 h-4" />
                  Export Report
                </button>
                <button 
                  onClick={() => setShowChat(!showChat)}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white flex items-center gap-2 transition-all"
                >
                  <MessageSquare className="w-4 h-4" />
                  AI Assistant
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {!report ? (
          <UploadSection 
            onFileUpload={handleFileUpload}
            onDrop={handleDrop}
            loading={loading}
            fileInputRef={fileInputRef}
          />
        ) : (
          <>
            {/* Health Score & Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <HealthScoreCard score={report.health_score} />
              <MetricCard 
                icon={Phone}
                label="Total Calls"
                value={report.metrics.total_calls.toLocaleString()}
                trend={+5.2}
                color="blue"
              />
              <MetricCard 
                icon={Target}
                label="Conversion Rate"
                value={`${report.metrics.conversion_rate}%`}
                trend={-2.1}
                color="purple"
              />
              <MetricCard 
                icon={DollarSign}
                label="Revenue"
                value={`$${(report.metrics.total_revenue / 1000).toFixed(1)}k`}
                trend={+8.3}
                color="green"
              />
            </div>

            {/* Revenue Leakage Alert */}
            {report.metrics.revenue_leakage > 0 && (
              <RevenueLea kageAlert leakage={report.metrics.revenue_leakage} percentage={report.metrics.revenue_leakage_percentage} />
            )}

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <ChartCard title="Conversion Trends" icon={LineChartIcon}>
                <ConversionTrendChart data={report.conversion_trends} />
              </ChartCard>
              
              <ChartCard title="Health Components" icon={Activity}>
                <HealthRadarChart components={report.health_score.components} />
              </ChartCard>
              
              <ChartCard title="Revenue Leakage Sources" icon={PieChart}>
                <LeakagePieChart data={report.revenue_leakage_breakdown?.by_source || []} />
              </ChartCard>
              
              <ChartCard title="Escalation Breakdown" icon={BarChart3}>
                <EscalationBarChart data={report.escalation_impact?.reasons || []} />
              </ChartCard>
            </div>

            {/* Issues & Recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <IssuesPanel issues={report.issues} />
              <RecommendationsPanel recommendations={report.recommendations} />
            </div>

            {/* AI Chat Assistant */}
            {showChat && (
              <AIChat 
                messages={chatMessages}
                setMessages={setChatMessages}
                report={report}
                onClose={() => setShowChat(false)}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Upload Section Component
function UploadSection({ onFileUpload, onDrop, loading, fileInputRef }) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-3">
          Upload Your Campaign Data
        </h2>
        <p className="text-gray-400 text-lg">
          Get AI-powered insights, revenue leakage analysis, and actionable recommendations
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {[
          { icon: Brain, title: 'AI Analysis', desc: 'LLM-powered insights' },
          { icon: TrendingUp, title: 'Health Scoring', desc: '0-100 campaign health' },
          { icon: Zap, title: 'Real-time', desc: 'Instant analytics' }
        ].map((feature, i) => (
          <div key={i} className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10">
            <feature.icon className="w-8 h-8 text-blue-400 mb-3" />
            <h3 className="text-white font-semibold mb-1">{feature.title}</h3>
            <p className="text-gray-400 text-sm">{feature.desc}</p>
          </div>
        ))}
      </div>

      {/* Upload Area */}
      <div
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
        className="relative group"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={(e) => onFileUpload(e.target.files[0])}
          className="hidden"
        />
        
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="p-16 rounded-2xl backdrop-blur-xl bg-white/5 border-2 border-dashed border-white/20 hover:border-blue-500/50 transition-all cursor-pointer group-hover:bg-white/10"
        >
          {loading ? (
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-white text-lg font-semibold">Analyzing your data...</p>
              <p className="text-gray-400 mt-2">This may take a few moments</p>
            </div>
          ) : (
            <div className="text-center">
              <Upload className="w-16 h-16 text-blue-400 mx-auto mb-4" />
              <h3 className="text-white text-xl font-semibold mb-2">
                Drop your file here or click to browse
              </h3>
              <p className="text-gray-400 mb-4">
                Supports CSV, XLSX, XLS • Max 200MB
              </p>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <CheckCircle className="w-4 h-4" />
                <span>Encrypted & Secure</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sample Format */}
      <div className="mt-6 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
        <p className="text-blue-300 text-sm font-medium mb-2">📋 Expected CSV Format:</p>
        <code className="text-xs text-gray-400 block">
          call_id, timestamp, duration_seconds, status, conversion_value, actual_revenue, sentiment_score
        </code>
      </div>
    </div>
  );
}

// Health Score Card
function HealthScoreCard({ score }) {
  const getColor = (value) => {
    if (value >= 80) return 'from-green-500 to-emerald-600';
    if (value >= 60) return 'from-blue-500 to-cyan-600';
    if (value >= 40) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-pink-600';
  };

  const percentage = (score.overall / 100) * 360;

  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10 relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${getColor(score.overall)} opacity-10`}></div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <span className="text-gray-400 text-sm font-medium">Health Score</span>
          <Activity className="w-5 h-5 text-gray-400" />
        </div>
        
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-4xl font-bold text-white">{score.overall}</span>
          <span className="text-lg text-gray-400">/100</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded text-xs font-semibold ${
            score.overall >= 70 ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'
          }`}>
            {score.status}
          </span>
          {score.trend === 'improving' ? (
            <TrendingUp className="w-4 h-4 text-green-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-400" />
          )}
        </div>

        {/* Mini progress bars for components */}
        <div className="mt-4 space-y-2">
          {Object.entries(score.components).slice(0, 3).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-20 capitalize">{key}</span>
              <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${getColor(value)} transition-all`}
                  style={{ width: `${value}%` }}
                ></div>
              </div>
              <span className="text-xs text-gray-400 w-8 text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Metric Card
function MetricCard({ icon: Icon, label, value, trend, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-600',
    purple: 'from-purple-500 to-pink-600',
    green: 'from-green-500 to-emerald-600',
    orange: 'from-orange-500 to-red-600'
  };

  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10 relative overflow-hidden group hover:bg-white/10 transition-all">
      <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} opacity-10 group-hover:opacity-20 transition-all`}></div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <span className="text-gray-400 text-sm font-medium">{label}</span>
          <Icon className="w-5 h-5 text-gray-400" />
        </div>
        
        <div className="text-3xl font-bold text-white mb-2">{value}</div>
        
        <div className="flex items-center gap-2">
          {trend > 0 ? (
            <>
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-400">+{trend}%</span>
            </>
          ) : (
            <>
              <TrendingDown className="w-4 h-4 text-red-400" />
              <span className="text-sm text-red-400">{trend}%</span>
            </>
          )}
          <span className="text-xs text-gray-500">vs last week</span>
        </div>
      </div>
    </div>
  );
}

// Revenue Leakage Alert
function RevenueLeakageAlert({ leakage, percentage }) {
  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 mb-8">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center flex-shrink-0">
          <AlertCircle className="w-6 h-6 text-orange-400" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-1">
            Revenue Leakage Detected
          </h3>
          <p className="text-gray-300 mb-3">
            You're losing <span className="font-bold text-orange-400">${leakage.toLocaleString()}</span> ({percentage.toFixed(1)}% of potential revenue)
          </p>
          
          <div className="flex gap-3">
            <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-600 text-white text-sm font-semibold hover:from-orange-600 hover:to-red-700 transition-all">
              View Recovery Plan
            </button>
            <button className="px-4 py-2 rounded-lg bg-white/10 text-white text-sm font-semibold hover:bg-white/20 transition-all">
              Analyze Root Cause
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Chart Card Wrapper
function ChartCard({ title, icon: Icon, children }) {
  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <Icon className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  );
}

// Conversion Trend Chart
function ConversionTrendChart({ data }) {
  if (!data || data.length === 0) return <div className="text-gray-500 text-center py-8">No trend data available</div>;
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorConversion" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
        <XAxis dataKey="date" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1e293b', 
            border: '1px solid #334155',
            borderRadius: '8px'
          }}
        />
        <Area 
          type="monotone" 
          dataKey="conversion_rate" 
          stroke="#3b82f6" 
          fillOpacity={1} 
          fill="url(#colorConversion)" 
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// Health Radar Chart
function HealthRadarChart({ components }) {
  const data = Object.entries(components).map(([key, value]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    value: value,
    fullMark: 100
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="#ffffff20" />
        <PolarAngleAxis dataKey="subject" stroke="#9ca3af" />
        <PolarRadiusAxis stroke="#9ca3af" />
        <Radar name="Health" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

// Leakage Pie Chart
function LeakagePieChart({ data }) {
  if (!data || data.length === 0) return <div className="text-gray-500 text-center py-8">No leakage data</div>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartPie>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={(entry) => `${entry.source}: $${(entry.amount/1000).toFixed(1)}k`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="amount"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </RechartPie>
    </ResponsiveContainer>
  );
}

// Escalation Bar Chart
function EscalationBarChart({ data }) {
  if (!data || data.length === 0) return <div className="text-gray-500 text-center py-8">No escalation data</div>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
        <XAxis dataKey="reason" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#1e293b', 
            border: '1px solid #334155',
            borderRadius: '8px'
          }}
        />
        <Bar dataKey="count" fill="#ec4899" />
      </BarChart>
    </ResponsiveContainer>
  );
}

// Issues Panel
function IssuesPanel({ issues }) {
  const severityColors = {
    critical: 'from-red-500 to-pink-600',
    high: 'from-orange-500 to-red-500',
    medium: 'from-yellow-500 to-orange-500',
    low: 'from-blue-500 to-cyan-500'
  };

  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <AlertCircle className="w-5 h-5 text-red-400" />
        <h3 className="text-lg font-semibold text-white">Detected Issues</h3>
        <span className="ml-auto px-2 py-1 rounded-full bg-red-500/20 text-red-300 text-xs font-semibold">
          {issues?.length || 0}
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {issues && issues.length > 0 ? (
          issues.map((issue, i) => (
            <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all group">
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${severityColors[issue.severity]} opacity-20 flex items-center justify-center flex-shrink-0`}>
                  <AlertCircle className="w-5 h-5 text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${
                      issue.severity === 'critical' ? 'bg-red-500/20 text-red-300' :
                      issue.severity === 'high' ? 'bg-orange-500/20 text-orange-300' :
                      'bg-yellow-500/20 text-yellow-300'
                    }`}>
                      {issue.severity}
                    </span>
                    <h4 className="text-white font-semibold">{issue.title}</h4>
                  </div>
                  
                  <p className="text-gray-400 text-sm mb-2">{issue.root_cause}</p>
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>💰 ${issue.revenue_impact.toLocaleString()} impact</span>
                    <span>📞 {issue.affected_calls} calls</span>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500/50" />
            <p>No issues detected - Great job!</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Recommendations Panel
function RecommendationsPanel({ recommendations }) {
  return (
    <div className="p-6 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10">
      <div className="flex items-center gap-3 mb-6">
        <Zap className="w-5 h-5 text-yellow-400" />
        <h3 className="text-lg font-semibold text-white">AI Recommendations</h3>
        <span className="ml-auto px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-300 text-xs font-semibold">
          {recommendations?.length || 0}
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {recommendations && recommendations.length > 0 ? (
          recommendations.slice(0, 5).map((rec, i) => (
            <div key={i} className="p-4 rounded-lg bg-gradient-to-br from-blue-500/5 to-purple-500/5 border border-blue-500/20 hover:border-blue-500/40 transition-all group">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 text-white font-bold text-sm">
                  P{rec.priority}
                </div>
                
                <div className="flex-1">
                  <h4 className="text-white font-semibold mb-2">{rec.action}</h4>
                  <p className="text-gray-400 text-sm mb-3">{rec.expected_impact}</p>
                  
                  <div className="flex items-center gap-4 text-xs">
                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300">
                      +${(rec.expected_revenue_recovery/1000).toFixed(1)}k recovery
                    </span>
                    <span className="text-gray-500">
                      {rec.implementation_effort} effort
                    </span>
                    <span className="text-gray-500">
                      {rec.estimated_time}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Zap className="w-12 h-12 mx-auto mb-2 text-yellow-500/50" />
            <p>No recommendations available</p>
          </div>
        )}
      </div>
    </div>
  );
}

// AI Chat Component
function AIChat({ messages, setMessages, report, onClose }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call Claude API to analyze the question
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': 'YOUR_API_KEY', // User needs to add their key
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 1024,
          messages: [
            {
              role: 'user',
              content: `You are an AI assistant analyzing sales call data. Here's the report data:
              
Health Score: ${report.health_score.overall}/100
Total Calls: ${report.metrics.total_calls}
Conversion Rate: ${report.metrics.conversion_rate}%
Revenue: $${report.metrics.total_revenue}
Revenue Leakage: $${report.metrics.revenue_leakage}

Issues: ${JSON.stringify(report.issues, null, 2)}
Recommendations: ${JSON.stringify(report.recommendations, null, 2)}

User question: ${input}

Provide a clear, actionable answer based on this data.`
            }
          ]
        })
      });

      const data = await response.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.content[0].text
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure your API key is configured.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] rounded-2xl backdrop-blur-2xl bg-slate-900/95 border border-white/20 shadow-2xl flex flex-col z-50">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-semibold">AI Assistant</h3>
            <p className="text-xs text-gray-400">Ask anything about your data</p>
          </div>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white' 
                : 'bg-white/10 text-gray-200'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white/10 p-3 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about your campaign..."
            className="flex-1 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white disabled:opacity-50 hover:from-blue-600 hover:to-purple-700 transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* Suggested Questions */}
        <div className="mt-2 flex flex-wrap gap-2">
          {['What's my biggest issue?', 'How to improve conversion?', 'Revenue recovery plan'].map((q, i) => (
            <button
              key={i}
              onClick={() => setInput(q)}
              className="text-xs px-2 py-1 rounded bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white transition-all"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}