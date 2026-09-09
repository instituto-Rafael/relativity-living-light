# 🏗️ Arquitetura do Dashboard Relativity

## Visão Geral

Dashboard moderno, fluido e avançado construído com React 19, TypeScript, Tailwind CSS e Recharts. Implementa padrões de design profissionais com foco em usabilidade, performance e escalabilidade.

## 🎯 Princípios de Design

### 1. User-Centric Design
- Interface intuitiva e acessível
- Fluxos simples e diretos
- Feedback visual imediato
- Erros e sucesso claramente comunicados

### 2. Performance First
- Bundle size otimizado
- Lazy loading automático
- Caching inteligente
- Sem tokens vazios

### 3. Type Safety
- TypeScript strict mode
- Interfaces bem definidas
- Zero implicit any

### 4. Modularidade
- Componentes reutilizáveis
- Separação de responsabilidades
- Fácil manutenção

## 📐 Arquitetura em Camadas

```
┌─────────────────────────────────┐
│     Apresentação (UI)           │
│  ├─ Components/                 │
│  ├─ Pages/                      │
│  └─ Layout/                     │
├─────────────────────────────────┤
│     Estado & Lógica             │
│  ├─ store/ (Zustand)            │
│  ├─ hooks/                      │
│  └─ utils/                      │
├─────────────────────────────────┤
│     Dados & Integração          │
│  ├─ services/ (API)             │
│  ├─ types/                      │
│  └─ i18n/                       │
├─────────────────────────────────┤
│     Infraestrutura              │
│  ├─ Vite (Build)                │
│  ├─ Tailwind (Styling)          │
│  └─ Recharts (Visualização)     │
└─────────────────────────────────┘
```

## 🧩 Componentes Principais

### Layout Components
- **Header**: Navegação superior, tema, idioma
- **Sidebar**: Menu lateral responsivo
- **Card**: Componente base para conteúdo

### Feature Components
- **DashboardPage**: Dashboard principal com KPIs
- **AnalysisPanel**: Painel de análise com gráficos
- **ExportPanel**: Interface de exportação
- **SettingsPage**: Configurações de usuário

### UI Components
- **Card**: Container principal
- **AnalysisChart**: Wrapper de gráficos Recharts

## 🔄 Fluxo de Dados

```
User Input
    ↓
Component Event Handler
    ↓
Store (Zustand) - Updates State
    ↓
Component Re-renders
    ↓
Updated UI
```

### Exemplo: Alteração de Idioma

```
Language Selector Click
    ↓
setLanguage(code) → Store
    ↓
i18n.changeLanguage(code)
    ↓
Re-render com novo idioma
    ↓
DOM atualizado
```

## 🌐 Sistema de i18n

### Estrutura de Traduções

```
src/i18n/
├── locales/
│   ├── pt.json (Português)
│   ├── en.json (English)
│   ├── es.json (Español)
│   ├── fr.json (Français)
│   └── de.json (Deutsch)
└── config.ts (Configuração i18next)
```

### Uso em Componentes

```tsx
import { useTranslation } from 'react-i18next'

export function MyComponent() {
  const { t } = useTranslation()
  return <h1>{t('nav.dashboard')}</h1>
}
```

## 🎨 Sistema de Temas

### Temas Disponíveis
- **Light**: Tema claro (padrão)
- **Dark**: Tema escuro (OLED-friendly)
- **Auto**: Segue preferência do sistema

### Implementação

```tsx
useAppStore() → { theme, setTheme }
```

Armazenado em localStorage e aplicado via classe `dark` no HTML.

## 🔐 Type System

### Tipos Principais

```typescript
// types/index.ts
interface AnalysisData {
  id: string
  timestamp: Date
  value: number
  category: string
  metadata?: Record<string, unknown>
}

interface ExportOptions {
  format: 'pdf' | 'csv' | 'json' | 'xlsx'
  includeMetadata: boolean
  dateRange?: { start: Date; end: Date }
}

interface ChartConfig {
  title: string
  type: 'line' | 'bar' | 'area' | 'pie'
  dataKey: string
  responsive: boolean
}
```

## 🏪 State Management

### Zustand Store

```typescript
// store/appStore.ts
interface AppStore {
  theme: 'light' | 'dark' | 'auto'
  language: string
  sidebarOpen: boolean
  setTheme: (theme) => void
  setLanguage: (lang) => void
  toggleSidebar: () => void
}
```

**Por que Zustand?**
- Minimal boilerplate
- Sem providers necessários (opcional)
- Type-safe
- Performance otimizada
- Pequeno bundle (~1KB)

## 🎯 Padrões de Componentes

### Container vs Presentational

**Containers** (Smart Components)
- Lógica de negócio
- Gerenciamento de estado
- Chamadas de API

**Presentational** (Dumb Components)
- Props-driven
- UI pura
- Reutilizável

### Exemplo

```tsx
// Container
function AnalysisPanelContainer() {
  const [data, setData] = useState([])
  const { filters } = useAppStore()
  
  useEffect(() => {
    // Fetch data
  }, [filters])
  
  return <AnalysisPanel data={data} />
}

// Presentational
function AnalysisPanel({ data }) {
  return <AnalysisChart data={data} />
}
```

## 📊 Fluxo de Visualização de Dados

```
Raw Data
    ↓
Filter & Transform
    ↓
Type Check (TypeScript)
    ↓
Recharts Processing
    ↓
Canvas Rendering
    ↓
Interactive Chart
```

## 🔄 Performance Otimizations

### Code Splitting
- Vite lazy loading automático
- Route-based splitting (future)

### Memoization
```tsx
const MemoizedChart = memo(AnalysisChart)
```

### CSS-in-JS
- Tailwind (zero runtime)
- Classe-based (não inline styles)

### Caching
- LocalStorage para preferências
- IndexedDB para dados (future)

## ♿ Acessibilidade

### WCAG 2.1 Compliance
- Semantic HTML
- ARIA labels onde necessário
- Keyboard navigation
- Color contrast ratios

### Exemplo
```tsx
<button
  onClick={handleClick}
  aria-label="Menu principal"
  title="Abrir/Fechar menu"
>
  <Menu />
</button>
```

## 🌍 Responsive Design

### Breakpoints (Tailwind)
```
sm: 640px  - Tablets
md: 768px  - Small desktops
lg: 1024px - Large desktops
```

### Mobile-First Approach
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  {/* Mobile: 1 coluna, Tablet: 2, Desktop: 4 */}
</div>
```

## 🚀 Build & Deployment

### Vite Optimization
- Tree-shaking automático
- Code minification
- Asset optimization
- Source maps (development)

### Bundle Analysis
```bash
npm run build -- --analyze
```

## 🧪 Testing Strategy

### Unit Tests
- Componentes individuais
- Utilitários e helpers
- Store (Zustand)

### Integration Tests
- Fluxos de usuário
- Interações entre componentes

### E2E Tests (Future)
- Playwright
- Cenários críticos

## 🔒 Segurança

### Práticas Implementadas
- Content Security Policy ready
- XSS protection (React escaping)
- HTTPS ready
- No inline scripts
- Dependency scanning

## 📈 Escalabilidade

### Como Adicionar Novos Recursos

1. **Novo Componente**
```bash
# Criar arquivo
src/components/MyFeature/MyComponent.tsx

# Com types
src/types/index.ts → Adicionar interface
```

2. **Novo Idioma**
```
Criar src/i18n/locales/xx.json
Importar em config.ts
Adicionar ao dropdown de idiomas
```

3. **Novo Gráfico**
```
Adicionar tipo em ChartConfig
Implementar em AnalysisChart.tsx
Usar em AnalysisPanel
```

## 🛠️ Ferramentas de Desenvolvimento

### Debug
```tsx
console.log('debug:', { theme, language })
React DevTools (Chrome Extension)
```

### Performance Profiling
```bash
npm run dev
# Chrome DevTools → Performance tab
```

## 📚 Convenções de Código

### Naming Conventions
- Components: PascalCase (`DashboardPage`)
- Functions: camelCase (`handleExport`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- Types: PascalCase (`ChartConfig`)

### Arquivo Structure
```tsx
// 1. Imports
import { useTranslation } from 'react-i18next'

// 2. Types
interface Props { ... }

// 3. Component
export function MyComponent(props: Props) {
  // Setup
  const { t } = useTranslation()
  const [state, setState] = useState()
  
  // Effects
  useEffect(() => {}, [])
  
  // Handlers
  const handleEvent = () => {}
  
  // Render
  return <div>{t('key')}</div>
}
```

## 🎓 Próximos Passos

1. ✅ Estrutura Base
2. ✅ Componentes Core
3. ✅ i18n (5 Idiomas)
4. ✅ Temas (Light/Dark)
5. ⏳ API Integration
6. ⏳ Real-time Updates
7. ⏳ Advanced Filtering
8. ⏳ Data Export (Real)
9. ⏳ Unit Tests
10. ⏳ E2E Tests

---

**Dashboard Relativity © 2026**
