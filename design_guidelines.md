{
  "product": {
    "name": "Quantum Wealth & BO Platform",
    "type": "dashboard/trading_terminal",
    "brand_attributes": [
      "institutional",
      "military-grade secure",
      "high-density data",
      "real-time",
      "modular",
      "AI-augmented",
      "zero-playfulness"
    ],
    "north_star": "Bloomberg/TradingView-inspired terminal: dense, fast-scannable, solid dark surfaces, neon micro-accents for AI + live status."
  },

  "design_personality": {
    "style_fusion": [
      "Bloomberg Terminal density (compact tables, strict grids)",
      "TradingView paneling (multi-dock layout + toolbars)",
      "Modern 'glow-border' fintech (subtle cyan/teal edge glows for active focus)"
    ],
    "do_not": [
      "No transparent/glass backgrounds (solid surfaces only)",
      "No playful gradients or colorful hero sections",
      "No purple accents (AI accents must be cyan/teal/lime)",
      "No oversized whitespace typical of marketing sites",
      "No centered app container"
    ]
  },

  "typography": {
    "google_fonts": {
      "primary_ui": {
        "family": "Space Grotesk",
        "weights": ["400", "500", "600", "700"],
        "usage": "Headings, navigation labels, panel titles"
      },
      "data_mono": {
        "family": "IBM Plex Mono",
        "weights": ["400", "500", "600"],
        "usage": "Tables, tickers, prices, timestamps, ISINs"
      }
    },
    "font_application": {
      "body": "Space Grotesk",
      "mono": "IBM Plex Mono",
      "cyrillic_support_note": "Both fonts support Cyrillic; ensure font loading includes subsets if configured."
    },
    "type_scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
      "h2": "text-base md:text-lg font-semibold tracking-tight",
      "panel_title": "text-sm font-semibold tracking-wide",
      "table": "text-[12px] leading-4 font-medium",
      "meta": "text-xs text-muted-foreground",
      "numbers": "font-mono tabular-nums"
    }
  },

  "color_system": {
    "mode": "dark-only",
    "tokens_hsl_for_index_css": {
      "background": "222 22% 6%",
      "foreground": "210 20% 96%",
      "card": "222 20% 9%",
      "card-foreground": "210 20% 96%",
      "popover": "222 20% 9%",
      "popover-foreground": "210 20% 96%",
      "primary": "210 20% 96%",
      "primary-foreground": "222 22% 6%",
      "secondary": "222 16% 14%",
      "secondary-foreground": "210 20% 96%",
      "muted": "222 16% 14%",
      "muted-foreground": "215 12% 70%",
      "accent": "222 16% 14%",
      "accent-foreground": "210 20% 96%",
      "destructive": "0 72% 52%",
      "destructive-foreground": "210 20% 96%",
      "border": "222 14% 18%",
      "input": "222 14% 18%",
      "ring": "188 92% 45%",
      "chart-1": "188 92% 45%",
      "chart-2": "142 72% 45%",
      "chart-3": "0 72% 52%",
      "chart-4": "38 92% 55%",
      "chart-5": "210 12% 70%"
    },
    "semantic_accents": {
      "ai_neon": {
        "name": "Quantum Cyan",
        "hex": "#22D3EE",
        "usage": "AI Insights highlights, active panel border glow, focus rings"
      },
      "buy": {
        "hex": "#22C55E",
        "usage": "Buy signals, positive PnL"
      },
      "sell": {
        "hex": "#EF4444",
        "usage": "Sell signals, negative PnL, risk warnings"
      },
      "warning": {
        "hex": "#F59E0B",
        "usage": "Safeguard warnings, latency warnings"
      },
      "info": {
        "hex": "#60A5FA",
        "usage": "Connection info, neutral system messages"
      }
    },
    "surfaces": {
      "app_bg": "#070A0F",
      "panel_bg": "#0B1220",
      "panel_bg_2": "#0A0F1A",
      "elevated": "#0E172A",
      "border": "#1B2A3A"
    },
    "glow_rules": {
      "default": "No glow by default; glow only for active/focused/selected states.",
      "active_panel_glow_css": "0 0 0 1px rgba(34,211,238,0.35), 0 0 24px rgba(34,211,238,0.10)",
      "danger_glow_css": "0 0 0 1px rgba(239,68,68,0.35), 0 0 24px rgba(239,68,68,0.10)",
      "success_glow_css": "0 0 0 1px rgba(34,197,94,0.35), 0 0 24px rgba(34,197,94,0.10)"
    }
  },

  "layout": {
    "desktop_first": true,
    "grid": {
      "app_shell": "h-screen w-screen grid grid-cols-[72px_1fr]",
      "main": "grid grid-rows-[48px_1fr_32px]",
      "top_bar": "h-12",
      "status_bar": "h-8",
      "content_split": "grid grid-cols-12 gap-3 p-3",
      "panel_spans_example": {
        "portfolio": "col-span-12 xl:col-span-5",
        "news": "col-span-12 xl:col-span-4",
        "ai_insights": "col-span-12 xl:col-span-3",
        "signals": "col-span-12 xl:col-span-7",
        "trades": "col-span-12 xl:col-span-5"
      }
    },
    "panel_chrome": {
      "container": "rounded-lg border bg-card",
      "header": "flex items-center justify-between px-3 py-2 border-b",
      "body": "p-3",
      "dense_body": "p-2"
    },
    "scrolling": {
      "rule": "Panels scroll internally; the app shell should not scroll.",
      "component": "ScrollArea",
      "class": "h-full"
    }
  },

  "components": {
    "shadcn_primary": {
      "navigation": [
        {
          "name": "Sidebar (custom)",
          "use": "Button + Tooltip + Separator",
          "component_path": [
            "/app/frontend/src/components/ui/button.jsx",
            "/app/frontend/src/components/ui/tooltip.jsx",
            "/app/frontend/src/components/ui/separator.jsx"
          ]
        }
      ],
      "panels": [
        {
          "name": "Card",
          "component_path": "/app/frontend/src/components/ui/card.jsx",
          "usage": "All panels use Card with dense header + internal ScrollArea"
        },
        {
          "name": "Resizable",
          "component_path": "/app/frontend/src/components/ui/resizable.jsx",
          "usage": "Optional: allow user to resize Portfolio/News/AI columns"
        },
        {
          "name": "Tabs",
          "component_path": "/app/frontend/src/components/ui/tabs.jsx",
          "usage": "Portfolio: Holdings/Allocation/Performance; AI: Summary/Rules/Errors"
        }
      ],
      "data_display": [
        {
          "name": "Table",
          "component_path": "/app/frontend/src/components/ui/table.jsx",
          "usage": "Bloomberg-style compact tables"
        },
        {
          "name": "Badge",
          "component_path": "/app/frontend/src/components/ui/badge.jsx",
          "usage": "Signal type, market, timeframe, risk level"
        },
        {
          "name": "Progress",
          "component_path": "/app/frontend/src/components/ui/progress.jsx",
          "usage": "Risk meter, model confidence"
        },
        {
          "name": "Skeleton",
          "component_path": "/app/frontend/src/components/ui/skeleton.jsx",
          "usage": "Loading states for live feeds"
        }
      ],
      "forms_modals": [
        {
          "name": "Dialog",
          "component_path": "/app/frontend/src/components/ui/dialog.jsx",
          "usage": "Add Holding modal (ISIN entry + live resolution preview)"
        },
        {
          "name": "AlertDialog",
          "component_path": "/app/frontend/src/components/ui/alert-dialog.jsx",
          "usage": "Destructive confirmations (delete holding, purge memory rule)"
        },
        {
          "name": "Input",
          "component_path": "/app/frontend/src/components/ui/input.jsx",
          "usage": "ISIN, quantity, price, webhook payload search"
        },
        {
          "name": "Select",
          "component_path": "/app/frontend/src/components/ui/select.jsx",
          "usage": "Asset type (stock/bond/fund), board, currency"
        },
        {
          "name": "Textarea",
          "component_path": "/app/frontend/src/components/ui/textarea.jsx",
          "usage": "Trade notes, AI feedback"
        }
      ],
      "feedback": [
        {
          "name": "Sonner Toast",
          "component_path": "/app/frontend/src/components/ui/sonner.jsx",
          "usage": "Trade logged, webhook received, ISIN resolved"
        },
        {
          "name": "Tooltip",
          "component_path": "/app/frontend/src/components/ui/tooltip.jsx",
          "usage": "Explain metrics, safeguards, AI confidence"
        }
      ]
    },
    "icons": {
      "library": "lucide-react",
      "rule": "No emoji icons. Use consistent 1.75px stroke icons.",
      "suggested": [
        "LayoutDashboard",
        "Briefcase",
        "Newspaper",
        "BrainCircuit",
        "Radar",
        "NotebookPen",
        "ShieldAlert",
        "Settings",
        "PlugZap"
      ]
    }
  },

  "tables_bloomberg_style": {
    "density": {
      "row_height": "h-8",
      "cell_padding": "px-2 py-1",
      "font": "text-[12px] font-mono tabular-nums",
      "header": "text-[11px] uppercase tracking-wider text-muted-foreground"
    },
    "row_states": {
      "default": "border-b border-border",
      "hover": "hover:bg-[#0E1A2B]",
      "selected": "bg-[#0B2230] shadow-[0_0_0_1px_rgba(34,211,238,0.35)]"
    },
    "cell_alignment": {
      "numbers": "text-right",
      "tickers": "text-left",
      "status": "text-center"
    },
    "inline_sparkline": {
      "library": "recharts",
      "pattern": "Tiny LineChart in a 64x20 cell; no axes; stroke uses semantic buy/sell color"
    }
  },

  "charts_recharts": {
    "theme": {
      "grid": "rgba(148,163,184,0.12)",
      "axis": "rgba(148,163,184,0.55)",
      "tooltip_bg": "#0B1220",
      "tooltip_border": "#1B2A3A",
      "tooltip_text": "#E5E7EB"
    },
    "recommended": [
      {
        "name": "Portfolio Allocation",
        "type": "PieChart",
        "note": "Use muted palette + one cyan highlight for selected slice"
      },
      {
        "name": "Performance",
        "type": "AreaChart",
        "note": "Solid dark fill with low alpha; no gradients beyond subtle fill alpha"
      },
      {
        "name": "Win/Loss Ratio",
        "type": "BarChart",
        "note": "Green for wins, red for losses; compact bars"
      }
    ]
  },

  "motion_microinteractions": {
    "principles": [
      "Fast, subtle, functional (terminal feel)",
      "No bouncy easing",
      "Prefer opacity/outline/shadow changes over transforms for layout stability"
    ],
    "durations": {
      "hover": "150ms",
      "panel_state": "200ms",
      "toast": "200ms"
    },
    "easing": "cubic-bezier(0.2, 0.8, 0.2, 1)",
    "patterns": {
      "active_panel": "On focus/selection: apply cyan ring + subtle glow shadow",
      "live_dot": "Pulsing dot for websocket/last update",
      "row_hover": "Background tint only (no translate)"
    },
    "css_snippets": {
      "live_pulse": ".q-liveDot{position:relative}.q-liveDot::after{content:'';position:absolute;inset:-2px;border-radius:9999px;background:rgba(34,211,238,.35);filter:blur(0.5px);animation:qPulse 1.6s cubic-bezier(.2,.8,.2,1) infinite}@keyframes qPulse{0%{transform:scale(.9);opacity:.65}70%{transform:scale(1.6);opacity:0}100%{opacity:0}}",
      "focus_ring": ".q-focus:focus-visible{outline:none;box-shadow:0 0 0 2px rgba(34,211,238,.35),0 0 0 6px rgba(34,211,238,.12)}"
    },
    "optional_library": {
      "name": "framer-motion",
      "install": "npm i framer-motion",
      "usage": "Use only for panel entrance (opacity) and tab underline transitions; avoid layout-shifting animations."
    }
  },

  "status_bar": {
    "layout": "fixed bottom-0 left-0 right-0 h-8 border-t bg-[#070A0F]",
    "content": [
      "Connection: WS Online/Offline (pulsing dot)",
      "MOEX last sync time",
      "TradingView webhook last received",
      "Latency ms",
      "User mode: Safe/Live"
    ],
    "tailwind": "flex items-center justify-between px-3 text-xs text-muted-foreground",
    "testids": {
      "connection": "statusbar-connection",
      "last_update": "statusbar-last-update",
      "latency": "statusbar-latency"
    }
  },

  "ai_adaptive_memory_panel": {
    "visual": {
      "rule_cards": "Dense list with severity stripe (left border) + confidence meter",
      "severity_colors": {
        "low": "border-l-[#60A5FA]",
        "medium": "border-l-[#F59E0B]",
        "high": "border-l-[#EF4444]"
      },
      "confidence": "Progress component with cyan fill"
    },
    "interactions": [
      "One-click 'Apply safeguard' button",
      "Inline 'Explain' tooltip",
      "Audit log drawer (Sheet)"
    ],
    "testids": {
      "apply_rule": "adaptive-memory-apply-rule-button",
      "rule_row": "adaptive-memory-rule-row"
    }
  },

  "signal_cards_tradingview_webhook": {
    "card": {
      "layout": "grid grid-cols-[1fr_auto] gap-2",
      "left": "symbol + timeframe + direction badge",
      "right": "Primary action: Log Trade",
      "meta": "payload hash + received time"
    },
    "direction_badges": {
      "buy": "bg-[#052014] text-[#86EFAC] border border-[#14532D]",
      "sell": "bg-[#240A0A] text-[#FCA5A5] border border-[#7F1D1D]"
    },
    "actions": {
      "log_trade": "Button variant=default (solid) with green/red outline depending on direction",
      "view_payload": "Button variant=ghost"
    },
    "testids": {
      "signal_card": "signals-signal-card",
      "log_trade": "signals-log-trade-button",
      "view_payload": "signals-view-payload-button"
    }
  },

  "forms_isin_resolution_modal": {
    "flow": [
      "Open Dialog: Add Holding",
      "Input ISIN (uppercase, monospace)",
      "Live preview card: resolved name (Cyrillic), type, board, currency",
      "Confirm add"
    ],
    "ui": {
      "input_class": "font-mono tracking-wider",
      "preview": "Card with compact key/value rows",
      "error": "Inline Alert (destructive)"
    },
    "testids": {
      "open": "portfolio-add-holding-open-button",
      "isin": "portfolio-add-holding-isin-input",
      "preview": "portfolio-add-holding-resolution-preview",
      "submit": "portfolio-add-holding-submit-button"
    }
  },

  "accessibility": {
    "contrast": "Ensure WCAG AA for text on dark surfaces; avoid low-contrast gray-on-gray.",
    "focus": "Always visible focus ring using cyan ring token; never remove outline without replacement.",
    "reduced_motion": "Respect prefers-reduced-motion: disable pulse + entrance animations.",
    "keyboard": "All sidebar icons, tabs, table rows (if clickable), and dialogs must be keyboard reachable."
  },

  "testing_data_testid_rules": {
    "convention": "kebab-case describing role",
    "must_apply_to": [
      "sidebar nav buttons",
      "topbar search",
      "panel tabs",
      "table row actions",
      "dialogs and submit buttons",
      "signal log buttons",
      "status bar indicators"
    ]
  },

  "images": {
    "usage_rule": "Terminal UI should be mostly vector + data; use images only as subtle backgrounds in non-reading areas.",
    "image_urls": [
      {
        "category": "background_overlay_optional",
        "description": "Very subtle abstract grid texture for top bar or empty states (apply at 6–10% opacity, multiply blend if needed).",
        "url": "https://images.unsplash.com/photo-1657894825744-1da6d5fbf24d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxkYXJrJTIwYWJzdHJhY3QlMjBkYXRhJTIwZ3JpZCUyMGJhY2tncm91bmR8ZW58MHx8fGJsdWV8MTc3NTk4NTkyMHww&ixlib=rb-4.1.0&q=85"
      },
      {
        "category": "background_overlay_optional",
        "description": "Abstract dark tech blur for empty panel placeholder (keep behind a solid overlay).",
        "url": "https://images.unsplash.com/photo-1538153126577-dcd6a3cf614e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwzfHxkYXJrJTIwYWJzdHJhY3QlMjBkYXRhJTIwZ3JpZCUyMGJhY2tncm91bmR8ZW58MHx8fGJsdWV8MTc3NTk4NTkyMHww&ixlib=rb-4.1.0&q=85"
      }
    ]
  },

  "instructions_to_main_agent": {
    "global_css": [
      "Remove CRA demo styles from App.css (logo spin, centered header).",
      "Set dark mode permanently by applying className=\"dark\" on <html> or <body> and remove light tokens usage.",
      "Update :root/.dark tokens in index.css to the provided HSL tokens; keep solid surfaces.",
      "Add font imports in index.html or CSS (Google Fonts): Space Grotesk + IBM Plex Mono."
    ],
    "app_shell_build": [
      "Implement AppShell with: left icon sidebar (72px), top bar (48px), main multi-panel grid, bottom status bar (32px).",
      "Use shadcn Card for each panel; CardHeader dense; CardContent uses ScrollArea.",
      "Use Table component for holdings and trade journal; apply compact density classes.",
      "Use Dialog for Add Holding with ISIN live resolution preview card.",
      "Use Sonner for toasts; ensure every interactive element has data-testid."
    ],
    "recharts": [
      "Apply chart theme colors from tokens; avoid gradients except subtle alpha fills.",
      "Use tabular-nums + mono for numeric axes and tooltips."
    ],
    "i18n": [
      "Ensure UI supports Cyrillic: avoid uppercase transforms on asset names; only uppercase tickers/ISIN.",
      "Use font fallback stack that includes system fonts with Cyrillic support."
    ]
  }
}

---

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
