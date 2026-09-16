# UMI-Prior Website Design System

This site adapts the public `umi-on-legs.github.io` academic-project template at commit `4aa985b61444492b6a7eb6318a0ba13acb7a1258`. It preserves the template's Bulma-style semantic layout vocabulary through a small local CSS subset; the content, media, color system, and responsive behavior are specific to UMI-Prior.

## 1. Atmosphere & Identity

The page should feel like a robotics demonstration first and a paper abstract second: immediate, physical, and technically credible. Its signature is a full-bleed real-robot hero framed by a cobalt-to-cyan signal color, followed by calm white editorial sections and one dark system section that makes the three-stage control hierarchy easy to remember.

## 2. Color

| Role | Token | Value | Usage |
|---|---|---:|---|
| Hero cobalt | `--color-cobalt` | `#1464f4` | Primary accent and links |
| Hero cobalt dark | `--color-cobalt-dark` | `#0c46b7` | Hover and dark gradient stop |
| Signal cyan | `--color-cyan` | `#42d5ff` | Secondary hero light and focus |
| Ink | `--color-ink` | `#151923` | Headings and body text |
| Ink soft | `--color-ink-soft` | `#4b5565` | Supporting copy |
| Paper | `--color-paper` | `#ffffff` | Main surface |
| Mist | `--color-mist` | `#f4f7fb` | Alternate section surface |
| Line | `--color-line` | `#dce3ee` | Borders and dividers |
| Night | `--color-night` | `#0a1020` | System section and footer |
| Night soft | `--color-night-soft` | `#151e35` | Elevated dark surface |
| Positive | `--color-positive` | `#087150` | Quantitative success cues |
| White | `--color-white` | `#ffffff` | Text on dark/video surfaces |

Transparent surface, overlay, badge, and text variants use named opacity tokens derived from these base roles (`--color-white-*`, `--color-hero-*`, `--color-cobalt-*`, `--color-cyan-04`, and `--color-positive-10`). Shadows are likewise centralized as `--shadow-*` tokens.

Accent color is reserved for links, focus, quantitative highlights, and active navigation. Media supplies the visual variety; UI chrome stays within the cobalt/cyan ramp.

## 3. Typography

| Level | Token | Size | Weight | Line Height | Usage |
|---|---|---:|---:|---:|---|
| Display | `--type-display` | `clamp(4rem, 12vw, 10rem)` | 700 | 0.9 | `UMI-Prior` hero wordmark |
| Hero subtitle | `--type-hero-subtitle` | `clamp(1.45rem, 4vw, 3.4rem)` | 600 | 1.08 | Full paper subtitle |
| Section title | `--type-section` | `clamp(2rem, 4vw, 3.25rem)` | 700 | 1.1 | Primary section headings |
| Subsection | `--type-subsection` | `clamp(1.25rem, 2.4vw, 1.75rem)` | 700 | 1.25 | Cards and subsection headings |
| Lead | `--type-lead` | `clamp(1.1rem, 1.8vw, 1.35rem)` | 400 | 1.65 | Overview statement |
| Body | `--type-body` | `1rem` | 400 | 1.7 | Main copy |
| Small | `--type-small` | `0.875rem` | 500 | 1.5 | Captions and metadata |
| Overline | `--type-overline` | `0.75rem` | 700 | 1.4 | Uppercase section labels |

Primary stack: `"Noto Sans", "Helvetica Neue", Arial, sans-serif`. Mono stack: `"SFMono-Regular", Consolas, "Liberation Mono", monospace`. The page uses no remote fonts.

## 4. Spacing & Layout

Base unit: 4px.

| Token | Value | Usage |
|---|---:|---|
| `--space-1` | `0.25rem` | Icon details |
| `--space-2` | `0.5rem` | Inline gaps |
| `--space-3` | `0.75rem` | Compact controls |
| `--space-4` | `1rem` | Standard gap |
| `--space-6` | `1.5rem` | Card and cluster spacing |
| `--space-8` | `2rem` | Media spacing |
| `--space-12` | `3rem` | Section interior rhythm |
| `--space-16` | `4rem` | Mobile section rhythm |
| `--space-24` | `6rem` | Desktop section rhythm |

Maximum editorial width is 960px; wide technical media may expand to 1180px. The responsive layout follows the template's Bulma-style tablet boundary: mobile behavior runs through 768px and the wider grid begins at 769px. Mobile uses one column and horizontally scrollable anchor tabs; desktop media grids use two columns.

## 5. Components

### Resource Button
- **Structure**: anchor with icon slot and text label.
- **Variants**: solid dark, outline/inverted, compact nav.
- **Spacing**: `--space-2`, `--space-3`, `--space-4`.
- **States**: default, hover (contrast shift + 2px lift), active (returns to rest), focus-visible (cyan ring), disabled (`aria-disabled`, reduced opacity).
- **Accessibility**: native anchor semantics, descriptive label, 44px minimum target.
- **Motion**: 160ms transform/color transition; disabled under reduced motion.
- **Layout**: inline cluster that wraps on mobile.

### Anchor Tabs
- **Structure**: navigation landmark containing in-page anchors.
- **Variants**: transparent hero footer; sticky white document bar.
- **States**: default, hover, focus-visible, active section.
- **Accessibility**: horizontal scrolling preserves every item; no clipped links.
- **Motion**: color/background only, 160ms.
- **Layout**: scrollable cluster on mobile, centered row on desktop.

### Section Heading
- **Structure**: overline, heading, optional lead paragraph.
- **Variants**: light and dark.
- **Accessibility**: semantic heading order; max line length prevents awkward wrapping.
- **Motion**: none.
- **Layout**: centered stack, left-aligned supporting text.

### Media Frame
- **Structure**: figure containing image or video and optional caption.
- **Variants**: wide technical figure, task tile, hero background.
- **Asset policy**: paper figures are served as SVG so text and line art stay sharp at any zoom; photographic robot demonstrations remain native video or raster posters because their source pixels are not vector data. Task demos preserve the complete source duration and use 16:9 encodes; the hero cover may use a shorter loop.
- **States**: video play/pause is driven by viewport visibility; native controls remain available outside autoplay hero.
- **Accessibility**: meaningful `alt`, captions, fixed aspect ratio, no unexpected audio.
- **Motion**: media itself does not animate as decoration; playback communicates the robot behavior.
- **Layout**: fluid frame with 12px radius for content media; hero remains edge-to-edge.

### Vector Figure Link
- **Structure**: a full-frame anchor wrapping an SVG paper figure with a persistent “Open full-size SVG” action row.
- **States**: default, hover lift, focus-visible cyan ring, and native visited-link behavior suppressed so the action stays within the cobalt/night palette.
- **Accessibility**: the visible chip identifies the zoom affordance; each anchor label names the figure and announces that it opens in a new tab.
- **Motion**: adapts the beui.dev `expanding-arrow-button` affordance mechanism as a restrained 160ms label lift; reduced-motion removes the transform.
- **Layout**: the inline figure remains responsive, while opening the raw SVG gives mobile users native pinch-zoom and pan at full resolution.

### Metric Strip
- **Structure**: definition list with value and label pairs.
- **Variants**: light and dark.
- **Accessibility**: text conveys values without relying on color.
- **Motion**: none.
- **Layout**: two columns on mobile, four columns on desktop.

### Task Card
- **Structure**: media frame, task title, result badge, explanatory copy.
- **Variants**: quantitative and qualitative.
- **States**: links within cards use Resource Button states; card itself is not falsely interactive.
- **Accessibility**: heading, result text, and caption remain in the DOM.
- **Motion**: none on the non-interactive card.
- **Layout**: two-column responsive grid.

## 6. Motion & Interaction

| Type | Duration | Easing | Usage |
|---|---:|---|---|
| Micro | 160ms | `ease-out` | Buttons and anchor tabs |
| Standard | 240ms | `ease-in-out` | Sticky bar surface transition |
| Emphasis | 500ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Hero copy entrance only |

The hero entrance is the single signature motion. All other motion communicates affordance or video playback. Only `transform` and `opacity` animate. `prefers-reduced-motion: reduce` removes smooth scrolling, hero entrance, and transforms.

## 7. Depth & Surface

Strategy: mixed, following the source template's full-bleed video/overlay plus paper-like content sections. The hero uses a real video, a dark cobalt overlay, and a subtle top/bottom vignette. Content media uses a soft cobalt-tinted shadow and a `--color-line` border; non-interactive text sections rely on negative space rather than card containers.

| Token | Value | Usage |
|---|---|---|
| `--shadow-media` | `0 20px 55px rgba(30, 70, 140, 0.16)` | Wide technical media |
| `--shadow-button` | `0 10px 24px rgba(7, 20, 48, 0.2)` | Solid buttons on hero |

## 8. Accessibility Constraints & Accepted Debt

### Constraints
- WCAG 2.2 AA target with 4.5:1 body-text and 3:1 large-text contrast.
- Every interactive element has a visible `:focus-visible` state.
- Page landmarks, heading hierarchy, link purpose, captions, and alt text are explicit.
- Layout reflows at 375px with no primary-content horizontal overflow.
- Video is muted when autoplayed, supports pause through native controls outside the hero, and uses posters.
- Reduced-motion users receive static transitions and no smooth scrolling.

### Accepted Debt

| Item | Location | Why accepted | Owner / Exit |
|---|---|---|---|
| Anonymous author identity | Hero metadata | The paper is in anonymous-review form | Replace after de-anonymization |
| Code/arXiv links omitted | Resource cluster | No public URLs are present in the manuscript | Add when public artifacts exist |
