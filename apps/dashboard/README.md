# 📊 Relativity Dashboard - UX Moderna & Fluida

Dashboard profissional para análise de dados Relativity Living Light com interface moderna, fluida e avançada.

## ✨ Características Principais

### 🎨 Design Elegante & Profissional
- Interface moderna com Tailwind CSS
- Tema claro/escuro automático
- Animações fluidas e responsivas
- Design intuitivo e acessível

### 📊 Análises Avançadas
- Gráficos interativos (linha, barra, área, pizza)
- Dashboard em tempo real
- Filtros e ordenação de dados
- Análise comparativa e preditiva

### 🌍 Multilíngue (5 Idiomas)
- Português (PT-BR)
- English (EN-US)
- Español (ES-ES)
- Français (FR-FR)
- Deutsch (DE-DE)

### 💾 Exportação de Dados
- JSON para integração
- CSV para Excel
- PDF para relatórios
- Excel (.xlsx) para análise

### 📱 Compatibilidade Mobile
- Suporte Android 10-17
- ARM32/64 (v7/v8)
- Interface responsiva
- PWA (Progressive Web App)

### ⚙️ Personalizável
- Temas customizáveis
- Layout flexível
- Componentes reutilizáveis
- Fácil integração

## 🚀 Começar Rápido

### Pré-requisitos
- Node.js 18+
- npm ou yarn

### Instalação

```bash
cd apps/dashboard
npm install
```

### Desenvolvimento

```bash
npm run dev
```

Abra `http://localhost:3000` no navegador.

### Build para Produção

```bash
npm run build
npm run preview
```

## 📁 Estrutura do Projeto

```
apps/dashboard/
├── src/
│   ├── components/
│   │   ├── Layout/        # Header, Sidebar
│   │   ├── Dashboard/     # Dashboard principal
│   │   ├── Analysis/      # Painéis de análise
│   │   ├── Charts/        # Componentes de gráficos
│   │   ├── Export/        # Exportação de dados
│   │   ├── Settings/      # Configurações
│   │   └── ui/           # Componentes base (Card, etc)
│   ├── store/            # Zustand store (tema, idioma)
│   ├── i18n/             # Configuração i18next
│   │   └── locales/      # Traduções (5 idiomas)
│   ├── types/            # TypeScript types
│   ├── App.tsx           # App principal
│   ├── main.tsx          # Entry point
│   └── index.css         # Estilos globais
├── public/               # Assets estáticos
├── index.html           # HTML template
├── package.json
├── tailwind.config.js   # Configuração Tailwind
├── vite.config.ts       # Configuração Vite
└── tsconfig.json        # Configuração TypeScript
```

## 🎯 Funcionalidades

### Dashboard
- Métricas em tempo real
- Gráficos interativos
- Cards de KPI
- Trends de dados

### Análise
- Análise avançada
- Análise comparativa
- Análise preditiva
- Estatísticas detalhadas

### Exportação
- Múltiplos formatos
- Opções de metadados
- Compactação automática
- Download direto

### Configurações
- Tema (Claro/Escuro/Auto)
- Idioma (5 opções)
- Notificações
- Privacidade e cookies

## 🎨 Customização

### Alterar Cores
Edite `tailwind.config.js` na seção `theme.extend.colors`

### Adicionar Idioma
1. Crie arquivo em `src/i18n/locales/xx.json`
2. Importe em `src/i18n/config.ts`
3. Adicione à lista de idiomas

### Criar Novo Componente
```tsx
import { Card, CardHeader, CardBody } from '../ui/Card'

export function MyComponent() {
  return (
    <Card>
      <CardHeader title="Título" />
      <CardBody>Conteúdo</CardBody>
    </Card>
  )
}
```

## 📊 Tecnologias

- **React 19** - UI moderna
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Gráficos interativos
- **Zustand** - State management
- **i18next** - Internacionalização
- **Vite** - Build tool rápido

## 🔒 Segurança

- TypeScript strict mode
- HTTPS ready
- CSP compatible
- Sem dependências externas inseguras

## 📈 Performance

- Bundle size otimizado (~250KB)
- Lazy loading de componentes
- Tree-shaking automático
- Cache inteligente

## 🌐 Responsividade

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly
- Acessibilidade WCAG 2.1

## 📝 Licença

MIT License - Veja LICENSE.md para detalhes

## 💬 Contribuições

Pull requests são bem-vindos! Por favor:
1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 🆘 Suporte

Para problemas ou dúvidas, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para Relativity Living Light**
# CI/CD Pipeline Active
