# 苔の巨人 — The Moss Giant Awakens

A ~64-second hand-drawn-style 2D anime short, delivered as one self-contained HTML file:
[`moss-giant-awakens.html`](moss-giant-awakens.html). Open it in a desktop browser
(Chrome, Edge, Firefox, Safari), wait for the background paintings to finish, then press **上映 ▶**.

Nothing is loaded from the network: every background, cel, effect and sound is generated
in the page at load time.

## Controls

| Key | Action |
| --- | --- |
| Space / click | pause · resume |
| ← / → | step one frame (Shift: one second) |
| R | restart |
| M | sound on/off |

While paused, the bar at the bottom shows the time, frame number and cut.

## How it is made

- **Backgrounds (美術):** each cut has its own painting, generated once with gouache-style
  dabs, dry-brush strokes and paper grain: misty forest depth layers, buttressed trunks,
  backlit canopy masses, cumulus skies, the forest sea at sunrise.
- **Cels (セル):** the robot is an original design, drawn as a 2D rig of inked parts.
  It has hand-ink lines with pressure and taper and hard-edged cel shadows. Moss, grime
  and rust are painted textures, and the moss grew only on the surfaces that faced the sky
  while it knelt.
- **Timing:** characters animate on twos and threes with holds. The camera moves on ones,
  sliding over the held cels the way an anime camera stand does.
- **Compositing (撮影):** light shafts, diffusion, glow, film grain, flash frames and shake.
- **Sound:** a short original score with forest ambience, birdsong and machine sounds,
  synthesized with WebAudio.
