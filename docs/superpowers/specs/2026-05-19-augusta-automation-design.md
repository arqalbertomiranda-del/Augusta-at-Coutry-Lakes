# Augusta at Country Lakes — Diseño de Automatización
**Fecha:** 2026-05-19
**Versión:** 1.0
**Ejecutor:** Claude Code (CLI)
**Autonomía:** Human-in-the-loop — el sistema propone, Jaime Miranda aprueba

---

## 1. Contexto y Objetivo

**Proyecto:** Augusta at Country Lakes — la privada más exclusiva frente al campo de golf de Country Lakes, diseñado por Greg Letsche. Arquitectura Artigas Arquitectos, paisajismo Maat Handasa. Entrega julio 2028.

**Empresa:** Boma Desarrollos — Jaime Alberto Miranda Gallardo, CEO. Portafolio: Country Lakes, Arrecife Sisal, Kumay y los proyectos más emblemáticos del sureste mexicano.

**Objetivo único:** Vender el 100% del inventario disponible antes del 31 de diciembre de 2026.

**Sitio actual:** https://augustacountrylakes.mx/inicio (será reemplazado por el nuevo sitio)

---

## 2. Mercado Objetivo

| Segmento | Perfil | Motivación |
|---|---|---|
| Mexicano interior | 35-60 años, HNWI, Monterrey/CDMX/Guadalajara | Golf, inversión, retiro activo |
| Americano (USA) | 40-65 años, segunda residencia, Sun Belt | Calidad de vida, costo-beneficio vs Florida/AZ |
| Canadiense | 45-70 años, jubilado activo o pre-jubilado | Clima, golf, costo de vida, comunidad |

**90% del inventario:** Second home como inversión. El mensaje central es estilo de vida + plusvalía + exclusividad.

**Afinidades del comprador:** Golf, sustentabilidad, turismo de lujo, gastronomía de autor, privacidad, comunidad de pares.

---

## 3. Stack Tecnológico (Decisiones Bloqueadas)

| Subsistema | Tecnología |
|---|---|
| Sitio web | Next.js 15 (App Router) + Tailwind + Framer Motion |
| CMS | Sanity.io (contenido blog + páginas) |
| Hosting | Vercel (CDN global, Core Web Vitals) |
| Inventario | Odoo REST API (sync en tiempo real) |
| CRM | HubSpot (leads, pipeline, email sequences) |
| WhatsApp | WhatsApp Business API |
| Contenido | Buffer (scheduling: Instagram, Facebook, TikTok, LinkedIn) |
| Video influencers | Arcads (Nanobanana 2 Pro) + ElevenLabs + ffmpeg |
| Competitiva | Apify web scraping + Apollo.io |
| Análisis | Claude Code agents + HubSpot Analytics MCP |

---

## 4. Roster de Influencers

**Isabela** — TOFU (Top of Funnel)
- Perfil: ~28 años, dark brunette lacia larga, ojos verdes claros, piel clara con bronceado ligero
- Ropa signature: lino blanco, escotes en V, joyería oro 18k discreta
- Uso: Reels dinámicos TikTok/Instagram, descubrir, inspirar
- Pipeline: `scripts/01_generate_isabela_augusta_stills.py` → `scripts/02_animate_voiceover_combine.py`
- Voz ElevenLabs: Jessica (cgSgspJ2msm6clMCkdW9), stability=0.38, style=0.35
- Carpeta: `influencers/isabela-dark-brunette-straight-green-eyes-fair/`

**Camila** — BOFU (Bottom of Funnel)
- Perfil: ~35 años, castaña media lacia, ojos verde oliva, tez blanca con bronceado natural
- Arquetipo: Old money mexicana consolidada — "el lujo que no necesita demostrarse"
- Uso: Testimoniales, stories de confianza, videos de cierre
- Voz ElevenLabs: Ana María (m7yTemJqdIqrcNleANfX), stability=0.15, style=0.90
- Carpeta refs: en Arrecife Sisal docs/references/influencers/camila-chestnut/

**Influencers adicionales disponibles** (roster completo en carpeta `influencers/`):
- Gabriela (rubia ondulada, ojos verdes, bronceada)
- Valentina (dos versiones: rubia playera y rubia ondulada)
- Sofia (cabello negro lacio, hoyuelos, ojos avellana)
- Renata (pelirroja ondulada, ojos verde mar, piel marfil)
- Nico (hombre, brunette ondulado, barba corta, ojos verdes, piel oliva)
- Jayden (hombre, brunette cortina, mandíbula definida, ojos cafés, bronceado)

---

## 5. Assets de Producción

**Renders arquitectónicos:**
`C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos\02. Alcances\02.13 Renders\Arquitectonicos\`
- ACCESO.jpg — entrada principal (cobblestone roundabout, pergola)
- ACCESO CASA CLUB.jpg — casa club con alberca infinity
- AUGUSTA_AEREO CC.jpg — vista aérea del desarrollo
- BAR.jpg, GYM.jpg, COWORK.jpg, PET PARK.jpg — amenidades

**Renders casa club:**
`references/Augusta_casa-club_render_imagenes/`
- Augusta_casa-club_acceso.png
- Augusta_casa-club_terraza.png

**Video referencia:** `references/Augusta_casa-club_modelo.mp4`

**Master plan:** `references/Augusta_master-plan.png`

**Still preferido para video:** `outputs/isabela-augusta-stills-2026-05-13/S1-alberca-augusta.jpg`

---

## 6. Identidad de Marca

**Voz:** Cálida, segura, nunca pretenciosa. El lujo que se siente, no el que se proclama.
**Tono:** Editorial de golf club europeo — no mall de lujo. Privacidad y pertenencia, no exclusión agresiva.
**Idiomas:** Español (primario) + English (USA/Canada market)

**Paleta visual:**
- Verde campo profundo (#1B4332 o similar)
- Marfil cálido (#F5F0E8)
- Gold 18k (#C9A84C)
- Negro editorial (#0D0D0D)
- NUNCA: gradientes genéricos, gris corporativo, azul inmobiliario estándar

**Tipografía:**
- Headlines: serif elegante (Cormorant Garamond o Playfair Display)
- Body: sans limpio (Inter o DM Sans)
- Accent: serif italic para citas y testimoniales

**Anti-patrones prohibidos:**
- Cards uniformes con mismo padding
- Stock photos de parejas felices genéricas
- "Preventa" como único hook — siempre añadir el porqué del deseo
- Emojis en contenido de lujo (excepto stories casuales máximo 1)

---

## 7. Fase 1 — Sitio Web (Semanas 1-4)

### Objetivo
Reemplazar augustacountrylakes.mx con un sitio Next.js moderno que:
- Posicione en Google y ChatGPT para búsquedas clave
- Convierta visitantes en leads calificados vía cotizador
- Muestre inventario en tiempo real desde Odoo
- Capture leads directamente en HubSpot

### Arquitectura de Páginas

```
/ (Home)
  └── Hero: video 16:9 de Isabela en el campo, golden hour
  └── Hook: "La privada más exclusiva frente al campo de golf más codiciado de Latinoamérica"
  └── Stats: lotes disponibles (live desde Odoo), precio desde, entrega
  └── Preview: amenidades, campo, renders principales
  └── CTA: "Ver lotes disponibles" → /lotes

/el-proyecto
  └── Story de Augusta: Greg Letsche, Artigas, Maat Handasa
  └── Masterplan interactivo (SVG)
  └── Galería de renders
  └── Video: Augusta_casa-club_modelo.mp4

/campo-de-golf
  └── Greg Letsche — diseñador, trayectoria, filosofía
  └── El campo Country Lakes — 18 hoyos, el mejor de Latinoamérica
  └── Lifestyle: quiénes juegan aquí, torneos, membresías

/amenidades
  └── Casa club con alberca infinity
  └── Bar, Gym, Cowork, Pet Park
  └── Acceso cobblestone + pergola
  └── Video y renders de cada amenidad

/lotes (Cotizador — pieza clave)
  └── Mapa SVG interactivo del masterplan
  └── Filtros: tamaño, vista, ubicación, precio
  └── Cada lote: disponibilidad live (Odoo API), precio, m², renders
  └── Calculadora de financiamiento (36 MSI + hipotecario 180 meses)
  └── CTA: "Reservar" → Formulario → HubSpot + WhatsApp notification

/financiamiento
  └── Opciones: 36 MSI, crédito hipotecario 180 meses
  └── Calculadora interactiva
  └── FAQ de proceso de compra

/blog
  └── SEO content: golf Mérida, inversión Yucatán, second home México
  └── Manejado desde Sanity.io CMS
  └── Bilingüe ES/EN

/galeria
  └── Renders + videos + virtual tour 360

/contacto
  └── Formulario → HubSpot pipeline "Augusta Web"
  └── WhatsApp Business directo
  └── Mapa ubicación Country Lakes

```

### SEO Técnico

**Keywords objetivo (Tier 1):**
- "lotes frente al campo de golf México"
- "preventa residencial Mérida golf"
- "inversión lotes golf Yucatán"
- "second home Mexico golf luxury"
- "Augusta Country Lakes Mérida"

**Keywords objetivo (Tier 2 — long tail):**
- "campo de golf Greg Letsche México"
- "lotes residenciales preventa Mérida 2025"
- "mejor campo de golf Latinoamérica"
- "inversión inmobiliaria Mérida segunda casa"

**Implementaciones técnicas:**
- Schema.org: RealEstateListing, LocalBusiness, Organization, FAQPage
- Open Graph y Twitter Cards en todas las páginas
- Sitemap.xml dinámico (actualiza cuando hay cambios de inventario)
- Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1
- Canonical tags, hreflang ES/EN
- llms.txt para visibilidad en AI search (ChatGPT, Perplexity)
- Google Search Console + GA4 desde día 1

### Flujo del Cotizador

```
1. Usuario navega /lotes
2. Selecciona filtros (vista golf, tamaño, rango de precio)
3. Sistema consulta Odoo API → devuelve lotes disponibles en tiempo real
4. Usuario hace click en lote específico
5. Ve: precio, m², vista, renders, ubicación en masterplan
6. Calculadora muestra opciones de pago
7. Click "Quiero este lote" → formulario mínimo (nombre, email, teléfono, país)
8. Lead creado en HubSpot pipeline "Augusta - Cotizaciones"
9. WhatsApp Business notifica al asesor en < 2 minutos
10. Email automático de confirmación al lead (HubSpot sequence)
```

### Integraciones Fase 1

| Integración | Dirección | Propósito |
|---|---|---|
| Odoo REST API | Odoo → Sitio | Inventario y precios en tiempo real |
| HubSpot Forms | Sitio → HubSpot | Captura de leads del cotizador |
| HubSpot Email | HubSpot → Lead | Secuencias de nurturing automáticas |
| WhatsApp Business | HubSpot webhook → WhatsApp | Notificación inmediata al asesor |
| Google Analytics 4 | Sitio → GA4 | Tracking de comportamiento y conversiones |
| Google Search Console | Google → equipo | Indexación y rendimiento SEO |
| Vercel Analytics | Automático | Core Web Vitals en tiempo real |

---

## 8. Fase 2 — Motor de Contenido (Semanas 5-6)

### Canales y Cadencia

| Canal | Formatos | Frecuencia | Audiencia principal |
|---|---|---|---|
| Instagram | Reels + Carruseles + Stories | 5 piezas/semana | Mexicanos 30-55 aspiracionales |
| Facebook | Posts + Lead Ads + Events | 3 piezas/semana | 40-65, familias, inversión |
| TikTok | Reels 15-30s + trends golf | 4 piezas/semana | 28-45 aspiracional, USA/MX |
| LinkedIn | Artículos + posts inversión | 2 piezas/semana | Canadienses/americanos ejecutivos |

**Total:** ~14 piezas de contenido por semana

### 6 Pilares de Contenido

1. **El campo** — lifestyle golf, golden hour, Greg Letsche, el mejor de LATAM
2. **El proyecto** — renders, arquitectura Artigas, amenidades, masterplan
3. **Inversión** — ROI, plusvalía Mérida, financiamiento 36 MSI, preventa
4. **Comunidad** — estilo de vida de compradores, eventos, golf, privada exclusiva
5. **Credibilidad** — portfolio Boma, Country Lakes, Arrecife Sisal, premios
6. **Educativo** — ¿cómo funciona la preventa?, fideicomiso, proceso de compra

**Rotación:** Cada semana usa los 6 pilares distribuidos entre los 4 canales. Nunca dos posts del mismo pilar en el mismo canal en días consecutivos.

### Pipeline de Video Influencers

**Isabela (3 videos/semana — TOFU):**
```
Script → 01_generate_isabela_augusta_stills.py (Arcads Nanobanana 2 Pro)
       → 02_animate_voiceover_combine.py (Veo 3.1 o Seedance 2.0 Pro)
       → Voz Jessica ElevenLabs
       → ffmpeg combine 9:16 final
```
Nota: Usar Veo 3.1 para conservar arquitectura/render en el still. Usar Seedance 2.0 Pro solo si lipsync es prioridad y el backdrop puede cambiar.

**Camila (1 video/semana — BOFU):**
- Misma pipeline, voz Ana María ElevenLabs (m7yTemJqdIqrcNleANfX)
- Formatos: testimonial largo (45-60s), story corta (10-15s)

### Flujo Semanal del Motor de Contenido

```
LUNES — Claude Code genera el Paquete Semanal:
├── 14 piezas: copy + caption + hashtags + canal + fecha/hora sugerida
├── 7 briefs para diseñador: concepto + render a usar + dimensiones + paleta
├── 4 scripts de video: Isabela (3) + Camila (1) con voiceover texto
└── Calendario semanal en formato Buffer-ready CSV

MARTES AM — Jaime recibe notificación WhatsApp:
└── "Paquete de contenido Augusta semana [X] listo para revisión"
└── Link al documento de aprobación

MARTES PM — Jaime aprueba/solicita cambios:
├── Aprueba pieza por pieza o aprueba todo el paquete
└── Cambios específicos por pieza si los hay

MIÉRCOLES AM — Claude Code ejecuta lo aprobado:
├── Genera videos Isabela/Camila (Arcads pipeline)
├── Entrega briefs al diseñador vía carpeta compartida o email
└── Programa publicaciones en Buffer (Wed-Sun schedule)

VIERNES — Reporte de Performance:
└── Ver Fase 3 — Loop de Aprendizaje
```

### Brief para el Diseñador

Cada brief incluye:
- Concepto de la pieza en 1 párrafo
- Render o asset de referencia (ruta específica)
- Dimensiones requeridas por canal
- Paleta de colores del diseño
- Tipografías a usar (Cormorant + Inter)
- Copy principal y secundario
- CTA
- Nota de mood/estilo

---

## 9. Fase 3 — Loop de Aprendizaje (Semanal, desde semana 2)

### Reporte Semanal (cada viernes)

El sistema genera automáticamente un reporte que incluye:

**Performance de contenido:**
- Engagement rate por canal vs semana anterior
- Top 3 piezas por alcance y por engagement
- Bottom 3 piezas (qué no funcionó)
- Mejor pilar de contenido de la semana
- Mejor influencer/formato de video

**Performance de leads:**
- Leads generados (total + por fuente: sitio, IG, FB, TikTok, LI)
- Cotizaciones iniciadas en el sitio
- Tasa de conversión visitante → lead
- Leads en pipeline HubSpot (por etapa)
- Tiempo promedio de respuesta del equipo de ventas

**Performance SEO:**
- Posiciones de keywords objetivo (GSC data)
- Páginas con mayor tráfico orgánico
- Core Web Vitals status

**Inteligencia competitiva:**
- ¿Qué están publicando los competidores esta semana?
- ¿Hay cambios en precios o inventario en proyectos similares?
- Oportunidades detectadas

**Recomendaciones para la siguiente semana:**
- Pilares de contenido a reforzar
- Ajustes de cadencia por canal
- Keywords a atacar con nuevo contenido de blog
- A/B tests sugeridos (headlines, CTAs, formatos)

### Análisis Competitivo (Mensual)

Proyectos a monitorear:
- Desarrollos de lotes frente a campo de golf en México (Querétaro, Jalisco, Yucatán)
- Proyectos premium en preventa en sureste mexicano
- Ofertas de second home para canadienses/americanos en el Caribe mexicano
- Benchmarks de conversión de sitios web inmobiliarios de lujo

Fuentes: sitios web de competidores, redes sociales, portales inmobiliarios (Lamudi, Inmuebles24, Vivanuncios), Google Trends, Apollo.io para datos empresariales.

### Loop de Mejora Continua

```
Semana 1-4:    Establecer baseline de todas las métricas
Semana 5-8:    Optimizar basándose en primeros datos reales
Mes 3+:        A/B testing sistemático de CTAs, headlines, formatos
Trimestral:    Revisión estratégica completa — ¿qué pivots necesitamos?
```

---

## 10. Integraciones Completas

### HubSpot CRM

**Pipeline "Augusta — Ventas":**
```
Interesado (lead web) → Cotizó (abrió cotizador) → Contactado → 
Reunión agendada → Propuesta enviada → Negociación → Cerrado ✓ / Perdido ✗
```

**Secuencias automáticas:**
- Lead nuevo (web): Email bienvenida en ES o EN según país → Follow-up día 3 → Follow-up día 7
- Lead que cotizó: Email con resumen de lote visto + opciones de financiamiento (24h)
- Lead inactivo (>7 días): Re-engagement con nuevo contenido (render, video Camila)

### Odoo ERP

**Sync de inventario:**
- Endpoint REST: consulta en tiempo real de lotes disponibles
- Campos expuestos al sitio: ID lote, estado (disponible/reservado/vendido), precio, m², vista, coordenadas en masterplan
- Actualización automática: cuando Odoo marca lote como reservado, el sitio lo muestra inmediatamente como no disponible

### WhatsApp Business (Augusta)

**Triggers automáticos:**
1. Lead nuevo del cotizador → Notificación al asesor en < 2 min (incluye nombre, interés, lote visto)
2. Lead que no ha sido contactado en > 4 horas → Alerta de seguimiento al equipo
3. Cotización completada → Mensaje de confirmación al lead
4. Nuevo reporte semanal listo → Notificación a Jaime

### Buffer (Social Scheduling)

- Conecta: Instagram Business, Facebook Page, TikTok Business, LinkedIn Company Page
- Claude Code genera el CSV semanal con piezas, captions, hashtags y horarios
- Jaime aprueba en Buffer antes de que salga cualquier pieza
- Horarios óptimos por canal y audiencia (timezone: CST para MX, EST para USA, EST para Canadá)

---

## 11. Flujo de Aprobación (Human-in-the-Loop)

### Jerarquía de Aprobación

| Acción | Requiere aprobación de | Timeout si no responde |
|---|---|---|
| Publicar contenido en redes | Jaime o delegado designado | No publica — espera |
| Cambio en el sitio web | Jaime | No despliega — espera |
| Enviar cotización a lead | Sistema automático (pre-aprobado) | N/A |
| Enviar email de nurturing | Sistema automático (pre-aprobado) | N/A |
| Notificación WhatsApp interna | Sistema automático | N/A |
| Cambio de precio en Odoo | Jaime (en Odoo, no en Claude Code) | N/A |

### Documento de Aprobación Semanal

El sistema genera un Google Doc o Notion page (según preferencia) con:
- Todas las piezas de contenido listadas
- Preview de cada pieza
- Checkbox de aprobación por pieza
- Campo de notas/cambios solicitados
- Botón "Aprobar todo" para agilizar revisión

---

## 12. Métricas de Éxito (KPIs)

### Métricas Principales (North Star)

| Métrica | Objetivo | Frecuencia |
|---|---|---|
| Inventario vendido | 100% antes 31-dic-2026 | Mensual |
| Leads calificados generados | >50/mes | Semanal |
| Cotizaciones completadas | >20/mes | Semanal |
| Tasa de conversión lead→venta | >5% | Mensual |

### Métricas de Canal

| Canal | KPI Principal | Objetivo |
|---|---|---|
| Sitio web | Sesiones orgánicas | +20% mensual |
| Instagram | Reach + Saves | >10K reach/semana |
| TikTok | Views + perfil visits | >50K views/semana |
| Facebook | Lead Ads conversiones | >10 leads/semana |
| LinkedIn | Impressions ejecutivos | >5K/semana |
| Email (HubSpot) | Open rate | >35% |

### Métricas SEO

- Posición #1-3 en Google para "lotes golf Mérida" y variantes (meta: mes 3)
- Aparición en AI Overviews de Google para búsquedas clave (meta: mes 4)
- Mención en respuestas de ChatGPT/Perplexity sobre "invertir en golf México" (meta: mes 5)

---

## 13. Roster de Skills de Claude Code

Invocar con `/skill <nombre>` en sesiones de Claude Code:

| Skill | Cuándo invocar |
|---|---|
| `augusta-website` | Para construir o modificar el sitio Next.js |
| `augusta-seo` | Para auditoría técnica, blog posts, schema markup |
| `augusta-content` | Para generar el paquete semanal de contenido |
| `augusta-video` | Para correr el pipeline Arcads/ElevenLabs/ffmpeg |
| `augusta-crm` | Para configurar/ajustar sequences en HubSpot |
| `augusta-cotizador` | Para actualizar la integración Odoo ↔ sitio |
| `augusta-intel` | Para análisis competitivo y benchmarks |
| `augusta-report` | Para generar el reporte semanal de performance |

---

## 14. Decisiones Pendientes (Fuera del Alcance de Este Documento)

- Credenciales de acceso API de Odoo (endpoint, API key)
- Número de WhatsApp Business Augusta (ya existe — necesita API token)
- Acceso a HubSpot portal ID y API key
- Dominio de hosting en Vercel (transferencia de DNS de augustacountrylakes.mx)
- Inventario exacto de lotes disponibles al momento de lanzar el sitio
- Definición de quién es el "delegado designado" para aprobar contenido cuando Jaime no está disponible
- Presupuesto para Sanity.io (plan Growth ~$99/mes) y Buffer (plan Team ~$120/mes)
