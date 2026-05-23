"""Sistema de diseño SVA-EPS.

Identidad visual inspirada en los Programas para el Bienestar de México:
guinda/vino institucional + dorado, sobre fondo papel cálido. Tipografía
editorial (Fraunces display + Geist Sans). Nada de negro genérico.
"""
from __future__ import annotations

# --- Paleta ---
GUINDA = "#9d2449"       # vino institucional
GUINDA_OSCURO = "#611232"
DORADO = "#a57f2c"
DORADO_CLARO = "#c9a227"
PAPEL = "#f7f3ec"        # fondo cálido
PAPEL_CARD = "#fffdf9"
TINTA = "#1c1a17"        # texto principal
TINTA_SUAVE = "#6b6357"
VERDE = "#3d6b35"
ROJO = "#b3261e"
AMBAR = "#b8860b"

# Fuentes desde Google Fonts (Fraunces editorial + Geist Sans)
FONT_LINKS = [
    "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,900&family=Geist:wght@300;400;500;600;700&display=swap",
]

# CSS global: fondo con textura, tipografía, scrollbar, micro-animaciones.
GLOBAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,900&family=Geist:wght@300;400;500;600;700&display=swap');

:root {
  --guinda: #9d2449;
  --guinda-oscuro: #611232;
  --dorado: #a57f2c;
  --dorado-claro: #c9a227;
  --papel: #f7f3ec;
  --papel-card: #fffdf9;
  --tinta: #1c1a17;
  --tinta-suave: #6b6357;
}

html, body {
  background-color: var(--papel);
  background-image:
    radial-gradient(circle at 12% 18%, rgba(157,36,73,0.06), transparent 42%),
    radial-gradient(circle at 88% 78%, rgba(165,127,44,0.07), transparent 45%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  color: var(--tinta);
  font-family: 'Geist', sans-serif;
}

h1, h2, h3, h4, .display {
  font-family: 'Fraunces', Georgia, serif !important;
  letter-spacing: -0.01em;
}

::-webkit-scrollbar { width: 11px; height: 11px; }
::-webkit-scrollbar-track { background: var(--papel); }
::-webkit-scrollbar-thumb {
  background: var(--guinda); border-radius: 6px;
  border: 2px solid var(--papel);
}

@keyframes rise {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.rise { animation: rise 0.5s cubic-bezier(0.22,1,0.36,1) both; }
.rise-1 { animation-delay: 0.05s; }
.rise-2 { animation-delay: 0.12s; }
.rise-3 { animation-delay: 0.20s; }

@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(157,36,73,0.45); }
  70%  { box-shadow: 0 0 0 12px rgba(157,36,73,0); }
  100% { box-shadow: 0 0 0 0 rgba(157,36,73,0); }
}
.pulse { animation: pulse-ring 1.8s infinite; }

@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
.shimmer {
  background: linear-gradient(90deg, transparent, rgba(165,127,44,0.18), transparent);
  background-size: 800px 100%;
  animation: shimmer 1.6s infinite;
}

.card-paper {
  background: var(--papel-card);
  border: 1px solid rgba(28,26,23,0.08);
  border-radius: 18px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.8) inset,
              0 12px 30px -18px rgba(28,26,23,0.30);
}
.card-paper:hover { box-shadow: 0 18px 40px -20px rgba(157,36,73,0.35); }

.kicker {
  font-family: 'Geist', sans-serif;
  font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--guinda);
}

.btn-guinda {
  background: linear-gradient(135deg, var(--guinda), var(--guinda-oscuro));
  color: #fff !important; border: none;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 20px -10px rgba(157,36,73,0.7);
}
.btn-guinda:hover:not(:disabled) { transform: translateY(-2px); }
.btn-guinda:disabled { opacity: 0.4; cursor: not-allowed; }

.dropzone {
  border: 2px dashed rgba(157,36,73,0.4);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(157,36,73,0.03), transparent);
  transition: all 0.2s ease;
}
.dropzone:hover { border-color: var(--guinda); background: rgba(157,36,73,0.06); }
"""
