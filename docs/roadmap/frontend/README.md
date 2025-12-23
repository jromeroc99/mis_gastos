# Frontend Web - React + Vite

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../../AGENTS.md) para reglas de desarrollo

---

## ⚠️ IMPORTANTE

**Este roadmap se ejecutará SOLO cuando el backend esté 100% completado y testeado.**

Antes de iniciar, verificar que:
- ✅ Backend completo funcional
- ✅ Todos los tests del backend pasan
- ✅ API documentada en Swagger
- ✅ Docker Compose funcional
- ✅ Usuario ha dado aprobación explícita para continuar

---

## Estructura de Tareas

### Task F.1: Setup Inicial
- Crear proyecto Vite + React + TypeScript
- Configurar Tailwind CSS
- Configurar ESLint y Prettier
- Estructura de carpetas

### Task F.2: Servicios API
- Configurar Axios con interceptors JWT
- Implementar servicio de autenticación
- Implementar servicios para cada endpoint del backend
- Manejo de errores

### Task F.3: Context y Hooks
- AuthContext para autenticación
- Custom hooks para API calls
- Hook para manejo de tokens
- Hook para formateo de moneda

### Task F.4: Componentes de Autenticación
- LoginForm
- RegisterForm
- ProtectedRoute
- AuthLayout

### Task F.5: Componentes de Transacciones
- TransactionList
- TransactionForm
- TransactionCard
- Filtros y búsqueda

### Task F.6: Componentes de Dashboard
- Summary cards
- Gráficos con Chart.js
- Breakdown por categorías
- Evolución patrimonial

### Task F.7: Componentes de Gestión
- CategoriesList
- AccountsList
- AssetsList
- LiabilitiesList

### Task F.8: Onboarding
- Wizard de bienvenida
- Upload CSV
- Inicialización con datos por defecto

### Task F.9: Testing Frontend
- Tests de componentes con Vitest
- Tests de integración
- E2E con Playwright (opcional)

### Task F.10: Build y Deployment
- Configurar build de producción
- Docker para servir con Nginx
- Variables de entorno

---

**Estado**: ⏸️ PENDIENTE - Esperando completar backend

**Se desglosará en detalle cuando el backend esté listo.**
