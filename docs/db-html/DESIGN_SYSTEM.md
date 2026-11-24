# Sistema de Diseño y Animación Motion — ISFT 189
## Interfaz Técnica y Documentación Interactiva de Base de Datos

Este documento define el **Design System** y las **Especificaciones de Motion** para la plataforma de documentación interactiva de bases de datos del **ISFT 189**, abarcando el modelo relacional académico (`instituto`) y el motor vectorial RAG (`isft189` / pgvector).

---

## 1. Paleta de Colores y Tokens de Diseño

La estética visual se basa en **Slate / Corporate Navy de Alta Densidad Técnica**, orientada a herramientas profesionales de ingeniería de datos (tipo DataGrip, Neon, Supabase, pgAdmin moderno). Se ofrece soporte bidireccional: **Light Theme** (institucional formal) y **Dark Slate Theme** (alta concentración técnica).

### 1.1 Tokens de Superficie y Bordes

| Token CSS | Light Mode | Dark Slate Mode | Uso Técnico |
| :--- | :--- | :--- | :--- |
| `--bg-app` | `#f1f5f9` (Slate 100) | `#090d16` (Deep Navy) | Fondo general del viewport |
| `--bg-canvas` | `#f8fafc` (Slate 50) | `#0f172a` (Slate 900) | Área de visualización y arquitectura RAG |
| `--surface-0` | `#ffffff` (Blanco) | `#111827` (Slate 900+tint) | Tarjetas de tablas, paneles y modales |
| `--surface-1` | `#f8fafc` (Slate 50) | `#1e293b` (Slate 800) | Cabeceras secundarias y filas alternas |
| `--surface-2` | `#f1f5f9` (Slate 100) | `#243248` (Slate 800L) | Cabeceras de columna `<th>` y toolbars |
| `--surface-3` | `#e2e8f0` (Slate 200) | `#334155` (Slate 700) | Estados hover, chips y selects |
| `--surface-code` | `#0f172a` (Slate 900) | `#070b12` (Onyx Navy) | Contenedor de visualización SQL / DDL |
| `--border-subtle`| `#e2e8f0` (Slate 200) | `#1e293b` (Slate 800) | Líneas divisorias entre filas |
| `--border-default`| `#cbd5e1` (Slate 300) | `#334155` (Slate 700) | Contorno de tarjetas y tablas |
| `--border-strong` | `#94a3b8` (Slate 400) | `#475569` (Slate 600) | Inputs activos y divisores de panel |
| `--border-focus` | `#2563eb` (Blue 600) | `#3b82f6` (Blue 500) | Indicador accesible de foco |

### 1.2 Acentos Semánticos Institucionales

- **Azul Zafiro Institucional (`--accent-sapphire: #1d4ed8` / Dark: `#3b82f6`)**: Identidad institucional ISFT 189, navegación superior, botones primarios y tabs seleccionados.
- **Teal / Cian Técnico (`--accent-teal: #0f766e` / Dark: `#14b8a6`)**: Módulo Asistente Virtual IA, RAG, búsqueda vectorial semántica y pgvector.
- **Índigo Relacional (`--accent-indigo: #4338ca` / Dark: `#6366f1`)**: Esquema relacional `instituto`, grafo de llaves foráneas y correlatividades.

### 1.3 Badges de Metadatos de Base de Datos (High Density)

Los metadatos se presentan en formato de micro-píldora (`font-size: 10.5px`, `font-family: var(--font-mono)`, padding: `2.5px 5.5px`):

| Badge | Significado | Color Fondo (Light/Dark) | Borde (Light/Dark) | Texto (Light/Dark) | Icono Lucide Asignado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PK` | Primary Key | `#fef3c7` / `rgba(245,158,11,0.15)` | `#fcd34d` / `rgba(245,158,11,0.35)` | `#92400e` / `#fbbf24` | `key` |
| `FK` | Foreign Key | `#e0e7ff` / `rgba(99,102,241,0.15)` | `#a5b4fc` / `rgba(99,102,241,0.35)` | `#3730a3` / `#a5b4fc` | `link-2` |
| `UK` | Unique Key | `#dcfce7` / `rgba(34,197,94,0.15)` | `#86efac` / `rgba(34,197,94,0.35)` | `#166534` / `#4ade80` | `shield-check` |
| `ENUM`| Enumerated Type | `#f3e8ff` / `rgba(168,85,247,0.15)` | `#d8b4fe` / `rgba(168,85,247,0.35)`| `#6b21a8` / `#c084fc` | `list-filter` |
| `VECTOR`| Vector Embeddings | `#ecfeff` / `rgba(6,182,212,0.15)` | `#67e8f9` / `rgba(6,182,212,0.35)` | `#155e75` / `#67e8f9` | `cpu` |
| `NN` | Not Null | `#f1f5f9` / `rgba(148,163,184,0.12)`| `#cbd5e1` / `rgba(148,163,184,0.25)`| `#475569` / `#cbd5e1` | *(sin icono)* |

---

## 2. Sistema Tipográfico

### 2.1 Stacks Tipográficos
```css
/* Interfaz de usuario, etiquetas y navegación */
--font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
font-feature-settings: "cv02", "cv03", "cv04", "cv11";

/* Código SQL, DDL, nombres de esquemas, tablas, columnas y tipos */
--font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code", "SFMono-Regular", Consolas, monospace;
font-feature-settings: "calt" 1, "zero" 1;
```

### 2.2 Escala Jerárquica y Tamaños

| Nivel | Tamaño (px / rem) | Peso | Line-Height | Tracking | Aplicación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Title 1** | `22px` (1.375rem) | 750 (Bold) | 1.25 | `-0.02em` | Título del Dashboard / Esquema |
| **Title 2** | `17px` (1.062rem) | 650 (SemiBold) | 1.30 | `-0.015em` | Secciones principales (Módulos) |
| **Title 3 / Table Name** | `14px` (0.875rem) | 650 (SemiBold) | 1.35 | `-0.01em` | Nombre de tabla (Mono: `instituto.alumnos`) |
| **Body UI** | `13.5px` (0.843rem)| 450 (Regular) | 1.45 | `0` | Textos descriptivos y controles UI |
| **Table Cell / Atributo**| `12.5px` (0.781rem)| 500 (Medium) | 1.40 | `0` | Nombres de columnas de BD y tipos |
| **Code Snippet / DDL** | `12px` (0.75rem) | 400 (Regular) | 1.55 | `0` | Bloques interactivos SQL |
| **Badges / Metadatos** | `10.5px` (0.656rem)| 700 (Bold) | 1.00 | `+0.04em` | Píldoras de PK, FK, UK, ENUM, VECTOR |

---

## 3. Catálogo Oficial de Lucide Icons (Cero Emojis)

Todos los iconos se representan mediante **Lucide Icons** con trazado uniforme (`stroke-width: 1.75px` para 16px, `stroke-width: 2.2px` para microbadges de 10.5px).

### 3.1 Infraestructura de Base de Datos y Objetos de Esquema
| Concepto | Nombre Lucide Exacto | Uso |
| :--- | :--- | :--- |
| Servidor / Esquema | `database` | Raíz del selector de esquema (`instituto` / `isft189`) |
| Tabla Relacional | `table` | Listado y encabezados de entidades |
| Clave Primaria (PK) | `key` | Identificador único principal |
| Clave Foránea (FK) | `link-2` | Dependencia relacional referencial |
| Clave Única (UK) | `shield-check` | Restricción UNIQUE |
| Columnas / Atributos | `columns` | Selector de proyección y conteo de campos |
| Tipo ENUM | `list-filter` | Dominios restringidos de valores |
| pgvector / Embeddings | `cpu` | Campo vectorial `vector(1536)` |
| Relación / Grafo | `git-fork` / `network` | Inspección de relaciones y arquitectura vectorial |
| Restricción Check | `check-circle-2` | Validaciones booleanas `CHECK` |
| Índice (Index) | `binary` | B-Tree, HNSW, IVFFlat |
| Trigger / Disparador | `zap` | Procedimientos en eventos de tabla |

### 3.2 Dominio Académico Institucional (ISFT 189)
| Entidad | Nombre Lucide Exacto | Justificación Técnica |
| :--- | :--- | :--- |
| Instituto / Sede | `landmark` | Encabezado institucional superior |
| Carrera / Plan de Estudios | `graduation-cap` | Entidad `carreras`, `planes_estudio` |
| Materia / Asignatura | `book-open` | Entidad `materias` |
| Correlatividades | `git-branch` | Árbol de prelación académica |
| Legajo Alumno | `user` | Entidad `alumnos` |
| Planta Docente | `user-check` | Entidad `docentes` |
| Preceptor / Bedelía | `badge-check` | Entidad `preceptores` |
| Permisos y Seguridad | `shield` | Entidad `usuarios`, `roles` |
| Cursada / Inscripción | `calendar-check` | Entidad `cursadas`, `inscripciones` |
| Mesa de Examen | `calendar` | Entidad `mesas_examen` |
| Acta de Examen | `file-spreadsheet` | Entidad `actas_examen` |
| Documentación Oficial | `file-text` | Entidad `documentos_oficiales` |

### 3.3 Módulo Asistente Virtual Inteligente (RAG / Bot)
| Componente | Nombre Lucide Exacto | Justificación Técnica |
| :--- | :--- | :--- |
| Asistente / Motor Bot | `bot` | Interfaz del chatbot de consulta técnica |
| Sesión / Conversación | `messages-square` | Entidad `conversaciones` |
| Mensajes / Prompts | `message-square` | Entidad `mensajes` |
| Chunking / Fragmentación | `layers` | Fragmentos de documentos particionados |
| Búsqueda Vectorial | `search-code` | Similitud de coseno sobre embeddings |
| Proyección Semántica | `scatter-chart` | Inspección de clústeres vectoriales |

---

## 4. Especificaciones Motion (Motion One / motion.animate / Springs)

Las animaciones tienen carácter puramente funcional: informan cambios de estado y continuidad espacial sin entorpecer el flujo de trabajo técnico.

### 4.1 Constantes de Tiempo y Curvas Bézier
```typescript
export const MOTION_TOKENS = {
  // Curvas Bézier estándar
  easeOutQuad: [0.25, 1, 0.5, 1],       // Entradas ágiles
  easeInQuad: [0.5, 0, 0.75, 0],         // Salidas discretas
  easeSpringSnappy: [0.16, 1, 0.3, 1],   // Elementos interactivos
  easeLayout: [0.4, 0, 0.2, 1],          // Reacomodación de rejilla

  // Timings en milisegundos
  durationInstant: 100, // Tooltips, hovers de celda
  durationFast: 160,    // Tab switches, dropdowns
  durationNormal: 220,  // Staggered lists, drawers
  durationSlow: 320,    // Modales de gran porte, vistas completas

  // Parámetros de física de resortes (Springs)
  springDrawer: {
    stiffness: 420,
    damping: 38,
    mass: 0.85
  },
  springModal: {
    stiffness: 380,
    damping: 32,
    mass: 0.9
  }
};
```

### 4.2 Implementación de Animaciones con Motion One (`motion.animate`)

#### A. Entrada Staggered de Tarjetas de Tabla de Base de Datos
```typescript
import { animate, stagger } from "motion";

export function animateTableEntries(selector: string = ".db-card") {
  return animate(
    selector,
    {
      opacity: [0, 1],
      transform: ["translateY(10px) scale(0.99)", "translateY(0px) scale(1)"]
    },
    {
      duration: 0.22,
      easing: [0.16, 1, 0.3, 1],
      delay: stagger(0.035, { start: 0.05 })
    }
  );
}
```

#### B. Apertura y Cierre de Inspector Lateral (Schema & Table Drawer)
```typescript
import { animate } from "motion";

export function toggleDrawer(isOpen: boolean, drawerEl: HTMLElement, backdropEl: HTMLElement) {
  if (isOpen) {
    // Backdrop
    animate(backdropEl, { opacity: [0, 1] }, { duration: 0.16, easing: "ease-out" });
    // Drawer con resorte amortiguado (cero overshoot)
    return animate(
      drawerEl,
      { transform: ["translateX(100%)", "translateX(0%)"] },
      {
        duration: 0.24,
        easing: [0.16, 1, 0.3, 1]
      }
    );
  } else {
    animate(backdropEl, { opacity: [1, 0] }, { duration: 0.14, easing: "ease-in" });
    return animate(
      drawerEl,
      { transform: ["translateX(0%)", "translateX(100%)"] },
      { duration: 0.18, easing: [0.5, 0, 0.75, 0] }
    );
  }
}
```

#### C. Cambio de Vistas / Pestañas (Tab Transition)
```typescript
export function animateTabSwitch(outgoingEl: HTMLElement, incomingEl: HTMLElement) {
  // Salida rápida del panel anterior
  animate(outgoingEl, { opacity: [1, 0], transform: ["translateY(0px)", "translateY(-4px)"] }, {
    duration: 0.12,
    easing: "ease-in"
  }).finished.then(() => {
    outgoingEl.style.display = "none";
    incomingEl.style.display = "block";
    // Entrada con nitidez del nuevo panel
    animate(
      incomingEl,
      { opacity: [0, 1], transform: ["translateY(6px)", "translateY(0px)"] },
      { duration: 0.18, easing: [0.16, 1, 0.3, 1] }
    );
  });
}
```

---

## 5. Reglas de Diseño Sin Elementos Superfluos

1. **Densidad de Información Rigurosa**:
   - Altura de fila de tabla técnica: fijada estrictamente entre `32px` y `36px`.
   - Cero márgenes inflados: espaciado modular en base 4 (`4px`, `8px`, `12px`, `16px`).
2. **Jerarquía Tipográfica Inequívoca**:
   - Todo identificador de base de datos (nombre de esquema, tabla, columna, foreign key) se renderiza en tipografía Mono con peso semibold.
   - Los tipos de datos SQL se diferencian visualmente en color secundario para no competir con el nombre de la columna.
3. **Ergonomía de Badges**:
   - Agrupación estandarizada en la última columna o junto al nombre: `[PK]` primero, seguido de `[FK]`, `[UK]`, `[NN]` o tipo especial `[VECTOR]`.
4. **Política Anti-Decorativa**:
   - Queda prohibido el uso de emojis en toda la interfaz de esquemas, diccionarios de datos y diagramas.
   - No se emplean sombras difusas ni bordes con gradientes de color; la separación es nítida mediante bordes de `1px` contrastados (`var(--border-subtle)` / `var(--border-default)`).
   - Animaciones limitadas a un umbral máximo de 250ms, respetando de forma nativa la directiva `@media (prefers-reduced-motion: reduce)`.
