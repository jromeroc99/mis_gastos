# Roadmap General - Mis Gastos

**Instrucciones básicas**: Ver [#file:AGENTS.md](../../AGENTS.md) para reglas de desarrollo

---

## Fases de Desarrollo

### FASE 1: Backend (FastAPI + PostgreSQL) ✅ PRIORIDAD
**Objetivo**: Backend robusto y funcional con todas las reglas de negocio implementadas

📁 Carpeta: `docs/roadmap/backend/`
- Contiene todas las tareas detalladas del backend
- Desarrollo secuencial task by task
- Testing obligatorio antes de avanzar

### FASE 2: Frontend Web (React + Vite) 📋 PENDIENTE
**Objetivo**: Interfaz web responsive que consume la API del backend

📁 Carpeta: `docs/roadmap/frontend/`
- Se iniciará SOLO cuando el backend esté 100% completado
- Cliente ligero que consume API REST

### FASE 3: Mobile App (Jetpack Compose) 📋 FUTURO
**Objetivo**: App móvil nativa para Android

📁 Carpeta: `docs/roadmap/mobile/`
- Se iniciará SOLO cuando frontend web esté completado
- Reutiliza misma API REST del backend

---

## Orden de Ejecución

```
1. Backend completo (todas las tareas)
   ├── Infraestructura base
   ├── Autenticación
   ├── Modelos y base de datos
   ├── APIs REST
   ├── Lógica de negocio
   └── Testing completo
   
2. Frontend Web (después de 1)
   ├── Setup y configuración
   ├── Servicios API
   ├── Componentes
   └── Integración completa
   
3. Mobile App (después de 2)
   ├── Setup Android
   ├── Servicios API
   ├── Screens
   └── Integración completa
```

---

## Metodología de Trabajo

**IMPORTANTE**: Leer [#file:AGENTS.md](../../AGENTS.md) antes de cada tarea

1. ✅ Ejecutar una tarea a la vez
2. ✅ Testing obligatorio antes de avanzar
3. ✅ Preguntar confirmación al usuario
4. ✅ Esperar aprobación explícita
5. ✅ No avanzar de fase hasta completar la anterior

---

**Estado actual**: FASE 1 - Backend en progreso
**Última actualización**: 2025-12-23
