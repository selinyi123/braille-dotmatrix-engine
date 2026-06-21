# Research Notes

Purpose: keep external research close to the repository so future planning avoids repeating basic discovery.

## Scope

Core target remains: visual input to Unicode Braille, tactile dot-matrix exports, ASCII/HTML previews, SVG/PNG/BRF artifacts, validation reports, and future semantic tactile graphics.

## Findings

### 1. Simple image-to-Braille converters

Representative repositories found through GitHub search:

- `Kuuhhl/pictureToBraille`
- `JDaxmaut/photo_to_braille`
- `an0ndev/brailleart`
- `DanielDJones/imgToBraille`

Assessment: these are adjacent but mostly narrower. Basic image-to-Unicode-Braille conversion is already common. This project should not compete only as a simple converter; its differentiation should be physical geometry, reportability, multi-output artifacts, and semantic tactile policy.

### 2. ASCII image converters

Representative repositories found through GitHub search:

- `TheZoraiz/ascii-image-converter`
- `itsPeetah/image-2-text-converter`
- `our0boros/ascii-art-converter`

Assessment: ASCII output is not novel by itself. Keep ASCII as a preview and visual-symbol backend, not as the core identity. Useful ideas to borrow: fast-path rendering, font/terminal aspect calibration, ANSI color handling, and HTML preview ergonomics.

### 3. BrailleRAP and tactile fabrication tools

Representative repositories found through GitHub search:

- `braillerap/DesktopBrailleRAP`
- related forks under other owners

Assessment: this direction is useful for physical output compatibility. Future work should explore embossing, CNC, laser, and print workflows, but avoid overfitting to one device until the geometry and SVG export contracts are stable.

### 4. Chart accessibility and semantic tactile graphics

Relevant research directions:

- Chart4Blind: bitmap chart conversion to accessible SVG, CSV, and alt-text outputs.
- Tactile Vega-Lite: tactile chart generation with tactile-specific abstractions and smart defaults.
- Color-image-to-tactile-graphics algorithms: edge extraction plus texture and region encoding.

Assessment: this is the strongest V2/V3 direction. The next meaningful leap is semantic region mapping, object-edge-text separation, and region-specific tactile policies.

### 5. v1.10.3 research pass: accessible SVG and tactile chart semantics

New sources reviewed for this pass:

- ChartFormer: chart image to tactile-accessible SVGs, with a synthetic Chart2Tactile dataset and pilot evaluation on a refreshable two-dimensional tactile display.
- Tactile Vega-Lite: tactile chart specification layer with tactile-specific abstractions, spacing defaults, textures, line styles, and Braille translation support.
- Chart4Blind: bitmap line-chart conversion into SVG, CSV, and alt-text outputs for embossed prints, laser-cut output, tactile displays, and screen readers.
- Tactile graphics literature: tactile graphics are not equivalent to visual images; they require surface, texture, orientation, elevation, and substrate-aware design.

Assessment for this repository: `v1.10.3` should separate renderer semantics from diagnostics. ASCII previews, chromatic previews, tactile dot exports, and future accessible SVGs are different renderer outputs. Running every output through one Braille-heavy pipeline creates misleading reports and wastes runtime. This motivates the current ASCII fast path and structured report sections.

### 6. v1.11.0 research pass: renderer architecture and vector-output substrate

New sources reviewed for this pass:

- ThorVG: lightweight open-source vector graphics engine with SVG, Lottie, PNG, JPEG, WebP, TTF, and WebAssembly-oriented deployment paths.
- Inkscape extension ecosystem: useful reference for SVG-first workflows and downstream manual editing, but too broad for direct dependency.
- OpenVG / vector graphics acceleration history: reinforces keeping vector output abstractions separate from raster preview code.
- Tactile graphics substrate literature: raised graphics depend on substrate, elevation, texture, orientation, and output device constraints.
- Braille embosser references: embossers are device-specific and can support 6-dot or 8-dot Braille, so renderer strategy should not hard-code one physical output family.

Assessment for this repository: renderer strategy is the correct next architectural step. TACTILE, SCREEN, CHROMATIC, ASCII, future accessible SVG, and future embosser export all require different output policies. A registry-based renderer layer keeps `process_image()` stable while new output families are added.

### 7. v1.12.0 research pass: artifact manifests and interactive tactile outputs

New sources reviewed for this pass:

- TactileNet: AI-generated tactile graphics dataset and framework; useful for future semantic/tactile quality scoring rather than a direct V1 dependency.
- TactIcons: 3D printed tactile map icons; useful for future symbol libraries and tactile legend artifacts.
- FluxMarker: dynamic tactile markers layered on static tactile graphics; useful as evidence that static tactile exports may need companion metadata for interaction or annotation.
- SVG format references: SVG is text/XML-based and open, reinforcing the need for explicit MIME/type/role metadata in artifact reports.
- Stack Overflow, Lobsters, TCS Stack Exchange, Reddit, X/Twitter, Zhihu, and hackathon searches did not surface a stronger direct component than the report/artifact split already planned.

Assessment for this repository: artifact metadata should be explicit, not inferred from file extensions or renderer mode. A dedicated artifact manifest makes future tactile SVG, embosser, interactive marker overlays, and semantic report outputs easier to audit and test.

### 8. v1.13.0 research pass: benchmark profiles and memory reporting

New sources reviewed for this pass:

- scikit-image: confirms that Python image-processing systems benefit from reproducible examples, documented APIs, and scientific benchmark discipline.
- Python memory profiling references: RSS and peak-memory tracking are coarse but useful for CI, while specialized profilers such as Scalene are better left as optional developer tooling.
- Theoretical CS memory references: time and space complexity should be tracked as functions of input size; large image profiles should therefore report pixels, megapixels, and estimated working set.
- External-memory algorithm references: large data pipelines can exceed memory and need explicit profile boundaries; this supports opt-in `medium` and `stress` benchmark profiles rather than making 4K mandatory in PR CI.
- Stack Overflow, Lobsters, Reddit, X/Twitter, Zhihu, hackathon, and TCS Stack Exchange searches did not reveal a stronger direct component than adding benchmark profiles and memory/artifact metrics to the existing benchmark module.

Assessment for this repository: benchmark artifacts should capture input scale, memory estimates, observed RSS, and output size. This is enough for V1 engineering control without prematurely introducing heavyweight profiling dependencies.

### 9. v1.14.0 research pass: embosser boundary and device export separation

New sources reviewed for this pass:

- Braille ASCII / BRF references: six-dot Braille ASCII remains a practical portable text route for many embossing workflows.
- Braille embosser references: embossers can be single-sided or interpoint, and may support 6-dot or 8-dot Braille.
- Unicode Braille references: Unicode covers 6-dot and 8-dot binary appearance, while many embossers still rely on Braille ASCII or device controls.
- Graphics-mode references: some embossers can place dots more freely for diagrams, but these modes are device-specific and not standardized.
- GitHub search found `braillerap/DesktopBrailleRAP` as an open physical embosser/tactile graphics project and `liblouis/liblouis` as the major open-source Braille translation engine.
- Stack Overflow, Lobsters, Reddit, X/Twitter, Zhihu, hackathon, and TCS Stack Exchange searches did not reveal a stronger direct component than adding a neutral export boundary before device-specific exporters.

Assessment for this repository: do not hard-code any single embosser workflow yet. Add a generic embosser profile and export manifest first, then build real BRF or device-specific exporters in later releases.

### 10. v1.15.0 research pass: six-dot text export and pagination

New sources reviewed for this pass:

- Braille ASCII references: the 64 printable characters from ASCII 32 through 95 represent all possible six-dot Braille cells.
- BRF references: BRF files are plain Braille ASCII plus spaces and line/page control characters, making them a practical offline export artifact.
- Unicode Braille references: Unicode Braille supports 8-dot patterns, so six-dot export must explicitly reject dots 7 and 8 instead of dropping them.
- BrlAPI references: direct device APIs are useful later, but v1.15.0 should remain offline text export rather than live device control.
- GitHub, Stack Overflow, Lobsters, Reddit, X/Twitter, Zhihu, hackathon, and TCS Stack Exchange searches did not surface a stronger direct component than implementing a conservative local mapping and diagnostics layer.

Assessment for this repository: implement six-dot BRF-like export as a pure text artifact, not as a translator or device driver. Use the embosser profile from v1.14.0 only for wrapping and pagination.

### 11. v1.16.0 research pass: BRF artifact manifest and CLI integration

New sources reviewed for this pass:

- Braille ASCII references: BRF is a plain artifact format rather than a live device protocol, so it belongs in artifact/report integration before any device API.
- Braille embosser references: embossers vary across single-sided, interpoint, 6-dot, and 8-dot devices, supporting the choice to keep renderer semantics separate from BRF artifact generation.
- BrlAPI references: live braille device control is a different abstraction layer and should remain future work.
- GitHub searches found BRF export examples in adjacent accessibility tooling, but no reusable component that supersedes this repository's existing `write_brf_text()` pipeline-adjacent route.
- Stack Overflow, Lobsters, Reddit, X/Twitter, Zhihu, hackathon, and TCS Stack Exchange searches did not surface a stronger architecture than CLI-level artifact integration plus explicit report diagnostics.

Assessment for this repository: integrate BRF at the artifact boundary. Do not add a new renderer mode. Let CLI generate a BRF-like artifact after rendering, then update `artifact_manifest`, legacy `artifacts`, and `brf_export` in the report JSON.

### 12. v1.17.0 research pass: embosser profile presets

New sources reviewed for this pass:

- Braille page-layout references: common embosser ranges cluster around roughly 34 to 40 cells per line and about 25 lines per page.
- Braille ASCII and BRF references: BRF remains a six-dot, line-oriented offline artifact format, so preset defaults should target predictable line/page capacities.
- Braille embosser references: devices differ by paper size, interpoint behavior, 6-dot/8-dot support, and graphics capability; presets should be metadata defaults rather than vendor drivers.
- GitHub searches for embosser profiles and BRF exporters did not reveal a stronger reusable profile registry component than adding a small in-project preset registry.
- Hacker News, Medium, LinkedIn, Reddit, X/Twitter, Zhihu, Stack Overflow, Lobsters, hackathon, and TCS Stack Exchange searches did not surface a project-specific alternative with better fit than the current preset + override architecture.

Assessment for this repository: add named capacity presets for common page layouts, keep manual overrides, and preserve the driver boundary. `--brf-profile` should select a preset, while `--brf-cols` and `--brf-rows` should remain explicit overrides.

### 13. v1.18.0 research pass: BRF diagnostic severity

New sources reviewed for this pass:

- Braille ASCII / BRF references: BRF files are plain Braille ASCII with line and page controls, so validation should be deterministic and local.
- Unicode Braille references: Unicode can encode 8-dot Braille, but BRF/Braille ASCII is six-dot oriented; dots 7 and 8 must be treated as errors rather than silent lossy export.
- Braille pattern references: U+2800 blank is visually blank but not a normal text space, reinforcing the need for explicit mapping rather than generic whitespace handling.
- GitHub searches for BRF diagnostics and exporter strict modes did not reveal a reusable library that cleanly fits this repository's existing offline artifact path.
- Hacker News, Medium, LinkedIn, Reddit, X/Twitter, Zhihu, Stack Overflow, Lobsters, hackathon, and TCS Stack Exchange searches did not surface a stronger fit than reason-grouped diagnostics and a strict CLI/API path.

Assessment for this repository: keep BRF export local and deterministic. Add warning/error severity, reason grouping, and strict mode. Do not introduce a translator dependency or live device API yet.

## Non-duplication rule for future research

Do not repeat generic `image to braille converter` discovery unless checking for major new repositories. New research should focus on one slice per pass:

1. semantic tactile chart engines,
2. embossing-machine output formats,
3. tactile geometry readability standards,
4. dot-density and collision validation,
5. segmentation-assisted tactile policy,
6. fast raster/vector backends,
7. benchmark datasets for tactile graphics,
8. artifact manifests and interactive tactile metadata,
9. benchmark profiles, memory models, and artifact-size accounting,
10. embosser page profiles, BRF export, and device-specific graphics modes,
11. BRF pagination, six-dot compatibility diagnostics, and optional translator integration,
12. BRF artifact/report contracts and CLI ergonomics,
13. embosser profile presets, page-size capacity defaults, and profile override ergonomics,
14. BRF diagnostic severity, strict export policy, and reason-grouped report contracts.
