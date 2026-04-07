import { useEffect, useState } from 'react'

const COLS = 32
const ROWS = 4
const TOTAL = COLS * ROWS

export default function PixelProgressBar({ running }) {
  const [tick, setTick] = useState(0)

  useEffect(() => {
    if (!running) { setTick(0); return }
    const id = setInterval(() => setTick(t => t + 1), 90)
    return () => clearInterval(id)
  }, [running])

  // Comet head position sweeps across all blocks
  const head = (tick * 1.8) % TOTAL

  return (
    <div style={{
      background: 'var(--bg)',
      border: '1px solid var(--border)',
      borderRadius: 2,
      padding: '20px 16px 16px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 14,
    }}>

      {/* Pixel grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, width: '100%' }}>
        {Array.from({ length: ROWS }, (_, row) => (
          <div key={row} style={{ display: 'flex', gap: 4 }}>
            {Array.from({ length: COLS }, (_, col) => {
              const idx = row * COLS + col

              // Distance from comet head (wraps around)
              const dist = (head - idx + TOTAL) % TOTAL
              const TAIL = 10

              // Comet head glow
              let alpha = 0
              if (dist === 0) alpha = 1
              else if (dist < TAIL) alpha = (1 - dist / TAIL) * 0.85

              // Occasional random flicker on passed blocks
              const passed = dist < TAIL + 4
              const flicker = passed && ((idx * 137 + tick * 31) % 17 === 0)

              const bg = alpha > 0
                ? `rgba(255,112,48,${0.18 + alpha * 0.82})`
                : flicker
                  ? 'rgba(255,112,48,0.35)'
                  : 'var(--hi)'

              const glow = alpha > 0.7
                ? `0 0 ${Math.round(alpha * 10)}px rgba(255,112,48,${alpha * 0.9}), 0 0 ${Math.round(alpha * 20)}px rgba(255,112,48,${alpha * 0.4})`
                : 'none'

              return (
                <div
                  key={col}
                  style={{
                    flex: 1,
                    height: 13,
                    background: bg,
                    boxShadow: glow,
                    imageRendering: 'pixelated',
                  }}
                />
              )
            })}
          </div>
        ))}
      </div>

      {/* Status text */}
      <div style={{
        fontFamily: 'var(--mono)',
        fontSize: 11,
        letterSpacing: '0.2em',
        color: 'var(--ox)',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        userSelect: 'none',
      }}>
        {'PROCESSING'.split('').map((char, i) => (
          <span
            key={i}
            style={{
              opacity: ((tick + i * 3) % 20 < 14) ? 1 : 0.25,
              transition: 'opacity 0.09s',
              display: 'inline-block',
            }}
          >
            {char}
          </span>
        ))}
        <span style={{
          opacity: tick % 6 < 3 ? 1 : 0,
          transition: 'opacity 0.09s',
          color: 'var(--ox)',
          fontSize: 13,
        }}>█</span>
      </div>

    </div>
  )
}
