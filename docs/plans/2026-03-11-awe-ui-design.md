# AWE Web UI Design Document

> Date: 2026-03-11
> Status: Approved
> Style: Linear + Notion inspired — 簡潔日系富有設計感

---

## 1. Design Language

### 美學定位

結合 Linear 的精確工程感與 Notion 的親和呼吸感：

- **色彩**：中性灰基底（Gray 50–900），單一品牌強調色（Blue 500 `#3B82F6`），語義色僅用於狀態
- **字體**：英文 Inter、中文 Noto Sans TC、程式碼 JetBrains Mono
- **圓角**：小元件 4px、卡片 8px、Modal 12px — 不超過 12px
- **陰影**：僅 hover/float 時使用，靜態元素無陰影，保持平面感
- **間距**：8px grid 系統，所有間距為 8 的倍數
- **動畫**：duration 150–200ms、easing `cubic-bezier(0.4, 0, 0.2, 1)`，僅功能性動畫
- **圖標**：自訂 SVG component，stroke 風格，統一 1.5px 線寬，round cap + round join

### 色彩系統

| Token | Light | 用途 |
|-------|-------|------|
| `surface.primary` | `#FFFFFF` | 主背景 |
| `surface.secondary` | `#F9FAFB` (Gray 50) | 次要區域、卡片底 |
| `surface.variant` | `#F3F4F6` (Gray 100) | Badge、Tag 底色 |
| `border.default` | `#E5E7EB` (Gray 200) | 卡片/分隔線 |
| `text.primary` | `#111827` (Gray 900) | 主文字 |
| `text.secondary` | `#6B7280` (Gray 500) | 次要文字 |
| `accent` | `#3B82F6` (Blue 500) | 品牌色、互動元素 |

### 語義色（僅用於狀態指示）

| 狀態 | 顏色 | Hex |
|------|------|-----|
| Running | Blue | `#3B82F6` |
| Completed | Emerald | `#10B981` |
| Failed | Red | `#EF4444` |
| Pending | Gray | `#9CA3AF` |
| Retrying | Amber | `#F59E0B` |

---

## 2. Tech Stack

| 層級 | 選型 |
|------|------|
| Framework | React + Vite (SPA) |
| Language | TypeScript |
| UI Library | MUI (Material UI) |
| Canvas | @xyflow/react |
| Router | TanStack Router |
| Data Fetching | TanStack Query |
| State | Nano Stores |
| Forms | React Hook Form + Zod |
| Real-time | SSE (Server-Sent Events) |

### 專案結構

```
awe/
├── backend/          # Python: Engine + FastAPI + CLI
├── frontend/         # TypeScript: React UI
│   └── src/
│       ├── components/
│       │   ├── icons/        # 自訂 SVG icon components
│       │   ├── canvas/       # @xyflow/react node components
│       │   └── common/       # 共用 UI 組件
│       ├── pages/            # 頁面組件
│       ├── stores/           # Nano Stores
│       ├── hooks/            # Custom hooks (SSE, queries)
│       ├── api/              # Auto-generated API client
│       └── theme/            # MUI theme customization
├── schemas/          # Shared JSON Schema
├── examples/         # Pipeline + Agent YAMLs
└── Makefile          # Unified dev commands
```

### 前後端橋接

- FastAPI auto-generates OpenAPI spec
- Frontend auto-generates TypeScript types from OpenAPI
- JSON Schema 作為 shared contract（Pydantic exports → frontend validates）

---

## 3. Layout

### 全域框架

```
┌──────────────────────────────────────────────────┐
│  ◆ AWE    Pipelines  Runs  Agents     ⚙ Settings │  ← Top Nav (48px)
├──────────────────────────────────────────────────┤
│                                                  │
│                 Content Area                     │  ← 100vh - 48px
│                                                  │
└──────────────────────────────────────────────────┘
```

- **Top Navigation**：48px 高度，固定頂部
- 左側：Logo mark（幾何菱形 `◆`）+ 產品名「AWE」
- 中間：頁面切換 tabs（文字 link，hover 底線，active 態品牌色底線 2px）
- 右側：Settings 齒輪 icon
- 不使用 Sidebar — Canvas 頁需要最大水平空間

---

## 4. Pages

### 4.1 Pipelines 頁面

入口頁，展示所有可用 Pipeline。

**頂部操作列**
- 左側：標題「Pipelines」+ 計數 badge
- 右側：Ghost button「+ New Pipeline」

**卡片網格** — 3 欄（xl 4 欄），每張卡片：

```
┌─────────────────────────────────────┐
│                                     │
│    ○ ── ○ ── ○                      │  ← Mini flow preview (80px 高)
│                                     │
├─────────────────────────────────────┤
│  Analyze & Fix                      │  ← Pipeline 名稱
│  2 steps · Last run: 3h ago         │  ← 摘要資訊
│                                     │
│  ┌──────┐  ┌─────────┐             │
│  │ Run ▶ │  │ Edit    │             │  ← 操作按鈕
│  └──────┘  └─────────┘             │
└─────────────────────────────────────┘
```

| 元素 | 規格 |
|------|------|
| Mini flow preview | 灰色節點 + 連線，純裝飾用，80px 高 |
| Pipeline 名稱 | `text.primary`，16px，font-weight 600 |
| 摘要 | `text.secondary`，14px |
| Run 按鈕 | Contained，品牌色，附 Play icon |
| Edit 按鈕 | Outlined，跳轉至 Canvas |

**新增 Pipeline**：Ghost button 卡片，虛線邊框，hover 顯示品牌色

**空狀態**：中央線條插圖 +「尚無 Pipeline」+ Ghost button「建立第一個 Pipeline →」

---

### 4.2 Canvas 頁面（核心）

Pipeline 的視覺化編輯與執行頁面，分「設計模式」與「執行模式」。

**整體佈局**

```
┌──────────────────────────────────────────────────┐
│  ◆ AWE    Pipelines  Runs  Agents     ⚙ Settings │
├──────────────────────┬───────────────────────────┤
│                      │  Node Config Panel (320px) │
│                      │                           │
│     Canvas Area      │  Agent: [dropdown]        │
│     (@xyflow/react)  │  Prompt: [textarea]       │
│                      │  Context From: [multi]    │
│                      │  Quality Gate: [config]   │
│  ┌────┐   ┌────┐    │                           │
│  │ S1 │──▶│ S2 │    │                           │
│  └────┘   └────┘    │                           │
│                      │                           │
├──────────────────────┴───────────────────────────┤
│  Execution Output Panel (collapsible, 200px)      │
│  [Step 1 ✓] → [Step 2 ⟳ running...]              │
│  > Raw output streaming here...                   │
└──────────────────────────────────────────────────┘
```

**Toolbar（Canvas 頂部，緊貼 Top Nav 下方）**

```
Pipeline Name (editable)  |  [Save]  [▶ Run]  |  Zoom controls
```

- Save：Ghost button
- Run：Contained + Play icon，執行時變為 Stop（品牌色 → 紅色）

#### 4.2.1 雙模式節點設計

**設計模式（Design Mode）— 精簡**

```
┌──────────────────────┐
│  ◉  Step Name        │  120×48px
│     agent-name       │  圓角 8px
└──────────────────────┘
```

- 左側 8px 狀態圓點（設計模式中固定灰色）
- 左右各一個 Handle（連接點），6px 圓形
- 選中態：品牌色 border 2px + 輕微 shadow

**執行模式（Execution Mode）— 資訊豐富**

```
┌──────────────────────────────┐
│  ◉  Step Name         2.3s  │  展開為 180×80px
│     agent-name              │
│  ████████░░ 80%  $0.003     │  進度條 + 費用
│  Tokens: 1,204              │
└──────────────────────────────┘
```

- 狀態圓點隨執行狀態變色（使用語義色系統）
- Running 狀態：呼吸動畫（opacity 0.4↔1.0）
- 進度條：4px 高，細長矩形
- 失敗態：左側 border 變紅 2px

#### 4.2.2 Right Panel（Node Config，320px）

選中節點時滑入，未選中時隱藏（Canvas 佔滿寬度）。

內容分區：

1. **Basic** — Step ID（唯讀）、Agent（dropdown）、Prompt（textarea，支援 `{{context}}` 語法高亮）
2. **Context** — Context From 多選（上游 step + compression strategy）
3. **Quality Gate** — Mode 切換（auto/agent/human）、動態表單（auto: command list / agent: review_prompt）
4. **Retry** — Max retries slider、Inject failure reason toggle

每個區塊使用 MUI `Accordion`，預設展開 Basic。

#### 4.2.3 Bottom Panel（Execution Output）

- 預設收合，執行時自動展開（200px）
- 可拖曳調整高度
- 左側：Step 執行流程（水平排列，使用狀態 icon）
- 右側：選中 step 的 raw output，SSE streaming 即時更新
- Monospace 字體（JetBrains Mono），暗底淺字（`Gray 900` 底 + `Gray 100` 字）

#### 4.2.4 SSE 即時更新機制

```
EventSource: /api/runs/{run_id}/stream

Events:
  step_start   → 節點狀態 → Running（呼吸動畫）
  step_output  → Bottom panel streaming
  step_done    → 節點狀態 → Completed，顯示耗時/費用
  step_failed  → 節點狀態 → Failed，紅色 border
  run_done     → Toolbar Run 按鈕恢復
```

---

### 4.3 Runs 頁面

Pipeline 執行歷史總覽，核心目標是 **scanability**。

**頂部篩選列**
- 左側：狀態篩選 chips — `All` / `Running` / `Completed` / `Failed`（MUI `ToggleButtonGroup`）
- 右側：時間範圍（Today / 7d / 30d / Custom）+ 搜尋框

**Run 列表（MUI DataGrid）**

| 欄位 | 說明 |
|------|------|
| Status | StatusDot icon（12px，語義色） |
| Run ID | Monospace，格式 `run-20260311-143022-a1b2` |
| Pipeline | 名稱，可點擊跳轉 Canvas |
| Steps | 分段進度條（4px 高），每段對應一個 step 的狀態色 |
| Duration | `2m 34s`，running 中顯示計時動畫 |
| Cost | `$0.042`，右對齊 |
| Started | 相對時間 `3 min ago`，hover tooltip 顯示絕對時間 |

**展開列（Expandable Row）**

點擊展開 step 明細：
- 水平 step 流程圖（迷你版，使用 StatusDot icon）
- 每個 step：名稱、agent、耗時、token 數
- 點擊 step 可跳轉至 Canvas 該節點

**空狀態**
- 線條風格插圖
- 「尚無執行記錄」+「從 Pipelines 頁面啟動你的第一個工作流」
- Ghost button「瀏覽 Pipelines →」

---

### 4.4 Agents 頁面

Agent 註冊管理。

**頂部操作列**
- 標題「Agents」+ 計數 `12 registered`
- 搜尋框 + Capability tag 篩選 Dropdown + Ghost button「+ New Agent」

**Agent 卡片網格** — 3 欄（xl 4 欄）

```
┌─────────────────────────────────┐
│  ◉ Researcher            sonnet │  ← 狀態燈 + 名稱 + model badge
│  Senior analysis agent          │  ← role
│                                 │
│  ┌────┐ ┌──────┐ ┌────────┐    │
│  │code│ │review│ │analysis│    │  ← capability tags (Chip)
│  └────┘ └──────┘ └────────┘    │
│                                 │
│  Tokens: 4,096    Cost: ~$0.02  │  ← 規格摘要
│  Schema: ✓        Runs: 47      │
└─────────────────────────────────┘
```

| 元素 | 規格 |
|------|------|
| 狀態燈 | 8px 實心圓。已驗證 = Emerald，未測試 = Gray |
| Model Badge | 圓角小標籤，`surface.variant` 底色，monospace |
| Capability Tags | MUI `Chip` size="small"，outline，圓角 4px |
| Schema 勾號 | CheckCircle SVG icon 16px |
| Runs | 從 `step_runs` 表聚合 |

**Agent 詳情 Drawer（右側，480px）**

點擊卡片滑出，三區塊：

1. **Profile** — YAML 可視化：名稱、role、model、max_tokens、constraints
2. **Capabilities** — Tag 列表 + 描述
3. **History** — 最近 10 次執行 mini table（Pipeline / Step / Duration / Result）

底部固定列：「Edit YAML」（Monaco Editor）+「Delete」（destructive，需二次確認）

**空狀態**
- 機器人輪廓線條插圖
- 「尚無已註冊的 Agent」+ Ghost button「查看範例 →」

---

### 4.5 Settings 頁面

單頁式設定，MUI `List` + `ListItem` 分區。

**Section 1：API Keys**
- Anthropic API Key — 密碼輸入框 + 「Test Connection」按鈕
- 連線狀態：StatusDot（綠/紅/灰）

**Section 2：Defaults**
- Default Model — Dropdown（opus / sonnet / haiku）
- Default Max Tokens — 數字輸入
- Default Compression — Dropdown（full / summary / diff_only）

**Section 3：Storage**
- Database 路徑 — 唯讀 `.awe/awe.db`
- Output 路徑 — 唯讀 `.awe/outputs/`
- 「Clear All Runs」— Destructive button，需輸入 `DELETE` 確認

**Section 4：About**
- 版本號、GitHub 連結、License

---

## 5. Icon System

所有圖示在 `frontend/src/components/icons/` 統一管理，以 React component 封裝。

### 規格

- 繪製方式：`<svg>` 內嵌，stroke 風格
- 線寬：統一 1.5px
- 端點：`stroke-linecap="round"` + `stroke-linejoin="round"`
- Props：`size: number`（預設 16）、`color: string`（預設 currentColor）

### Icon 清單

| Component | 用途 | 尺寸 |
|-----------|------|------|
| `StatusDot` | 執行狀態指示 | 8–12px，支援 running/completed/failed/pending/retrying variants |
| `CheckCircle` | Schema 存在、通過 | 16px 圓底 + 勾 |
| `CrossCircle` | 失敗、刪除 | 16px 圓底 + 叉 |
| `ArrowRotate` | 重試中 | 14px 圓弧箭頭，支援旋轉動畫 |
| `PipelineIcon` | 導航 | 16px 三節點連線 |
| `AgentIcon` | 導航 | 16px 機器人頭輪廓 |
| `PlayIcon` | 執行按鈕 | 16px 三角形 |
| `StopIcon` | 停止按鈕 | 16px 方形 |
| `SettingsIcon` | 設定導航 | 16px 齒輪 |
| `ChevronIcon` | 展開/收合 | 12px 箭頭，支援方向 prop |
| `SearchIcon` | 搜尋框 | 16px 放大鏡 |
| `PlusIcon` | 新增按鈕 | 16px + 號 |
| `TrashIcon` | 刪除 | 16px 垃圾桶 |
| `EditIcon` | 編輯 | 16px 鉛筆 |
| `LogoMark` | Top Nav 品牌 | 20px 幾何菱形 |

### StatusDot 動畫規格

| Variant | 視覺 | 動畫 |
|---------|------|------|
| `running` | 實心圓 Blue 500 | opacity 0.4↔1.0，duration 1.5s，ease-in-out |
| `completed` | 圓底 + 勾 Emerald 500 | 無動畫 |
| `failed` | 圓底 + 叉 Red 500 | 無動畫 |
| `pending` | 空心圓 Gray 400 | 無動畫 |
| `retrying` | 圓弧箭頭 Amber 500 | rotate 360deg，duration 1s，linear |

---

## 6. Interaction Patterns

### 通用

- **Loading**：Skeleton（MUI `Skeleton`），不使用 spinner
- **Toast**：右下角，自動消失 4s，分 success/error/info 三種
- **Confirm Dialog**：Destructive 操作使用 MUI `Dialog`，需明確確認
- **Empty State**：統一風格 — 線條插圖 + 主文字 + 次要說明 + CTA 按鈕
- **Hover**：卡片 hover 加 `border-color: accent` 過渡，150ms

### Canvas 特有

- **Node 拖曳**：@xyflow/react 內建，snap to grid 20px
- **連線**：從 Handle 拖出，hover 目標 Handle 時高亮
- **多選**：框選或 Cmd+Click，支援批次刪除
- **Undo/Redo**：Cmd+Z / Cmd+Shift+Z（操作 Nano Store history）
- **Keyboard**：Delete 刪除選中、Space 拖曳畫布、Cmd+S 儲存

---

## 7. Responsive Behavior

| Breakpoint | 行為 |
|------------|------|
| `>= 1280px` (xl) | 卡片 4 欄，完整佈局 |
| `>= 960px` (lg) | 卡片 3 欄，Canvas right panel 可收合 |
| `>= 600px` (md) | 卡片 2 欄，Top Nav 保持 |
| `< 600px` (sm) | 不主動支援（桌面優先工具） |

---

## 8. API Endpoints (Draft)

Frontend 需要的 API 端點概覽：

```
GET    /api/pipelines              # 列表
POST   /api/pipelines              # 建立
GET    /api/pipelines/:id          # 取得（含 steps）
PUT    /api/pipelines/:id          # 更新
DELETE /api/pipelines/:id          # 刪除

POST   /api/pipelines/:id/run      # 執行 pipeline
GET    /api/runs                   # 執行歷史列表
GET    /api/runs/:id               # 單次執行詳情
GET    /api/runs/:id/stream        # SSE 即時串流

GET    /api/agents                 # Agent 列表
GET    /api/agents/:id             # Agent 詳情
PUT    /api/agents/:id             # 更新 Agent YAML
DELETE /api/agents/:id             # 刪除

GET    /api/settings               # 讀取設定
PUT    /api/settings               # 更新設定
POST   /api/settings/test-key      # 測試 API Key
```
