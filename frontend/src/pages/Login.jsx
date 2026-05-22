import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './Login.module.css';

/* ── Color constants for SVG illustrations ── */
const TEAL      = '#03C4CE';
const TEAL_DARK = '#027F88';
const INDIGO    = '#6378F0';
const INK       = '#0E1A2B';
const MUTED     = '#64748B';

/* ── Inline SVG icons (no external deps needed for login) ── */
function IconBrain({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z" />
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
    </svg>
  );
}
function IconEye({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}
function IconEyeOff({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}
function IconLoader({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.spinIcon}>
      <line x1="12" y1="2" x2="12" y2="6" /><line x1="12" y1="18" x2="12" y2="22" />
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" /><line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
      <line x1="2" y1="12" x2="6" y2="12" /><line x1="18" y1="12" x2="22" y2="12" />
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" /><line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
    </svg>
  );
}
function IconAlert() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

/* ── Scene SVG illustrations ── */
function Scene1({ className }) {
  return (
    <svg className={className} viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="180" cy="180" r="140" fill={TEAL} opacity="0.08" />
      <g transform="translate(36, 96)">
        <rect x="0" y="0" width="150" height="100" rx="14" fill="#fff" stroke={INK} strokeWidth="2" />
        <rect x="14" y="16" width="60" height="6" rx="3" fill={INK} opacity="0.85" />
        <rect x="14" y="28" width="38" height="4" rx="2" fill={MUTED} opacity="0.45" />
        <path d="M14 76 L30 64 L46 68 L62 54 L80 48 L98 56 L116 44 L136 38 L136 84 L14 84 Z" fill={TEAL} opacity="0.25" />
        <path d="M14 76 L30 64 L46 68 L62 54 L80 48 L98 56 L116 44 L136 38" stroke={TEAL_DARK} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="136" cy="38" r="3" fill={TEAL_DARK} />
        <rect x="96" y="14" width="44" height="16" rx="8" fill="rgba(3,196,206,0.15)" />
        <text x="118" y="25" textAnchor="middle" fontFamily="'JetBrains Mono', monospace" fontSize="9" fontWeight="700" fill={TEAL_DARK}>+18%</text>
      </g>
      <g>
        <path d="M280 90 Q260 70 268 50 Q290 62 290 88 Z" fill={TEAL} opacity="0.5" stroke={INK} strokeWidth="1.6" strokeLinejoin="round">
          <animateTransform attributeName="transform" type="rotate" values="-3 280 90;3 280 90;-3 280 90" dur="5s" repeatCount="indefinite" />
        </path>
        <path d="M296 118 Q286 98 302 84 Q314 100 310 120 Z" fill={TEAL_DARK} opacity="0.85" stroke={INK} strokeWidth="1.6" strokeLinejoin="round">
          <animateTransform attributeName="transform" type="rotate" values="3 300 110;-3 300 110;3 300 110" dur="4.4s" repeatCount="indefinite" />
        </path>
        <path d="M62 220 Q46 216 44 200 Q64 198 72 216 Z" fill={TEAL} opacity="0.55" stroke={INK} strokeWidth="1.6" strokeLinejoin="round">
          <animateTransform attributeName="transform" type="rotate" values="-3 58 210;3 58 210;-3 58 210" dur="4.8s" repeatCount="indefinite" />
        </path>
      </g>
      <ellipse cx="200" cy="300" rx="120" ry="26" fill="#F3EEFD" />
      <g>
        <path d="M170 296 Q184 280 208 280 Q236 280 250 296 L250 306 Q210 310 170 306 Z" fill="#3A4A6E" stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
        <ellipse cx="178" cy="300" rx="10" ry="4" fill={INK} />
        <ellipse cx="242" cy="300" rx="10" ry="4" fill={INK} />
      </g>
      <g>
        <path d="M172 290 Q166 236 210 228 Q254 236 248 290 Z" fill={TEAL} stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
        <path d="M210 250 Q198 238 188 248 Q178 260 210 282 Q242 260 232 248 Q222 238 210 250 Z" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinejoin="round" />
        <rect x="204" y="218" width="12" height="14" fill="#fff" stroke={INK} strokeWidth="2" />
      </g>
      <g>
        <ellipse cx="210" cy="200" rx="26" ry="28" fill="#fff" stroke={INK} strokeWidth="2.2" />
        <path d="M198 198 Q202 202 206 198" stroke={INK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M214 198 Q218 202 222 198" stroke={INK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <circle cx="196" cy="208" r="3" fill={TEAL} opacity="0.4" />
        <circle cx="224" cy="208" r="3" fill={TEAL} opacity="0.4" />
        <path d="M204 212 Q210 218 216 212" stroke={INK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      </g>
      <g>
        <path d="M176 246 Q150 220 140 190" stroke={TEAL} strokeWidth="14" fill="none" strokeLinecap="round" />
        <path d="M176 246 Q150 220 140 190" stroke={INK} strokeWidth="2.2" fill="none" strokeLinecap="round" />
        <circle cx="140" cy="190" r="8" fill="#fff" stroke={INK} strokeWidth="2" />
        <path d="M244 246 Q270 220 280 190" stroke={TEAL} strokeWidth="14" fill="none" strokeLinecap="round" />
        <path d="M244 246 Q270 220 280 190" stroke={INK} strokeWidth="2.2" fill="none" strokeLinecap="round" />
        <circle cx="280" cy="190" r="8" fill="#fff" stroke={INK} strokeWidth="2" />
      </g>
      <g>
        <path d="M120 140 Q114 134 108 138 Q104 144 120 156 Q136 144 132 138 Q126 134 120 140 Z" fill={TEAL_DARK}>
          <animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite" />
          <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="3s" repeatCount="indefinite" additive="sum" />
        </path>
        <path d="M306 170 Q301 164 297 168 Q293 174 306 184 Q319 174 315 168 Q311 164 306 170 Z" fill={INDIGO}>
          <animate attributeName="opacity" values="0.5;1;0.5" dur="3.4s" repeatCount="indefinite" />
          <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="3.4s" repeatCount="indefinite" additive="sum" />
        </path>
      </g>
      <g>
        <circle cx="60" cy="130" r="2.5" fill={INDIGO}><animate attributeName="opacity" values="0.2;1;0.2" dur="2.4s" repeatCount="indefinite" /></circle>
        <circle cx="320" cy="260" r="2" fill={TEAL}><animate attributeName="opacity" values="0.2;1;0.2" dur="2.8s" repeatCount="indefinite" /></circle>
        <circle cx="40" cy="270" r="2.5" fill={TEAL}><animate attributeName="opacity" values="0.2;1;0.2" dur="2.6s" repeatCount="indefinite" /></circle>
      </g>
    </svg>
  );
}

function Scene2({ className }) {
  return (
    <svg className={className} viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="180" cy="175" r="140" fill={INDIGO} opacity="0.08" />
      <rect x="170" y="120" width="150" height="105" rx="14" fill="#fff" stroke={INK} strokeWidth="2" />
      <text x="184" y="144" fontFamily="'JetBrains Mono', monospace" fontSize="9" fill={MUTED} letterSpacing="0.04em">CLIMA · Q2</text>
      <rect x="184" y="190" width="14" height="22" rx="2" fill={TEAL} opacity="0.55">
        <animate attributeName="height" values="10;22;16;22" dur="3.5s" repeatCount="indefinite" />
        <animate attributeName="y" values="202;190;196;190" dur="3.5s" repeatCount="indefinite" />
      </rect>
      <rect x="204" y="175" width="14" height="37" rx="2" fill={TEAL}>
        <animate attributeName="height" values="30;37;33;37" dur="3.5s" repeatCount="indefinite" begin="0.2s" />
        <animate attributeName="y" values="182;175;179;175" dur="3.5s" repeatCount="indefinite" begin="0.2s" />
      </rect>
      <rect x="224" y="165" width="14" height="47" rx="2" fill={TEAL_DARK}>
        <animate attributeName="height" values="40;47;44;47" dur="3.5s" repeatCount="indefinite" begin="0.4s" />
        <animate attributeName="y" values="172;165;168;165" dur="3.5s" repeatCount="indefinite" begin="0.4s" />
      </rect>
      <rect x="244" y="155" width="14" height="57" rx="2" fill={INDIGO}>
        <animate attributeName="height" values="48;57;52;57" dur="3.5s" repeatCount="indefinite" begin="0.6s" />
        <animate attributeName="y" values="164;155;160;155" dur="3.5s" repeatCount="indefinite" begin="0.6s" />
      </rect>
      <rect x="264" y="170" width="14" height="42" rx="2" fill={INDIGO} opacity="0.6">
        <animate attributeName="height" values="36;42;38;42" dur="3.5s" repeatCount="indefinite" begin="0.8s" />
        <animate attributeName="y" values="176;170;174;170" dur="3.5s" repeatCount="indefinite" begin="0.8s" />
      </rect>
      <rect x="284" y="180" width="14" height="32" rx="2" fill={INDIGO} opacity="0.4">
        <animate attributeName="height" values="25;32;28;32" dur="3.5s" repeatCount="indefinite" begin="1s" />
        <animate attributeName="y" values="187;180;184;180" dur="3.5s" repeatCount="indefinite" begin="1s" />
      </rect>
      <path d="M186 178 L202 172 L222 164 L242 158 L260 170 L280 176" stroke={TEAL_DARK} strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="280" cy="176" r="3" fill={TEAL_DARK} />
      <ellipse cx="120" cy="310" rx="60" ry="6" fill={INK} opacity="0.08" />
      <path d="M105 305 L108 250 L130 250 L126 305" fill="#fff" stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
      <path d="M100 306 L115 306" stroke={INK} strokeWidth="3" strokeLinecap="round" />
      <path d="M122 306 L138 306" stroke={INK} strokeWidth="3" strokeLinecap="round" />
      <path d="M92 255 Q92 215 118 210 Q146 215 144 255 L140 262 Q118 268 96 262 Z" fill={INDIGO} stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
      <path d="M110 210 L118 220 L126 210" stroke="#fff" strokeWidth="1.8" fill="none" />
      <path d="M138 230 Q170 210 196 170" stroke={INK} strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <circle cx="196" cy="170" r="5" fill="#fff" stroke={INK} strokeWidth="2" />
      <path d="M96 230 Q82 240 80 258" stroke={INK} strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <rect x="62" y="252" width="30" height="22" rx="3" fill="#fff" stroke={INK} strokeWidth="2" />
      <rect x="66" y="256" width="22" height="3" rx="1" fill={TEAL} />
      <rect x="66" y="262" width="16" height="3" rx="1" fill={MUTED} opacity="0.5" />
      <rect x="66" y="268" width="20" height="3" rx="1" fill={MUTED} opacity="0.5" />
      <circle cx="118" cy="188" r="22" fill="#fff" stroke={INK} strokeWidth="2.2" />
      <path d="M98 185 Q98 166 118 164 Q138 166 138 185 Q136 176 128 174 Q118 172 108 174 Q100 176 98 185 Z" fill={INK} />
      <circle cx="112" cy="188" r="4" fill="none" stroke={INK} strokeWidth="1.6" />
      <circle cx="124" cy="188" r="4" fill="none" stroke={INK} strokeWidth="1.6" />
      <path d="M116 188 L120 188" stroke={INK} strokeWidth="1.6" />
      <path d="M114 198 Q118 201 122 198" stroke={INK} strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <g transform="translate(290, 90)">
        <circle r="18" fill="#fff" stroke={TEAL} strokeWidth="2" />
        <path d="M-7 0 L-2 5 L8 -5" stroke={TEAL_DARK} strokeWidth="2.4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        <animateTransform attributeName="transform" type="translate" values="290 90; 290 82; 290 90" dur="3s" repeatCount="indefinite" additive="replace" />
      </g>
      <circle cx="60" cy="130" r="3" fill={TEAL}><animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" /></circle>
      <circle cx="75" cy="155" r="2.5" fill={INDIGO}><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" repeatCount="indefinite" /></circle>
    </svg>
  );
}

function Scene3({ className }) {
  return (
    <svg className={className} viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="180" cy="180" r="140" fill={TEAL} opacity="0.08" />
      <rect x="100" y="80" width="160" height="200" rx="14" fill="#fff" stroke={INK} strokeWidth="2.2" />
      <rect x="150" y="72" width="60" height="18" rx="4" fill={INK} />
      <rect x="158" y="76" width="44" height="10" rx="2" fill="#fff" />
      <rect x="116" y="102" width="90" height="7" rx="2" fill={INK} opacity="0.85" />
      <rect x="116" y="114" width="60" height="5" rx="2" fill={MUTED} opacity="0.4" />
      {[0, 1, 2, 3].map((i) => (
        <g key={i} transform={`translate(116, ${138 + i * 30})`}>
          <circle cx="7" cy="7" r="8" fill={i < 3 ? TEAL : '#fff'} stroke={i < 3 ? TEAL_DARK : MUTED} strokeWidth="1.6" />
          {i < 3 && <path d="M3 7 L6 10 L12 4" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />}
          <rect x="24" y="3" width={i === 0 ? 110 : i === 1 ? 95 : i === 2 ? 120 : 80} height="4" rx="2" fill={i < 3 ? INK : MUTED} opacity={i < 3 ? 0.75 : 0.45} />
          <rect x="24" y="10" width={i === 0 ? 70 : i === 1 ? 55 : i === 2 ? 80 : 45} height="3" rx="2" fill={MUTED} opacity="0.4" />
        </g>
      ))}
      <rect x="116" y="258" width="128" height="6" rx="3" fill={INK} opacity="0.08" />
      <rect x="116" y="258" width="96" height="6" rx="3" fill={TEAL_DARK}>
        <animate attributeName="width" values="0;96" dur="1.8s" fill="freeze" />
      </rect>
      <ellipse cx="265" cy="315" rx="56" ry="6" fill={INK} opacity="0.08" />
      <path d="M248 310 L252 258 L274 258 L270 310" fill="#fff" stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
      <path d="M244 311 L258 311" stroke={INK} strokeWidth="3" strokeLinecap="round" />
      <path d="M266 311 L282 311" stroke={INK} strokeWidth="3" strokeLinecap="round" />
      <path d="M238 262 Q238 222 262 218 Q288 222 286 262 L282 268 Q262 272 242 268 Z" fill={TEAL} stroke={INK} strokeWidth="2.2" strokeLinejoin="round" />
      <path d="M244 238 Q226 232 220 218" stroke={INK} strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <g transform="translate(218, 214) rotate(-30)">
        <rect x="-3" y="-14" width="6" height="18" rx="1" fill={INDIGO} stroke={INK} strokeWidth="1.6" />
        <path d="M-3 4 L0 8 L3 4 Z" fill={INK} />
      </g>
      <path d="M282 238 Q296 244 298 256" stroke={INK} strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <circle cx="298" cy="258" r="5" fill="#fff" stroke={INK} strokeWidth="2" />
      <circle cx="262" cy="196" r="22" fill="#fff" stroke={INK} strokeWidth="2.2" />
      <circle cx="262" cy="174" r="8" fill={INK} />
      <path d="M242 192 Q244 176 262 174 Q280 176 282 192 Q280 184 272 182 Q262 180 252 182 Q244 184 242 192 Z" fill={INK} />
      <circle cx="256" cy="197" r="1.6" fill={INK} />
      <circle cx="268" cy="197" r="1.6" fill={INK} />
      <path d="M258 205 Q262 208 266 205" stroke={INK} strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <g transform="translate(70, 140)">
        <circle r="26" fill="#fff" stroke={INDIGO} strokeWidth="2" strokeDasharray="3 2" />
        <text textAnchor="middle" y="-3" fontFamily="'JetBrains Mono', monospace" fontSize="7" fill={INDIGO} fontWeight="700">NOM</text>
        <text textAnchor="middle" y="8" fontFamily="'JetBrains Mono', monospace" fontSize="9" fill={INDIGO} fontWeight="700">035</text>
        <animateTransform attributeName="transform" type="rotate" from="0 70 140" to="360 70 140" dur="18s" repeatCount="indefinite" additive="sum" />
      </g>
      <g fill={TEAL}>
        <circle cx="60" cy="220" r="2.5"><animate attributeName="opacity" values="0.2;1;0.2" dur="2s" repeatCount="indefinite" /></circle>
        <circle cx="80" cy="250" r="2"><animate attributeName="opacity" values="0.2;1;0.2" dur="2.5s" repeatCount="indefinite" /></circle>
        <circle cx="305" cy="100" r="3" fill={INDIGO}><animate attributeName="opacity" values="0.2;1;0.2" dur="2.2s" repeatCount="indefinite" /></circle>
      </g>
    </svg>
  );
}

/* ── Float info cards ── */
function FloatCard1({ className }) {
  return (
    <div className={className} style={{ bottom: 28, left: 20 }}>
      <div className={styles.fcIcon} style={{ background: 'rgba(3,196,206,0.12)', color: TEAL_DARK }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
      </div>
      <div>
        <div className={styles.fcTitle}>Clima laboral</div>
        <div className={styles.fcSub}>12 áreas · sano</div>
      </div>
      <div className={styles.ring}>
        <svg width="30" height="30" viewBox="0 0 30 30">
          <circle cx="15" cy="15" r="12" stroke="rgba(3,196,206,0.18)" strokeWidth="3" fill="none" />
          <circle cx="15" cy="15" r="12" stroke={TEAL_DARK} strokeWidth="3" fill="none" strokeLinecap="round" strokeDasharray="75.4" strokeDashoffset="15.8" />
        </svg>
        <div className={styles.ringPct}>79%</div>
      </div>
    </div>
  );
}

function FloatCard2({ className }) {
  return (
    <div className={className} style={{ top: 28, right: 18 }}>
      <div className={styles.fcIcon} style={{ background: 'rgba(99,120,240,0.14)', color: INDIGO }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <path d="M9 9h6v6H9z" />
        </svg>
      </div>
      <div>
        <div className={styles.fcTitle}>+18% respuestas</div>
        <div className={styles.fcSub}>últimos 7 días</div>
      </div>
    </div>
  );
}

function FloatCard3({ className }) {
  return (
    <div className={className} style={{ bottom: 28, right: 18 }}>
      <div className={styles.fcIcon} style={{ background: 'rgba(3,196,206,0.12)', color: TEAL_DARK }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <path d="M22 4L12 14.01l-3-3" />
        </svg>
      </div>
      <div>
        <div className={styles.fcTitle}>3 de 4 requisitos</div>
        <div className={styles.fcSub}>auditoría lista</div>
      </div>
    </div>
  );
}

/* ── Scene config (module-level — styles is imported at top) ── */
const SCENES = [
  {
    Svg: Scene1,
    Card: FloatCard1,
    text: <>Bienestar psicosocial, <span className={styles.accent}>medido y accionable</span></>,
  },
  {
    Svg: Scene2,
    Card: FloatCard2,
    text: <>Diagnósticos NOM-035 <span className={styles.accent}>en tiempo real</span></>,
  },
  {
    Svg: Scene3,
    Card: FloatCard3,
    text: <>Cumplimiento documentado, <span className={styles.accent}>sin hojas de cálculo</span></>,
  },
];

/* ── Illustration pane with auto-rotating carousel ── */
function IllustrationPane() {
  const [idx, setIdx] = useState(0);
  const [prevIdx, setPrevIdx] = useState(null);
  const timerRef = useRef(null);

  const go = (newIdx) => {
    if (newIdx === idx) return;
    setPrevIdx(idx);
    setIdx(newIdx);
    setTimeout(() => setPrevIdx(null), 800);
  };

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      go((idx + 1) % SCENES.length);
    }, 5000);
    return () => clearTimeout(timerRef.current);
  });

  return (
    <div className={styles.right}>
      <div className={styles.stage}>
        {SCENES.map((S, i) => {
          const cls = [
            styles.scene,
            i === idx     ? styles.sceneIn  : '',
            i === prevIdx ? styles.sceneOut : '',
          ].join(' ');
          return (
            <div key={i} className={cls}>
              <S.Svg className={styles.sceneSvg} />
              <S.Card className={styles.floatCard} />
            </div>
          );
        })}
      </div>

      <div className={styles.caption}>
        {SCENES.map((S, i) => {
          const cls = [
            styles.capText,
            i === idx     ? styles.capTextIn  : '',
            i === prevIdx ? styles.capTextOut : '',
          ].join(' ');
          return <div key={i} className={cls}>{S.text}</div>;
        })}
      </div>

      <div className={styles.dots}>
        {SCENES.map((_, i) => (
          <button
            key={i}
            type="button"
            className={`${styles.dot} ${i === idx ? styles.dotActive : ''}`}
            onClick={() => go(i)}
            aria-label={`Ver ilustración ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}

/* ── Login form ── */
function LoginForm() {
  const { login } = useAuth();
  const [form, setForm]       = useState({ username: '', password: '' });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.username, form.password);
    } catch (err) {
      const errs = err.response?.data?.errors;
      const msg  = errs?.detail || errs?.non_field_errors?.[0];
      setError(msg || 'Credenciales incorrectas. Verifica tu usuario y contraseña.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.left}>
      <div className={styles.logoRow}>
        <span className={styles.brandSub}>NOM-035-STPS-2018</span>
      </div>

      <h1 className={styles.heading}>Bienvenido de nuevo</h1>
      <p className={styles.desc}>
        Continúa gestionando el cumplimiento de la <b>NOM-035-STPS-2018</b> para tus empresas cliente.
      </p>

      <form onSubmit={handleSubmit} className={styles.form} noValidate>
        <div className={styles.field}>
          <input
            type="text"
            className={styles.input}
            placeholder="Usuario"
            value={form.username}
            onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
            autoComplete="username"
            required
            aria-label="Usuario"
          />
        </div>

        <div className={styles.field}>
          <input
            type={showPass ? 'text' : 'password'}
            className={`${styles.input} ${styles.inputPr}`}
            placeholder="Contraseña"
            value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
            autoComplete="current-password"
            required
            aria-label="Contraseña"
          />
          <button
            type="button"
            className={styles.eyeBtn}
            onClick={() => setShowPass(v => !v)}
            tabIndex={-1}
            aria-label={showPass ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showPass ? <IconEyeOff size={16} /> : <IconEye size={16} />}
          </button>
        </div>

        <div className={styles.formRow}>
          <button
            type="button"
            className={styles.forgot}
            onClick={() => alert('Contacta al administrador de tu organización para restablecer tu contraseña.')}
          >
            ¿Olvidaste tu contraseña?
          </button>
        </div>

        {error && (
          <div className={styles.errorBox} role="alert">
            <IconAlert />
            <span>{error}</span>
          </div>
        )}

        <button type="submit" className={styles.submit} disabled={loading}>
          {loading
            ? <><IconLoader size={16} /><span>Iniciando…</span></>
            : 'Iniciar sesión'
          }
        </button>
      </form>

      <div className={styles.pageFooter}>
        NOM-035-STPS-2018 &copy; {new Date().getFullYear()}
      </div>
    </div>
  );
}

export default function Login() {
  return (
    <div className={styles.page}>
      <div className={styles.orb1} />
      <div className={styles.orb2} />
      <div className={styles.shell}>
        <LoginForm />
        <IllustrationPane />
      </div>
    </div>
  );
}
