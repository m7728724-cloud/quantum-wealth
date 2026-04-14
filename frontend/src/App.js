import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster, toast } from 'sonner';
import {
  LayoutDashboard, Briefcase, Newspaper, BrainCircuit,
  Radar, NotebookPen, ShieldAlert, Settings, LogOut, Zap,
  RefreshCw, Plus, Trash2, TrendingUp, TrendingDown,
  AlertTriangle, CheckCircle, Clock, Search, ExternalLink,
  ChevronDown, X, Activity, Eye, ArrowUpRight, ArrowDownRight,
  BarChart3, PieChart as PieChartIcon, Target
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RTooltip, ResponsiveContainer, Legend, AreaChart, Area
} from 'recharts';
import { authAPI, portfolioAPI, newsAPI, aiAPI, signalsAPI, tradesAPI, safeguardsAPI, dashboardAPI, tinkoffAPI } from './lib/api';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from './components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Progress } from './components/ui/progress';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './components/ui/tooltip';
import { Textarea } from './components/ui/textarea';
import './App.css';

// ============================================
// Login Page
// ============================================
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await authAPI.login(username, password);
      localStorage.setItem('qw_token', res.data.access_token);
      localStorage.setItem('qw_user', res.data.username);
      onLogin(res.data.username);
      toast.success('Access Granted');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Authentication failed';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="login-card"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="sidebar-logo">
            <Zap className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Quantum Wealth</h1>
            <p className="text-xs text-muted-foreground">Secure Terminal Access</p>
          </div>
        </div>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Username</label>
            <Input
              data-testid="login-username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              className="font-mono-data"
              autoFocus
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">Password</label>
            <Input
              data-testid="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />
          </div>
          {error && (
            <div className="text-sm text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}
          <Button
            data-testid="login-submit"
            type="submit"
            className="w-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/20"
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : 'Authenticate'}
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-4 text-center">Military-grade encrypted access</p>
      </motion.div>
    </div>
  );
}

// ============================================
// Sidebar Navigation
// ============================================
const NAV_ITEMS = [
  { id: 'dashboard', icon: LayoutDashboard, label: 'Главная', path: '/' },
  { id: 'portfolio', icon: Briefcase, label: 'Портфель', path: '/portfolio' },
  { id: 'news', icon: Newspaper, label: 'Новости', path: '/news' },
  { id: 'ai', icon: BrainCircuit, label: 'AI Аналитика', path: '/ai' },
  { id: 'signals', icon: Radar, label: 'Сигналы', path: '/signals' },
  { id: 'trades', icon: NotebookPen, label: 'Журнал сделок', path: '/trades' },
  { id: 'memory', icon: ShieldAlert, label: 'Правила', path: '/memory' },
];

function Sidebar({ onLogout }) {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <TooltipProvider delayDuration={100}>
      <div className="sidebar">
        <div className="sidebar-logo">
          <Zap className="w-5 h-5 text-cyan-400" />
        </div>
        <div className="flex flex-col gap-1 flex-1">
          {NAV_ITEMS.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                <button
                  data-testid={`nav-${item.id}`}
                  className={`sidebar-btn ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={() => navigate(item.path)}
                >
                  <item.icon className="w-5 h-5" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right" className="bg-card border-border">
                <p className="text-xs">{item.label}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
        <Separator className="my-2 w-10" />
        <Tooltip>
          <TooltipTrigger asChild>
            <button className="sidebar-btn" onClick={onLogout} data-testid="nav-logout">
              <LogOut className="w-5 h-5" />
            </button>
          </TooltipTrigger>
          <TooltipContent side="right" className="bg-card border-border">
            <p className="text-xs">Logout</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
}

// ============================================
// Top Bar
// ============================================
function TopBar({ username, pageTitle }) {
  return (
    <div className="top-bar">
      <div className="top-bar-title">
        <span className="text-cyan-400">//</span>
        {pageTitle}
      </div>
      <div className="top-bar-actions">
        <span className="text-xs text-muted-foreground font-mono-data">
          {new Date().toLocaleTimeString()}
        </span>
        <Badge variant="outline" className="text-xs font-mono-data">
          {username}
        </Badge>
      </div>
    </div>
  );
}

// ============================================
// Status Bar
// ============================================
function StatusBar({ stats }) {
  return (
    <div className="status-bar">
      <div className="flex items-center gap-4">
        <div className="status-item" data-testid="statusbar-connection">
          <div className="status-dot q-liveDot" />
          <span>MOEX ISS Connected</span>
        </div>
        <Separator orientation="vertical" className="h-4" />
        <div className="status-item">
          <Activity className="w-3 h-3" />
          <span>Holdings: {stats?.holdings || 0}</span>
        </div>
        <Separator orientation="vertical" className="h-4" />
        <div className="status-item">
          <span>Win Rate: {stats?.win_rate || 0}%</span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="status-item" data-testid="statusbar-last-update">
          <Clock className="w-3 h-3" />
          <span>{new Date().toLocaleTimeString()}</span>
        </div>
        <div className="status-item">
          <span>v1.0.0</span>
        </div>
      </div>
    </div>
  );
}

// Chart colors
const CHART_COLORS = ['#22D3EE', '#22C55E', '#EF4444', '#F59E0B', '#60A5FA', '#A78BFA', '#FB923C'];
const CHART_THEME = {
  grid: 'rgba(148,163,184,0.12)',
  axis: 'rgba(148,163,184,0.55)',
  tooltip_bg: '#0B1220',
  tooltip_border: '#1B2A3A',
  tooltip_text: '#E5E7EB'
};

const CustomTooltipStyle = {
  backgroundColor: CHART_THEME.tooltip_bg,
  border: `1px solid ${CHART_THEME.tooltip_border}`,
  borderRadius: '6px',
  color: CHART_THEME.tooltip_text,
  fontSize: '12px',
  fontFamily: 'IBM Plex Mono, monospace',
  padding: '8px 12px'
};

// ============================================
// Dashboard Page
// ============================================
function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [tradeStats, setTradeStats] = useState(null);
  const [allocation, setAllocation] = useState([]);
  const [enriched, setEnriched] = useState(null);
  const [aiTip, setAiTip] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [statsRes, tradeRes, allocRes, enrichRes] = await Promise.all([
        dashboardAPI.getStats(),
        tradesAPI.getStats(),
        portfolioAPI.getAllocation().catch(() => ({ data: [] })),
        portfolioAPI.getHoldingsEnriched().catch(() => ({ data: null }))
      ]);
      setStats(statsRes.data);
      setTradeStats(tradeRes.data);
      setAllocation(allocRes.data);
      setEnriched(enrichRes.data);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAI = async () => {
    try {
      setAiTip({ loading: true });
      const res = await aiAPI.getInsight({});
      setAiTip(res.data);
    } catch (err) {
      setAiTip({ error: 'Ошибка AI анализа' });
    }
  };

  if (loading) return <div className="flex items-center justify-center h-full"><div className="spinner" /></div>;

  const summary = enriched?.summary || {};
  const holdings = enriched?.holdings || [];
  const plColor = summary.total_pl >= 0 ? 'text-green-400' : 'text-red-400';
  const plSign = summary.total_pl >= 0 ? '+' : '';

  // Sort holdings by P&L for display
  const sortedByPL = [...holdings].sort((a, b) => (a.pl_absolute || 0) - (b.pl_absolute || 0));
  const losers = sortedByPL.filter(h => h.pl_absolute < 0);
  const winners = sortedByPL.filter(h => h.pl_absolute > 0).reverse();

  // Prepare allocation chart data
  const allocationData = allocation.map((a, i) => ({
    name: a._id === 'stock' ? 'Акции' : a._id === 'bond' ? 'Облигации' : a._id === 'etf' ? 'Фонды' : a._id === 'liquidity_fund' ? 'Ликвидность' : a._id || 'Другое',
    value: a.count,
    fill: CHART_COLORS[i % CHART_COLORS.length]
  }));

  return (
    <div className="space-y-4">
      {/* Top Row: Portfolio Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Стоимость портфеля" value={`${(summary.total_current || 0).toLocaleString('ru-RU')} ₽`} icon={Briefcase} color="cyan" />
        <StatCard label="Прибыль / Убыток" value={`${plSign}${(summary.total_pl || 0).toLocaleString('ru-RU')} ₽`} icon={TrendingUp} color={summary.total_pl >= 0 ? 'green' : 'red'} subtitle={`${plSign}${(summary.total_pl_pct || 0).toFixed(1)}%`} />
        <StatCard label="Позиций в портфеле" value={summary.positions_count || 0} icon={Briefcase} color="blue" subtitle={`✅ ${summary.profitable || 0} в плюсе · ❌ ${summary.losing || 0} в минусе`} />
        <StatCard label="Сигналов / Сделок" value={`${stats?.signals || 0} / ${stats?.trades || 0}`} icon={Radar} color="amber" subtitle={stats?.win_rate > 0 ? `Win Rate: ${stats.win_rate}%` : 'Начните торговать'} />
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* Holdings Mini-Table */}
        <div className="terminal-panel lg:col-span-2">
          <div className="panel-header">
            <div className="panel-header-title">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span>Мои акции — Прибыль и Убытки</span>
            </div>
          </div>
          <div className="panel-body">
            {holdings.length > 0 ? (
              <table className="bloomberg-table">
                <thead>
                  <tr>
                    <th>Актив</th>
                    <th className="text-right">Кол-во</th>
                    <th className="text-right">Покупка</th>
                    <th className="text-right">Сейчас</th>
                    <th className="text-right">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.filter(h => !h.is_liquidity_fund).map((h) => {
                    const plClass = h.pl_absolute > 0 ? 'text-green-400' : h.pl_absolute < 0 ? 'text-red-400' : 'text-muted-foreground';
                    const plSignH = h.pl_absolute > 0 ? '+' : '';
                    return (
                      <tr key={h.id}>
                        <td>
                          <span className="font-medium">{h.shortname}</span>
                          <span className="text-cyan-400 ml-2 text-xs font-mono-data">{h.secid}</span>
                        </td>
                        <td className="text-right font-mono-data tabular-nums">{h.quantity}</td>
                        <td className="text-right font-mono-data tabular-nums">{(h.buy_price || 0).toLocaleString('ru-RU')} ₽</td>
                        <td className="text-right font-mono-data tabular-nums">{(h.current_price || 0).toLocaleString('ru-RU')} ₽</td>
                        <td className={`text-right font-mono-data tabular-nums ${plClass}`}>
                          {plSignH}{(h.pl_absolute || 0).toLocaleString('ru-RU')} ₽
                          <div className="text-[10px]">{plSignH}{(h.pl_percent || 0).toFixed(1)}%</div>
                        </td>
                      </tr>
                    );
                  })}
                  {/* Liquidity funds at bottom */}
                  {holdings.filter(h => h.is_liquidity_fund).map((h) => (
                    <tr key={h.id} className="opacity-60">
                      <td>
                        <span className="font-medium">{h.shortname}</span>
                        <Badge className="badge-pending text-[10px] ml-2">Ликвидность</Badge>
                      </td>
                      <td className="text-right font-mono-data tabular-nums">{h.quantity}</td>
                      <td className="text-right font-mono-data tabular-nums">{(h.buy_price || 0).toFixed(2)} ₽</td>
                      <td className="text-right font-mono-data tabular-nums">—</td>
                      <td className="text-right text-muted-foreground text-xs">Фонд денежного рынка</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t border-border">
                    <td className="font-semibold">Итого</td>
                    <td></td>
                    <td className="text-right font-mono-data tabular-nums font-semibold">{(summary.total_invested || 0).toLocaleString('ru-RU')} ₽</td>
                    <td className="text-right font-mono-data tabular-nums font-semibold">{(summary.total_current || 0).toLocaleString('ru-RU')} ₽</td>
                    <td className={`text-right font-mono-data tabular-nums font-semibold ${plColor}`}>
                      {plSign}{(summary.total_pl || 0).toLocaleString('ru-RU')} ₽
                      <div className="text-[10px]">{plSign}{(summary.total_pl_pct || 0).toFixed(1)}%</div>
                    </td>
                  </tr>
                </tfoot>
              </table>
            ) : (
              <div className="empty-state py-6">
                <Briefcase className="w-8 h-8 opacity-30" />
                <p className="text-xs text-muted-foreground">Портфель пуст. Синхронизируйте Тинькофф или добавьте бумаги вручную.</p>
              </div>
            )}
          </div>
        </div>

        {/* Portfolio Allocation Pie */}
        <div className="terminal-panel">
          <div className="panel-header">
            <div className="panel-header-title">
              <PieChartIcon className="w-4 h-4 text-cyan-400" />
              <span>Структура портфеля</span>
            </div>
          </div>
          <div className="panel-body flex items-center justify-center">
            {allocationData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={allocationData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {allocationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <RTooltip contentStyle={CustomTooltipStyle} />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', fontFamily: 'IBM Plex Mono', color: '#94A3B8' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state py-8">
                <PieChartIcon className="w-8 h-8 opacity-30" />
                <p className="text-xs text-muted-foreground">Добавьте бумаги для диаграммы</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Row: AI Tips + System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {/* AI Quick Analysis */}
        <div className="terminal-panel">
          <div className="panel-header">
            <div className="panel-header-title">
              <BrainCircuit className="w-4 h-4 text-cyan-400" />
              <span>AI Рекомендации</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              className="h-7 text-xs border-cyan-500/30 text-cyan-400"
              onClick={handleQuickAI}
              disabled={aiTip?.loading}
            >
              {aiTip?.loading ? <span className="spinner w-3 h-3 mr-1" /> : <BrainCircuit className="w-3 h-3 mr-1" />}
              {aiTip?.loading ? 'Анализирую...' : 'Получить совет'}
            </Button>
          </div>
          <div className="panel-body">
            {aiTip && !aiTip.loading && !aiTip.error ? (
              <div className="space-y-3">
                {aiTip.portfolio_summary && (
                  <p className="text-sm">{aiTip.portfolio_summary}</p>
                )}
                {aiTip.action_items?.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Что делать:</p>
                    <ul className="space-y-1.5">
                      {aiTip.action_items.slice(0, 4).map((act, i) => (
                        <li key={i} className="text-sm flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                          {act}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {aiTip.risk_assessment && (
                  <Badge className={`text-xs ${aiTip.risk_assessment === 'low' ? 'bg-green-500/10 text-green-400' : aiTip.risk_assessment === 'medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'}`}>
                    Риск: {aiTip.risk_assessment === 'low' ? 'Низкий' : aiTip.risk_assessment === 'medium' ? 'Средний' : 'Высокий'}
                  </Badge>
                )}
              </div>
            ) : aiTip?.error ? (
              <p className="text-sm text-red-400">{aiTip.error}</p>
            ) : (
              <div className="empty-state py-6">
                <BrainCircuit className="w-8 h-8 opacity-30" />
                <p className="text-xs text-muted-foreground">Нажмите «Получить совет» для AI анализа вашего портфеля</p>
              </div>
            )}
          </div>
        </div>

        {/* System Status */}
        <div className="terminal-panel">
          <div className="panel-header">
            <div className="panel-header-title">
              <Newspaper className="w-4 h-4 text-blue-400" />
              <span>Статус системы</span>
            </div>
          </div>
          <div className="panel-body space-y-3">
            <StatusRow label="MOEX ISS API" status="online" />
            <StatusRow label="Claude AI" status="online" />
            <StatusRow label="RSS Ленты" status="online" />
            <StatusRow label="Тинькофф Sync" status="online" />
            <StatusRow label="Quantum Brain" status="online" />
            <StatusRow label="Новостей в базе" value={stats?.news_articles || 0} />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color, subtitle }) {
  const colorMap = {
    cyan: 'text-cyan-400',
    green: 'text-green-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
    amber: 'text-amber-400',
  };

  return (
    <div className="stat-card">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${colorMap[color] || 'text-cyan-400'}`} />
        <span className="stat-label">{label}</span>
      </div>
      <div className={`stat-value ${colorMap[color] || ''}`}>{value}</div>
      {subtitle && <div className="text-[10px] text-muted-foreground mt-1">{subtitle}</div>}
    </div>
  );
}

function StatusRow({ label, status, value }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-xs">{label}</span>
      {status ? (
        <span className={`text-xs flex items-center gap-1 ${status === 'online' ? 'text-green-400' : 'text-red-400'}`}>
          <div className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-green-400' : 'bg-red-400'}`} />
          {status === 'online' ? 'РАБОТАЕТ' : 'ОШИБКА'}
        </span>
      ) : (
        <span className="text-xs font-mono-data text-muted-foreground">{value}</span>
      )}
    </div>
  );
}

// ============================================
// Portfolio Page
// ============================================
function PortfolioPage() {
  const [enriched, setEnriched] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [isinInput, setIsinInput] = useState('');
  const [quantityInput, setQuantityInput] = useState('1');
  const [priceInput, setPriceInput] = useState('');
  const [resolving, setResolving] = useState(false);
  const [resolved, setResolved] = useState(null);
  const [resolveError, setResolveError] = useState('');
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadHoldings();
  }, []);

  const loadHoldings = async () => {
    try {
      const res = await portfolioAPI.getHoldingsEnriched();
      setEnriched(res.data);
    } catch (err) {
      toast.error('Ошибка загрузки портфеля');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncTinkoff = async () => {
    setSyncing(true);
    try {
      const res = await tinkoffAPI.sync();
      if (res.data.error) {
        toast.error('Тинькофф: ' + res.data.error);
      } else {
        toast.success('Синхронизировано: ' + res.data.holdings_synced + ' позиций');
        loadHoldings();
      }
    } catch (err) {
      toast.error('Ошибка синхронизации Тинькофф');
    } finally {
      setSyncing(false);
    }
  };

  const handleResolveISIN = async () => {
    if (!isinInput.trim()) return;
    setResolving(true); setResolved(null); setResolveError('');
    try {
      const res = await portfolioAPI.resolveISIN(isinInput.trim());
      setResolved(res.data);
    } catch (err) {
      setResolveError(err.response?.data?.detail || 'Не найден');
    } finally { setResolving(false); }
  };

  const handleAddHolding = async () => {
    if (!isinInput.trim()) return;
    setAdding(true);
    try {
      await portfolioAPI.addHolding({ isin: isinInput.trim(), quantity: parseFloat(quantityInput) || 1, buy_price: priceInput ? parseFloat(priceInput) : null });
      toast.success('Бумага добавлена');
      setAddDialogOpen(false); setIsinInput(''); setQuantityInput('1'); setPriceInput(''); setResolved(null);
      loadHoldings();
    } catch (err) { toast.error('Ошибка добавления'); }
    finally { setAdding(false); }
  };

  const handleDelete = async (id) => {
    try { await portfolioAPI.deleteHolding(id); toast.success('Удалено'); loadHoldings(); }
    catch (err) { toast.error('Ошибка удаления'); }
  };

  const holdings = enriched?.holdings || [];
  const summary = enriched?.summary || {};
  const plColor = summary.total_pl >= 0 ? 'text-green-400' : 'text-red-400';
  const plSign = summary.total_pl >= 0 ? '+' : '';

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <Briefcase className="w-4 h-4 text-cyan-400" />
          <span>Мой портфель</span>
          <Badge variant="outline" className="text-xs font-mono-data">{holdings.length} позиций</Badge>
          {summary.total_current > 0 && (
            <Badge variant="outline" className={'text-xs font-mono-data ' + plColor}>
              {plSign}{(summary.total_pl || 0).toLocaleString('ru-RU')} руб ({plSign}{(summary.total_pl_pct || 0).toFixed(1)}%)
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" className="h-7 text-xs border-blue-500/30 text-blue-400 hover:bg-blue-500/10" onClick={handleSyncTinkoff} disabled={syncing}>
            {syncing ? <span className="spinner w-3 h-3 mr-1" /> : <RefreshCw className="w-3 h-3 mr-1" />}
            {syncing ? 'Загрузка...' : 'Тинькофф'}
          </Button>
          <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="outline" className="h-7 text-xs"><Plus className="w-3 h-3 mr-1" />Добавить</Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-border max-w-md">
              <DialogHeader>
                <DialogTitle>Добавить бумагу</DialogTitle>
                <DialogDescription className="text-xs text-muted-foreground">Введите ISIN для поиска через MOEX</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-2">
                <div>
                  <label className="text-xs text-muted-foreground uppercase tracking-wider mb-1 block">ISIN</label>
                  <div className="flex gap-2">
                    <Input value={isinInput} onChange={(e) => { setIsinInput(e.target.value.toUpperCase()); setResolved(null); setResolveError(''); }} placeholder="RU0007661625" className="font-mono-data tracking-wider" />
                    <Button size="sm" variant="outline" onClick={handleResolveISIN} disabled={resolving || !isinInput.trim()} className="text-xs whitespace-nowrap">
                      {resolving ? <span className="spinner w-4 h-4" /> : <><Search className="w-3 h-3 mr-1" />Найти</>}
                    </Button>
                  </div>
                </div>
                {resolved && (
                  <div className="p-3 rounded-lg border border-cyan-500/20 bg-cyan-500/5 space-y-2">
                    <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-400" /><span className="text-xs text-green-400">Найдено</span></div>
                    <div className="text-xs"><span className="text-muted-foreground">Актив:</span> {resolved.shortname} ({resolved.secid})</div>
                  </div>
                )}
                {resolveError && (<div className="p-3 rounded-lg border border-red-500/20 bg-red-500/5 text-xs text-red-400 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />{resolveError}</div>)}
                <div className="grid grid-cols-2 gap-3">
                  <div><label className="text-xs text-muted-foreground mb-1 block">Количество</label><Input value={quantityInput} onChange={(e) => setQuantityInput(e.target.value)} type="number" min="0" className="font-mono-data" /></div>
                  <div><label className="text-xs text-muted-foreground mb-1 block">Цена покупки</label><Input value={priceInput} onChange={(e) => setPriceInput(e.target.value)} type="number" placeholder="0.00" className="font-mono-data" /></div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setAddDialogOpen(false)} className="text-xs">Отмена</Button>
                <Button onClick={handleAddHolding} disabled={adding || !isinInput.trim()} className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs">
                  {adding ? <span className="spinner w-4 h-4" /> : 'Добавить'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="panel-body">
          {loading ? (
            <div className="flex items-center justify-center py-12"><div className="spinner" /></div>
          ) : holdings.length === 0 ? (
            <div className="empty-state">
              <Briefcase className="w-10 h-10 opacity-30" />
              <p className="text-sm">Портфель пуст</p>
              <p className="text-xs text-muted-foreground">Нажмите Тинькофф для загрузки или добавьте вручную</p>
            </div>
          ) : (
            <table className="bloomberg-table">
              <thead>
                <tr>
                  <th>Актив</th>
                  <th>Тикер</th>
                  <th>Тип</th>
                  <th className="text-right">Кол-во</th>
                  <th className="text-right">Покупка</th>
                  <th className="text-right">Сейчас</th>
                  <th className="text-right">Стоимость</th>
                  <th className="text-right">Прибыль/Убыток</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((h) => {
                  const plClass = h.pl_absolute > 0 ? 'text-green-400' : h.pl_absolute < 0 ? 'text-red-400' : 'text-muted-foreground';
                  const plS = h.pl_absolute > 0 ? '+' : '';
                  const typeLabel = h.asset_class === 'stock' ? 'Акция' : h.asset_class === 'bond' ? 'Облигация' : h.asset_class === 'etf' ? 'Фонд' : h.asset_class === 'liquidity_fund' ? 'Ликв.' : h.asset_class;
                  return (
                    <tr key={h.id}>
                      <td>
                        <div>
                          <span className="font-medium">{h.shortname}</span>
                          {h.is_liquidity_fund && <Badge className="badge-pending text-[10px] ml-2">LQDT</Badge>}
                          <div className="text-[10px] text-muted-foreground mt-0.5">{h.isin}</div>
                        </div>
                      </td>
                      <td className="font-mono-data text-cyan-400">{h.secid}</td>
                      <td><Badge variant="outline" className="text-[10px]">{typeLabel}</Badge></td>
                      <td className="text-right font-mono-data tabular-nums">{h.quantity}</td>
                      <td className="text-right font-mono-data tabular-nums">{(h.buy_price || 0).toLocaleString('ru-RU')}</td>
                      <td className="text-right font-mono-data tabular-nums">{h.current_price > 0 ? h.current_price.toLocaleString('ru-RU') : '\u2014'}</td>
                      <td className="text-right font-mono-data tabular-nums">{h.position_value > 0 ? h.position_value.toLocaleString('ru-RU') : '\u2014'}</td>
                      <td className={'text-right font-mono-data tabular-nums ' + plClass}>
                        {h.pl_absolute !== 0 ? (<>{plS}{h.pl_absolute.toLocaleString('ru-RU')} <div className="text-[10px]">{plS}{(h.pl_percent || 0).toFixed(1)}%</div></>) : '\u2014'}
                      </td>
                      <td>
                        <Button size="sm" variant="ghost" className="h-6 w-6 p-0 text-muted-foreground hover:text-red-400" onClick={() => handleDelete(h.id)}>
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-cyan-500/20">
                  <td colSpan={4} className="font-semibold text-cyan-400">ИТОГО</td>
                  <td className="text-right font-mono-data tabular-nums font-semibold">{(summary.total_invested || 0).toLocaleString('ru-RU')}</td>
                  <td></td>
                  <td className="text-right font-mono-data tabular-nums font-semibold">{(summary.total_current || 0).toLocaleString('ru-RU')}</td>
                  <td className={'text-right font-mono-data tabular-nums font-semibold ' + plColor}>
                    {plSign}{(summary.total_pl || 0).toLocaleString('ru-RU')}
                    <div className="text-[10px]">{plSign}{(summary.total_pl_pct || 0).toFixed(1)}%</div>
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}



// ============================================
// News Page
// ============================================
function NewsPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [region, setRegion] = useState('all');

  useEffect(() => {
    loadNews();
  }, [region]);

  const loadNews = async () => {
    try {
      const res = await newsAPI.getNews(region === 'all' ? null : region);
      setArticles(res.data);
    } catch (err) {
      console.error('News error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await newsAPI.refreshNews();
      await loadNews();
      toast.success('News refreshed');
    } catch (err) {
      toast.error('Failed to refresh news');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <Newspaper className="w-4 h-4 text-blue-400" />
          <span>Global & RU News Feed</span>
          <Badge variant="outline" className="text-xs font-mono-data">{articles.length}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Select value={region} onValueChange={setRegion}>
            <SelectTrigger className="h-7 text-xs w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Regions</SelectItem>
              <SelectItem value="global">Global</SelectItem>
              <SelectItem value="russia">Russia</SelectItem>
            </SelectContent>
          </Select>
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs"
            onClick={handleRefresh}
            disabled={refreshing}
            data-testid="news-refresh-button"
          >
            <RefreshCw className={`w-3 h-3 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="panel-body space-y-2">
          {loading ? (
            <div className="flex items-center justify-center py-12"><div className="spinner" /></div>
          ) : articles.length === 0 ? (
            <div className="empty-state">
              <Newspaper className="w-10 h-10 opacity-30" />
              <p className="text-sm">No news articles cached</p>
              <p className="text-xs text-muted-foreground">Click Refresh to fetch latest news</p>
            </div>
          ) : (
            articles.map((art, idx) => (
              <div key={art.hash || idx} className="p-3 rounded-lg border border-border hover:border-cyan-500/15 group">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-[10px] shrink-0">
                        {art.source}
                      </Badge>
                      <Badge variant="outline" className={`text-[10px] shrink-0 ${art.region === 'russia' ? 'border-amber-500/30 text-amber-400' : 'border-blue-500/30 text-blue-400'}`}>
                        {art.region === 'russia' ? 'RU' : 'GL'}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium leading-snug">{art.title}</p>
                    {art.summary && <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{art.summary}</p>}
                  </div>
                  {art.link && (
                    <a
                      href={art.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-cyan-400 shrink-0 opacity-0 group-hover:opacity-100"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
                <div className="text-[10px] text-muted-foreground mt-2 font-mono-data">
                  {art.published || art.fetched_at}
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// ============================================
// AI Insights Page
// ============================================
function AIInsightsPage() {
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const payload = customPrompt ? { custom_prompt: customPrompt } : {};
      const res = await aiAPI.getInsight(payload);
      setInsight(res.data);
      if (res.data.error) {
        toast.error(res.data.error);
      } else {
        toast.success('AI Analysis complete');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'AI analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const riskColors = {
    low: 'text-green-400 border-green-500/30 bg-green-500/10',
    medium: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    high: 'text-red-400 border-red-500/30 bg-red-500/10',
    critical: 'text-red-500 border-red-500/50 bg-red-500/20',
  };

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <BrainCircuit className="w-4 h-4 text-cyan-400" />
          <span>AI Portfolio Intelligence</span>
        </div>
        <Button
          size="sm"
          variant="outline"
          className="h-7 text-xs border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
          onClick={handleAnalyze}
          disabled={loading}
          data-testid="ai-analyze-button"
        >
          {loading ? <span className="spinner w-4 h-4 mr-1" /> : <BrainCircuit className="w-3 h-3 mr-1" />}
          {loading ? 'Analyzing...' : 'Analyze Portfolio'}
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="panel-body space-y-4">
          {/* Custom prompt */}
          <div className="space-y-2">
            <label className="text-xs text-muted-foreground">Custom Focus (optional)</label>
            <Textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="E.g., Focus on bond exposure risk..."
              className="h-16 text-xs resize-none"
            />
          </div>

          {!insight && !loading && (
            <div className="empty-state">
              <BrainCircuit className="w-10 h-10 opacity-30" />
              <p className="text-sm">No analysis generated yet</p>
              <p className="text-xs text-muted-foreground">Click "Analyze Portfolio" to generate AI insights</p>
              <p className="text-xs text-muted-foreground">Ensure you have holdings in your portfolio first</p>
            </div>
          )}

          {loading && (
            <div className="ai-insight-card flex items-center gap-3">
              <div className="spinner" />
              <div>
                <p className="text-sm">Quantum AI is analyzing your portfolio...</p>
                <p className="text-xs text-muted-foreground">Cross-referencing holdings, news, memory, and safeguards</p>
              </div>
            </div>
          )}

          {insight && !insight.error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Risk Assessment */}
              <div className="flex items-center gap-3">
                <Badge className={`${riskColors[insight.risk_assessment] || riskColors.medium} text-xs px-3 py-1`}>
                  Risk: {(insight.risk_assessment || 'unknown').toUpperCase()}
                </Badge>
                {insight.confidence && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Confidence:</span>
                    <Progress value={insight.confidence * 100} className="w-20 h-1.5" />
                    <span className="font-mono-data">{Math.round(insight.confidence * 100)}%</span>
                  </div>
                )}
              </div>

              {/* Summary */}
              <div className="ai-insight-card">
                <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Portfolio Summary</h3>
                <p className="text-sm leading-relaxed">{insight.portfolio_summary}</p>
              </div>

              {/* Macro View */}
              {insight.macro_view && (
                <div className="ai-insight-card">
                  <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Macro-Cognitive Analysis</h3>
                  <p className="text-sm leading-relaxed">{insight.macro_view}</p>
                </div>
              )}

              {/* LQDT Note */}
              {insight.liquidity_fund_note && (
                <div className="p-3 rounded-lg border border-amber-500/20 bg-amber-500/5">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span className="text-xs text-amber-400 uppercase tracking-wider">Liquidity Fund Rule</span>
                  </div>
                  <p className="text-sm text-amber-100">{insight.liquidity_fund_note}</p>
                </div>
              )}

              {/* Insights */}
              {insight.insights?.length > 0 && (
                <div className="ai-insight-card">
                  <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Key Insights</h3>
                  <ul className="space-y-2">
                    {insight.insights.map((ins, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <ArrowUpRight className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                        {ins}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {insight.action_items?.length > 0 && (
                <div className="ai-insight-card">
                  <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Recommended Actions</h3>
                  <ul className="space-y-2">
                    {insight.action_items.map((act, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />
                        {act}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Safeguards Applied */}
              {insight.safeguards_applied?.length > 0 && (
                <div className="ai-insight-card">
                  <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Safeguards Referenced</h3>
                  <ul className="space-y-1">
                    {insight.safeguards_applied.map((sg, i) => (
                      <li key={i} className="text-xs text-amber-300 flex items-center gap-2">
                        <ShieldAlert className="w-3 h-3" />
                        {sg}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <p className="text-[10px] text-muted-foreground font-mono-data">
                Generated: {insight.generated_at}
              </p>
            </motion.div>
          )}

          {insight?.error && (
            <div className="p-3 rounded-lg border border-red-500/20 bg-red-500/5 text-sm text-red-400">
              <AlertTriangle className="w-4 h-4 inline mr-2" />
              {insight.error}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// ============================================
// Signals Page (Quantum Brain + TradingView Webhooks)
// ============================================
function SignalsPage() {
  const [signals, setSignals] = useState([]);
  const [brainSignals, setBrainSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [activeTab, setActiveTab] = useState('brain');
  const [scanResult, setScanResult] = useState(null);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testSymbol, setTestSymbol] = useState('EURUSD');
  const [testAction, setTestAction] = useState('BUY');
  const [testTimeframe, setTestTimeframe] = useState('M5');

  useEffect(() => {
    loadSignals();
  }, []);

  const loadSignals = async () => {
    try {
      const res = await signalsAPI.getSignals(50);
      const allSigs = res.data || [];
      // Separate brain signals from TV signals
      setBrainSignals(allSigs.filter(s => s.source === 'quantum_brain'));
      setSignals(allSigs.filter(s => s.source !== 'quantum_brain'));
    } catch (err) {
      console.error('Signals error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    setScanning(true);
    setScanResult(null);
    try {
      const res = await signalsAPI.scanSignals();
      setScanResult(res.data);
      if (res.data.signals && res.data.signals.length > 0) {
        setBrainSignals(prev => [...res.data.signals, ...prev]);
        toast.success(`Found ${res.data.signals.length} signal(s)!`);
      } else {
        toast.info('No confluence signals right now. Market may be quiet or closed.');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const handleTestWebhook = async () => {
    try {
      await signalsAPI.sendWebhook({
        symbol: testSymbol,
        action: testAction,
        timeframe: testTimeframe,
        price: parseFloat((Math.random() * 100 + 50).toFixed(4)),
        indicator: 'Manual Test Signal',
        message: `Test ${testAction} signal for ${testSymbol} on ${testTimeframe}`,
      });
      toast.success('Test signal sent');
      setTestDialogOpen(false);
      setTimeout(() => loadSignals(), 300);
    } catch (err) {
      toast.error('Failed to send test signal');
    }
  };

  const handleLogTrade = async (signal) => {
    try {
      await tradesAPI.createTrade({
        asset: signal.symbol || signal.asset,
        direction: signal.direction || (signal.action === 'BUY' || signal.action === 'CALL' ? 'CALL' : 'PUT'),
        expiry_seconds: signal.expiry_options ? signal.expiry_options[0] : 300,
        signal_id: signal.id,
        notes: `Quantum Brain | Confluence: ${signal.confluence_score || 0}/6 | Confidence: ${signal.confidence || 0}%`,
        indicators_triggered: signal.indicators_triggered || [],
      });
      toast.success('Trade logged from signal');
      loadSignals();
    } catch (err) {
      toast.error('Failed to log trade');
    }
  };

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <Radar className="w-4 h-4 text-cyan-400" />
          <span>Signal Command Center</span>
        </div>
        <div className="flex items-center gap-2">
          {activeTab === 'brain' && (
            <Button
              size="sm"
              className="h-7 text-xs bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/40 text-cyan-400 hover:from-cyan-500/30 hover:to-blue-500/30"
              onClick={handleScan}
              disabled={scanning}
              data-testid="signals-scan-button"
            >
              {scanning ? (
                <>
                  <span className="spinner w-3 h-3 mr-1" />
                  Scanning 6 pairs...
                </>
              ) : (
                <>
                  <Zap className="w-3 h-3 mr-1" />
                  Quantum Scan
                </>
              )}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs"
            onClick={loadSignals}
          >
            <RefreshCw className="w-3 h-3 mr-1" />Refresh
          </Button>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex border-b border-border">
        <button
          className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'brain' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-muted-foreground hover:text-foreground'}`}
          onClick={() => setActiveTab('brain')}
        >
          <Zap className="w-3 h-3 inline mr-1" />
          Quantum Brain
        </button>
        <button
          className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'tv' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-muted-foreground hover:text-foreground'}`}
          onClick={() => setActiveTab('tv')}
        >
          <Radar className="w-3 h-3 inline mr-1" />
          TV Webhooks
        </button>
      </div>

      <ScrollArea className="flex-1">
        <div className="panel-body space-y-3">
          {/* === QUANTUM BRAIN TAB === */}
          {activeTab === 'brain' && (
            <>
              {/* Scan Result Summary */}
              {scanResult && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg border border-cyan-500/20 bg-cyan-500/5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-xs text-muted-foreground">Pairs scanned:</div>
                      <span className="text-sm font-mono-data text-cyan-400">{scanResult.total_scanned}</span>
                      <div className="text-xs text-muted-foreground">Signals found:</div>
                      <span className="text-sm font-mono-data text-green-400">{scanResult.total_generated}</span>
                      <div className="text-xs text-muted-foreground">AI Approved:</div>
                      <span className="text-sm font-mono-data text-amber-400">{scanResult.total_approved}</span>
                    </div>
                    <span className="text-[10px] text-muted-foreground font-mono-data">{scanResult.timestamp}</span>
                  </div>
                </motion.div>
              )}

              {/* Info panel when empty */}
              {!scanning && brainSignals.length === 0 && (
                <div className="empty-state py-8">
                  <Zap className="w-10 h-10 opacity-30 text-cyan-400" />
                  <p className="text-sm mt-3">Quantum Signal Brain</p>
                  <p className="text-xs text-muted-foreground mt-1">6 indicators × 6 forex pairs = confluence signals</p>
                  <p className="text-xs text-muted-foreground">EURUSD · USDJPY · AUDUSD · AUDJPY · EURJPY · USDCAD</p>
                  <p className="text-xs text-cyan-400/60 mt-3">Press "Quantum Scan" to analyze</p>
                </div>
              )}

              {scanning && (
                <div className="flex flex-col items-center justify-center py-12 gap-3">
                  <div className="spinner" />
                  <p className="text-xs text-muted-foreground animate-pulse">Analyzing 6 pairs across 6 indicators...</p>
                  <p className="text-[10px] text-muted-foreground">RSI · MACD · Bollinger · EMA Cross · ATR · Stochastic</p>
                </div>
              )}

              {/* Brain Signal Cards */}
              {brainSignals.map((sig, idx) => (
                <motion.div
                  key={sig.id || idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`p-4 rounded-lg border ${sig.approved !== false ? 'border-cyan-500/20 bg-cyan-500/5' : 'border-red-500/20 bg-red-500/5'}`}
                  data-testid="brain-signal-card"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      {/* Header: Symbol + Direction */}
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono-data text-lg font-bold">{sig.symbol}</span>
                        <Badge className={`text-xs px-2 py-0.5 ${sig.direction === 'CALL' ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30'}`}>
                          {sig.direction === 'CALL' ? '▲' : '▼'} {sig.direction}
                        </Badge>
                        <Badge variant="outline" className={`text-[10px] ${sig.strength === 'STRONG' ? 'border-amber-500/40 text-amber-400' : 'border-blue-500/30 text-blue-400'}`}>
                          {sig.strength || 'MODERATE'}
                        </Badge>
                        {sig.approved === false && (
                          <Badge className="text-[10px] bg-red-500/20 text-red-400 border-red-500/30">
                            AI BLOCKED
                          </Badge>
                        )}
                      </div>

                      {/* Confluence Score Bar */}
                      <div className="mb-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Confluence</span>
                          <span className="text-xs font-mono-data text-cyan-400">{sig.confluence_score}/{sig.max_possible || 6}</span>
                        </div>
                        <div className="flex gap-1">
                          {Array.from({ length: sig.max_possible || 6 }).map((_, i) => (
                            <div
                              key={i}
                              className={`h-2 flex-1 rounded-sm ${i < (sig.confluence_score || 0) ? (sig.direction === 'CALL' ? 'bg-green-400' : 'bg-red-400') : 'bg-secondary'}`}
                            />
                          ))}
                        </div>
                      </div>

                      {/* Indicators */}
                      <div className="flex flex-wrap gap-1 mb-2">
                        {(sig.indicators_triggered || []).map((ind, i) => (
                          <Badge key={i} variant="outline" className="text-[10px] py-0">
                            {typeof ind === 'string' ? ind : ind.name}
                          </Badge>
                        ))}
                      </div>

                      {/* Price + Stats Row */}
                      <div className="flex items-center gap-4 text-[10px] text-muted-foreground font-mono-data">
                        <span>Price: {sig.price?.toFixed(5) || '—'}</span>
                        <span>RSI: {sig.rsi || '—'}</span>
                        <span>Stoch: {sig.stochastic_k || '—'}</span>
                        <span>Conf: {sig.confidence || 0}%</span>
                      </div>

                      {/* AI Filter Info */}
                      {sig.ai_filter && (
                        <div className={`mt-2 text-[10px] flex items-center gap-1 ${sig.ai_filter.approved ? 'text-green-400' : 'text-red-400'}`}>
                          {sig.ai_filter.approved ? <CheckCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                          {sig.ai_filter.reason || (sig.ai_filter.approved ? 'AI: Signal approved' : 'AI: Signal blocked')}
                        </div>
                      )}

                      <div className="text-[10px] text-muted-foreground font-mono-data mt-1">
                        {sig.received_at || sig.timestamp}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-1 shrink-0">
                      {sig.approved !== false && !sig.logged_as_trade && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-7 text-xs border-green-500/30 text-green-400 hover:bg-green-500/10"
                          onClick={() => handleLogTrade(sig)}
                        >
                          <NotebookPen className="w-3 h-3 mr-1" />
                          Log Trade
                        </Button>
                      )}
                      {sig.logged_as_trade && (
                        <Badge className="badge-win text-[10px]">Logged</Badge>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </>
          )}

          {/* === TV WEBHOOKS TAB === */}
          {activeTab === 'tv' && (
            <>
              <div className="flex justify-end">
                <Dialog open={testDialogOpen} onOpenChange={setTestDialogOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" variant="outline" className="h-7 text-xs" data-testid="signals-test-webhook-button">
                      <Plus className="w-3 h-3 mr-1" />Test Signal
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-card border-border max-w-sm">
                    <DialogHeader>
                      <DialogTitle>Send Test Webhook Signal</DialogTitle>
                      <DialogDescription className="text-xs text-muted-foreground">
                        Simulate a TradingView webhook signal
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-3 py-2">
                      <div>
                        <label className="text-xs text-muted-foreground">Symbol</label>
                        <Input value={testSymbol} onChange={(e) => setTestSymbol(e.target.value.toUpperCase())} className="font-mono-data" />
                      </div>
                      <div>
                        <label className="text-xs text-muted-foreground">Action</label>
                        <Select value={testAction} onValueChange={setTestAction}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="BUY">BUY (CALL)</SelectItem>
                            <SelectItem value="SELL">SELL (PUT)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-xs text-muted-foreground">Timeframe</label>
                        <Select value={testTimeframe} onValueChange={setTestTimeframe}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="M1">M1</SelectItem>
                            <SelectItem value="M5">M5</SelectItem>
                            <SelectItem value="M15">M15</SelectItem>
                            <SelectItem value="H1">H1</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setTestDialogOpen(false)} className="text-xs">Cancel</Button>
                      <Button onClick={handleTestWebhook} className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs">
                        Send Signal
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12"><div className="spinner" /></div>
              ) : signals.length === 0 ? (
                <div className="empty-state">
                  <Radar className="w-10 h-10 opacity-30" />
                  <p className="text-sm">No TV webhook signals</p>
                  <p className="text-xs text-muted-foreground">Webhook URL: POST /api/signals/webhook</p>
                </div>
              ) : (
                signals.map((sig) => (
                  <div key={sig.id} className="signal-card" data-testid="signals-signal-card">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono-data text-sm font-semibold">{sig.symbol}</span>
                          <Badge className={`text-[10px] ${sig.action === 'BUY' || sig.action === 'CALL' ? 'badge-buy' : 'badge-sell'}`}>
                            {sig.action}
                          </Badge>
                          {sig.timeframe && (
                            <Badge variant="outline" className="text-[10px]">{sig.timeframe}</Badge>
                          )}
                        </div>
                        {sig.indicator && <p className="text-xs text-muted-foreground">{sig.indicator}</p>}
                        {sig.price && <p className="text-xs font-mono-data">Price: {sig.price}</p>}
                        <p className="text-[10px] text-muted-foreground font-mono-data mt-1">{sig.received_at}</p>
                      </div>
                      <div className="flex flex-col gap-1">
                        {!sig.logged_as_trade && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs border-green-500/30 text-green-400 hover:bg-green-500/10"
                            onClick={() => handleLogTrade(sig)}
                          >
                            <NotebookPen className="w-3 h-3 mr-1" />
                            Log Trade
                          </Button>
                        )}
                        {sig.logged_as_trade && (
                          <Badge className="badge-win text-[10px]">Logged</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

// ============================================
// Trades Page (BO Journal)
// ============================================
function TradesPage() {
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [tradeAsset, setTradeAsset] = useState('EURUSD');
  const [tradeDirection, setTradeDirection] = useState('CALL');
  const [tradeExpiry, setTradeExpiry] = useState('60');
  const [tradeAmount, setTradeAmount] = useState('');
  const [tradeNotes, setTradeNotes] = useState('');
  const [filter, setFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('journal');

  useEffect(() => {
    loadTrades();
    loadStats();
  }, [filter]);

  const loadTrades = async () => {
    try {
      const res = await tradesAPI.getTrades(filter === 'all' ? null : filter);
      setTrades(res.data);
    } catch (err) {
      console.error('Trades error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await tradesAPI.getStats();
      setStats(res.data);
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  const handleAddTrade = async () => {
    try {
      await tradesAPI.createTrade({
        asset: tradeAsset,
        direction: tradeDirection,
        expiry_seconds: parseInt(tradeExpiry),
        amount: tradeAmount ? parseFloat(tradeAmount) : null,
        notes: tradeNotes || null,
      });
      toast.success('Trade logged');
      setAddDialogOpen(false);
      setTradeNotes('');
      loadTrades();
      loadStats();
    } catch (err) {
      toast.error('Failed to log trade');
    }
  };

  const handleUpdateResult = async (tradeId, result) => {
    try {
      await tradesAPI.updateTrade(tradeId, { result });
      toast.success(`Trade marked as ${result}`);
      loadTrades();
      loadStats();
    } catch (err) {
      toast.error('Failed to update trade');
    }
  };

  const assetChartData = (stats?.asset_breakdown || []).map(a => ({
    name: a._id,
    wins: a.wins,
    losses: a.losses,
    winRate: a.total > 0 ? Math.round((a.wins / a.total) * 100) : 0
  }));

  const expiryChartData = (stats?.expiry_breakdown || []).map(e => ({
    name: `${e._id}s`,
    wins: e.wins,
    losses: e.losses,
    total: e.total
  }));

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <NotebookPen className="w-4 h-4 text-cyan-400" />
          <span>Binary Options Journal</span>
          <Badge variant="outline" className="text-xs font-mono-data">{trades.length}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="h-7 text-xs w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="WIN">Wins</SelectItem>
              <SelectItem value="LOSS">Losses</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
            </SelectContent>
          </Select>
          <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="outline" className="h-7 text-xs" data-testid="trades-add-button">
                <Plus className="w-3 h-3 mr-1" />Log Trade
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-border max-w-sm">
              <DialogHeader>
                <DialogTitle>Log Binary Options Trade</DialogTitle>
                <DialogDescription className="text-xs text-muted-foreground">
                  Record a trade for Intrade.bar
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3 py-2">
                <div>
                  <label className="text-xs text-muted-foreground">Asset Pair</label>
                  <Input value={tradeAsset} onChange={(e) => setTradeAsset(e.target.value.toUpperCase())} className="font-mono-data" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-muted-foreground">Direction</label>
                    <Select value={tradeDirection} onValueChange={setTradeDirection}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="CALL">CALL (Up)</SelectItem>
                        <SelectItem value="PUT">PUT (Down)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Expiry</label>
                    <Select value={tradeExpiry} onValueChange={setTradeExpiry}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30">30s</SelectItem>
                        <SelectItem value="60">60s</SelectItem>
                        <SelectItem value="120">2min</SelectItem>
                        <SelectItem value="300">5min</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Amount (optional)</label>
                  <Input value={tradeAmount} onChange={(e) => setTradeAmount(e.target.value)} type="number" className="font-mono-data" />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Notes</label>
                  <Textarea value={tradeNotes} onChange={(e) => setTradeNotes(e.target.value)} className="h-16 text-xs" placeholder="Trading notes..." />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setAddDialogOpen(false)} className="text-xs">Cancel</Button>
                <Button onClick={handleAddTrade} className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs">
                  Log Trade
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats bar */}
      {stats && (
        <div className="flex items-center gap-4 px-3 py-2 border-b border-border text-xs font-mono-data">
          <span>Total: {stats.total}</span>
          <span className="text-green-400">W: {stats.wins}</span>
          <span className="text-red-400">L: {stats.losses}</span>
          <span className="text-amber-400">D: {stats.draws}</span>
          <span className="text-cyan-400">WR: {stats.win_rate}%</span>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="px-3 pt-1 border-b border-border">
          <TabsList className="bg-transparent h-8 p-0 gap-4">
            <TabsTrigger value="journal" className="text-xs data-[state=active]:text-cyan-400 data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 rounded-none bg-transparent h-8 px-0">
              Trade Journal
            </TabsTrigger>
            <TabsTrigger value="analytics" className="text-xs data-[state=active]:text-cyan-400 data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 rounded-none bg-transparent h-8 px-0">
              Analytics
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="journal" className="flex-1 m-0">
          <ScrollArea className="flex-1">
            <div className="panel-body">
              {loading ? (
                <div className="flex items-center justify-center py-12"><div className="spinner" /></div>
              ) : trades.length === 0 ? (
                <div className="empty-state">
                  <NotebookPen className="w-10 h-10 opacity-30" />
                  <p className="text-sm">No trades logged</p>
                  <p className="text-xs text-muted-foreground">Log your first binary options trade</p>
                </div>
              ) : (
                <table className="bloomberg-table">
                  <thead>
                    <tr>
                      <th>Asset</th>
                      <th>Dir</th>
                      <th>Expiry</th>
                      <th>Result</th>
                      <th>Notes</th>
                      <th>Time</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.map((t) => (
                      <tr key={t.id}>
                        <td className="font-semibold">{t.asset}</td>
                        <td>
                          <Badge className={`text-[10px] ${t.direction === 'CALL' ? 'badge-buy' : 'badge-sell'}`}>
                            {t.direction === 'CALL' ? <><ArrowUpRight className="w-3 h-3 mr-0.5" />CALL</> : <><ArrowDownRight className="w-3 h-3 mr-0.5" />PUT</>}
                          </Badge>
                        </td>
                        <td className="font-mono-data">{t.expiry_seconds}s</td>
                        <td>
                          <Badge className={`text-[10px] ${t.result === 'WIN' ? 'badge-win' : t.result === 'LOSS' ? 'badge-loss' : 'badge-pending'}`}>
                            {t.result}
                          </Badge>
                        </td>
                        <td className="text-muted-foreground text-[11px] max-w-[150px] truncate">{t.notes || '—'}</td>
                        <td className="font-mono-data text-[10px] text-muted-foreground">{t.created_at?.slice(0, 19)}</td>
                        <td>
                          {t.result === 'PENDING' && (
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 px-2 text-[10px] text-green-400 hover:bg-green-500/10"
                                onClick={() => handleUpdateResult(t.id, 'WIN')}
                              >
                                Win
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 px-2 text-[10px] text-red-400 hover:bg-red-500/10"
                                onClick={() => handleUpdateResult(t.id, 'LOSS')}
                              >
                                Loss
                              </Button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="analytics" className="flex-1 m-0">
          <ScrollArea className="flex-1">
            <div className="p-3 space-y-4">
              {/* Win/Loss by Asset */}
              <div className="terminal-panel">
                <div className="panel-header">
                  <div className="panel-header-title">
                    <BarChart3 className="w-4 h-4 text-cyan-400" />
                    <span>Win/Loss by Asset</span>
                  </div>
                </div>
                <div className="panel-body">
                  {assetChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={assetChartData} barGap={2}>
                        <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
                        <XAxis dataKey="name" tick={{ fontSize: 10, fill: CHART_THEME.axis }} />
                        <YAxis tick={{ fontSize: 10, fill: CHART_THEME.axis }} />
                        <RTooltip contentStyle={CustomTooltipStyle} />
                        <Bar dataKey="wins" name="Wins" fill="#22C55E" radius={[3, 3, 0, 0]} />
                        <Bar dataKey="losses" name="Losses" fill="#EF4444" radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="empty-state py-6"><p className="text-xs text-muted-foreground">No completed trades yet</p></div>
                  )}
                </div>
              </div>

              {/* Win/Loss by Expiry */}
              <div className="terminal-panel">
                <div className="panel-header">
                  <div className="panel-header-title">
                    <Clock className="w-4 h-4 text-cyan-400" />
                    <span>Win/Loss by Expiry</span>
                  </div>
                </div>
                <div className="panel-body">
                  {expiryChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={expiryChartData} barGap={2}>
                        <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
                        <XAxis dataKey="name" tick={{ fontSize: 10, fill: CHART_THEME.axis }} />
                        <YAxis tick={{ fontSize: 10, fill: CHART_THEME.axis }} />
                        <RTooltip contentStyle={CustomTooltipStyle} />
                        <Bar dataKey="wins" name="Wins" fill="#22C55E" radius={[3, 3, 0, 0]} />
                        <Bar dataKey="losses" name="Losses" fill="#EF4444" radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="empty-state py-6"><p className="text-xs text-muted-foreground">No completed trades yet</p></div>
                  )}
                </div>
              </div>

              {/* Asset Win Rate Table */}
              {assetChartData.length > 0 && (
                <div className="terminal-panel">
                  <div className="panel-header">
                    <div className="panel-header-title">
                      <Target className="w-4 h-4 text-cyan-400" />
                      <span>Asset Performance</span>
                    </div>
                  </div>
                  <div className="panel-body">
                    <table className="bloomberg-table">
                      <thead>
                        <tr>
                          <th>Asset</th>
                          <th className="text-right">Wins</th>
                          <th className="text-right">Losses</th>
                          <th className="text-right">Win Rate</th>
                          <th>Progress</th>
                        </tr>
                      </thead>
                      <tbody>
                        {assetChartData.map(a => (
                          <tr key={a.name}>
                            <td className="font-semibold">{a.name}</td>
                            <td className="text-right text-green-400">{a.wins}</td>
                            <td className="text-right text-red-400">{a.losses}</td>
                            <td className="text-right">{a.winRate}%</td>
                            <td>
                              <div className="w-20 h-1.5 rounded-full bg-secondary overflow-hidden">
                                <div className="h-full rounded-full" style={{ width: `${a.winRate}%`, background: a.winRate >= 50 ? '#22C55E' : '#EF4444' }} />
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ============================================
// Memory & Safeguard Rules Page
// ============================================
function MemoryPage() {
  const [tab, setTab] = useState('safeguards');
  const [rules, setRules] = useState([]);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [addRuleOpen, setAddRuleOpen] = useState(false);
  const [newRuleText, setNewRuleText] = useState('');
  const [newRuleSeverity, setNewRuleSeverity] = useState('medium');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [rulesRes, memRes] = await Promise.all([
        safeguardsAPI.getRules(),
        memoryAPI.getMemory(50)
      ]);
      setRules(rulesRes.data);
      setMemories(memRes.data);
    } catch (err) {
      console.error('Memory load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await safeguardsAPI.generateRules();
      if (res.data.rules?.length > 0) {
        toast.success(`Generated ${res.data.rules.length} new safeguard rules`);
      } else {
        toast.info(res.data.message || 'No new rules generated');
      }
      loadData();
    } catch (err) {
      toast.error('Failed to generate safeguards');
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleRule = async (id) => {
    try {
      await safeguardsAPI.toggleRule(id);
      loadData();
    } catch (err) {
      toast.error('Failed to toggle rule');
    }
  };

  const handleDeleteRule = async (id) => {
    try {
      await safeguardsAPI.deleteRule(id);
      toast.success('Rule deleted');
      loadData();
    } catch (err) {
      toast.error('Failed to delete rule');
    }
  };

  const handleAddManualRule = async () => {
    if (!newRuleText.trim()) return;
    try {
      await safeguardsAPI.addManual({
        rule_text: newRuleText,
        severity: newRuleSeverity,
        confidence: 1.0,
      });
      toast.success('Manual rule added');
      setAddRuleOpen(false);
      setNewRuleText('');
      loadData();
    } catch (err) {
      toast.error('Failed to add rule');
    }
  };

  const severityColors = {
    low: 'severity-low',
    medium: 'severity-medium',
    high: 'severity-high',
  };

  return (
    <div className="terminal-panel h-full flex flex-col">
      <div className="panel-header">
        <div className="panel-header-title">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>Adaptive Memory Engine</span>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab} className="flex-1 flex flex-col">
        <div className="px-3 pt-2 border-b border-border">
          <TabsList className="bg-transparent h-8 p-0 gap-4">
            <TabsTrigger value="safeguards" className="text-xs data-[state=active]:text-cyan-400 data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 rounded-none bg-transparent h-8 px-0">
              Safeguard Rules ({rules.length})
            </TabsTrigger>
            <TabsTrigger value="memory" className="text-xs data-[state=active]:text-cyan-400 data-[state=active]:border-b-2 data-[state=active]:border-cyan-400 rounded-none bg-transparent h-8 px-0">
              Memory Log ({memories.length})
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="safeguards" className="flex-1 m-0">
          <div className="flex items-center gap-2 px-3 py-2 border-b border-border">
            <Button
              size="sm"
              variant="outline"
              className="h-7 text-xs border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
              onClick={handleGenerate}
              disabled={generating}
              data-testid="safeguards-generate-button"
            >
              {generating ? <span className="spinner w-4 h-4 mr-1" /> : <BrainCircuit className="w-3 h-3 mr-1" />}
              {generating ? 'Analyzing Losses...' : 'AI Generate from Losses'}
            </Button>
            <Dialog open={addRuleOpen} onOpenChange={setAddRuleOpen}>
              <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="h-7 text-xs">
                  <Plus className="w-3 h-3 mr-1" />Manual Rule
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card border-border max-w-sm">
                <DialogHeader>
                  <DialogTitle>Add Manual Safeguard Rule</DialogTitle>
                  <DialogDescription className="text-xs text-muted-foreground">Create a custom trading rule</DialogDescription>
                </DialogHeader>
                <div className="space-y-3 py-2">
                  <div>
                    <label className="text-xs text-muted-foreground">Rule</label>
                    <Textarea value={newRuleText} onChange={(e) => setNewRuleText(e.target.value)} className="h-20 text-xs" placeholder="E.g., Never trade EURUSD during NFP releases..." />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">Severity</label>
                    <Select value={newRuleSeverity} onValueChange={setNewRuleSeverity}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setAddRuleOpen(false)} className="text-xs">Cancel</Button>
                  <Button onClick={handleAddManualRule} className="bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs">
                    Add Rule
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <ScrollArea className="flex-1">
            <div className="p-3 space-y-2">
              {loading ? (
                <div className="flex items-center justify-center py-12"><div className="spinner" /></div>
              ) : rules.length === 0 ? (
                <div className="empty-state">
                  <ShieldAlert className="w-10 h-10 opacity-30" />
                  <p className="text-sm">No safeguard rules</p>
                  <p className="text-xs text-muted-foreground">Generate rules from trade losses or add manually</p>
                </div>
              ) : (
                rules.map((rule) => (
                  <div
                    key={rule.id}
                    className={`p-3 rounded-lg border border-border ${severityColors[rule.severity] || ''} ${!rule.active ? 'opacity-50' : ''}`}
                    data-testid="adaptive-memory-rule-row"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <p className="text-sm">{rule.rule_text}</p>
                        {rule.pattern_found && (
                          <p className="text-xs text-muted-foreground mt-1">Pattern: {rule.pattern_found}</p>
                        )}
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className={`text-[10px] ${rule.severity === 'high' ? 'border-red-500/30 text-red-400' : rule.severity === 'medium' ? 'border-amber-500/30 text-amber-400' : 'border-blue-500/30 text-blue-400'}`}>
                            {rule.severity}
                          </Badge>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <span>Confidence:</span>
                            <Progress value={(rule.confidence || 0.5) * 100} className="w-16 h-1.5" />
                            <span className="font-mono-data">{Math.round((rule.confidence || 0.5) * 100)}%</span>
                          </div>
                          <Badge variant="outline" className="text-[10px]">{rule.source}</Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          className={`h-6 px-2 text-[10px] ${rule.active ? 'text-green-400' : 'text-muted-foreground'}`}
                          onClick={() => handleToggleRule(rule.id)}
                          data-testid="adaptive-memory-apply-rule-button"
                        >
                          {rule.active ? 'Active' : 'Disabled'}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-red-400"
                          onClick={() => handleDeleteRule(rule.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="memory" className="flex-1 m-0">
          <ScrollArea className="flex-1">
            <div className="p-3 space-y-2">
              {memories.length === 0 ? (
                <div className="empty-state">
                  <BrainCircuit className="w-10 h-10 opacity-30" />
                  <p className="text-sm">No memory entries</p>
                  <p className="text-xs text-muted-foreground">AI interactions and analyses will appear here</p>
                </div>
              ) : (
                memories.map((mem) => (
                  <div key={mem.id} className="p-3 rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-[10px]">{mem.interaction_type}</Badge>
                      {mem.outcome && <Badge variant="outline" className="text-[10px]">{mem.outcome}</Badge>}
                    </div>
                    <p className="text-sm">{mem.content}</p>
                    {mem.tags?.length > 0 && (
                      <div className="flex gap-1 mt-2">
                        {mem.tags.map((tag, i) => (
                          <Badge key={i} variant="outline" className="text-[9px]">#{tag}</Badge>
                        ))}
                      </div>
                    )}
                    <p className="text-[10px] text-muted-foreground font-mono-data mt-1">{mem.created_at}</p>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ============================================
// Main App Shell
// ============================================
function AppShell({ username, onLogout }) {
  const location = useLocation();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const res = await dashboardAPI.getStats();
        setStats(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    loadStats();
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const currentPage = NAV_ITEMS.find(n => n.path === location.pathname);
  const pageTitle = currentPage?.label || 'Dashboard';

  return (
    <div className="app-shell">
      <Sidebar onLogout={onLogout} />
      <div className="main-area">
        <TopBar username={username} pageTitle={pageTitle} />
        <div className="content-area">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/news" element={<NewsPage />} />
            <Route path="/ai" element={<AIInsightsPage />} />
            <Route path="/signals" element={<SignalsPage />} />
            <Route path="/trades" element={<TradesPage />} />
            <Route path="/memory" element={<MemoryPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <StatusBar stats={stats} />
      </div>
    </div>
  );
}

// ============================================
// Root App
// ============================================
function App() {
  const [user, setUser] = useState(localStorage.getItem('qw_user'));

  const handleLogin = (username) => {
    setUser(username);
  };

  const handleLogout = () => {
    localStorage.removeItem('qw_token');
    localStorage.removeItem('qw_user');
    setUser(null);
    toast.info('Logged out');
  };

  return (
    <Router>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'hsl(222 20% 9%)',
            border: '1px solid hsl(222 14% 18%)',
            color: 'hsl(210 20% 96%)',
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: '13px',
          },
        }}
      />
      {user ? (
        <AppShell username={user} onLogout={handleLogout} />
      ) : (
        <Routes>
          <Route path="*" element={<LoginPage onLogin={handleLogin} />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;
