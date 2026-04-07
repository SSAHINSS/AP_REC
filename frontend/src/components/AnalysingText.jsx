import { useState, useEffect, useRef } from 'react'

const CHARS = 'RE-NAMING...'.split('')

// Each letter gets its own personality
const PERSONALITIES = [
  { freq: 1.1, amp: 14, phase: 0.0,  hue: 0   },  // R
  { freq: 0.9, amp: 18, phase: 0.5,  hue: 15  },  // E
  { freq: 1.3, amp: 8,  phase: 1.0,  hue: 5   },  // -
  { freq: 0.7, amp: 20, phase: 1.5,  hue: 5   },  // N
  { freq: 1.5, amp: 10, phase: 0.3,  hue: 30  },  // A
  { freq: 1.0, amp: 16, phase: 0.8,  hue: 10  },  // M
  { freq: 1.2, amp: 22, phase: 1.2,  hue: 20  },  // I
  { freq: 0.8, amp: 15, phase: 0.1,  hue: 8   },  // N
  { freq: 1.4, amp: 11, phase: 1.8,  hue: 35  },  // G
  { freq: 1.1, amp: 8,  phase: 0.6,  hue: 0   },  // .
  { freq: 0.9, amp: 8,  phase: 1.1,  hue: 0   },  // .
  { freq: 1.3, amp: 8,  phase: 1.6,  hue: 0   },  // .
]

export default function AnalysingText() {
  const tRef = useRef(0)
  const lastRef = useRef(null)
  const [, forceUpdate] = useState(0)
  const rafRef = useRef(null)
  const [burst, setBurst] = useState({})

  useEffect(() => {
    function frame(now) {
      if (lastRef.current !== null) {
        const dt = (now - lastRef.current) / 1000
        tRef.current += dt * 1.8
        forceUpdate(n => n + 1)
      }
      lastRef.current = now
      rafRef.current = requestAnimationFrame(frame)
    }
    rafRef.current = requestAnimationFrame(frame)

    // Random letter bursts — occasionally a letter pops up big
    const burstInterval = setInterval(() => {
      const i = Math.floor(Math.random() * 9) // only letters, not dots
      setBurst(prev => ({ ...prev, [i]: true }))
      setTimeout(() => setBurst(prev => ({ ...prev, [i]: false })), 180)
    }, 600)

    return () => { cancelAnimationFrame(rafRef.current); clearInterval(burstInterval) }
  }, [])

  const t = tRef.current

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
      {CHARS.map((char, i) => {
        const p = PERSONALITIES[i]
        const isDot = char === '.' || char === '-'

        // Each letter has its own wave
        const y = Math.sin(t * p.freq - p.phase) * p.amp

        // Horizontal bounce — letters spread and rebound independently
        const xWave = Math.sin(t * p.freq * 0.7 + p.phase * 2) * (isDot ? 4 : 14)

        // Scale pulse — each letter breathes at its own rate
        const scale = isDot
          ? 1 + Math.abs(Math.sin(t * p.freq * 1.2 + p.phase)) * 0.4
          : burst[i]
            ? 1.6  // burst pop
            : 1 + Math.sin(t * p.freq * 0.9 + p.phase) * 0.18

        // Color — cycles through orange spectrum
        const brightness = (Math.sin(t * p.freq + p.phase) + 1) / 2
        const r = Math.round(255)
        const g = Math.round(70 + brightness * 60 + p.hue)
        const b = Math.round(20 + brightness * 20)
        const alpha = isDot ? 0.4 + brightness * 0.6 : 0.6 + brightness * 0.4

        // Rotation — letters wobble
        const rot = isDot ? 0 : Math.sin(t * p.freq * 0.5 + p.phase) * 8

        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `translateY(${y.toFixed(1)}px) translateX(${xWave.toFixed(1)}px) scale(${scale.toFixed(2)}) rotate(${rot.toFixed(1)}deg)`,
              color: `rgba(${r},${g},${b},${alpha.toFixed(2)})`,
              fontFamily: 'var(--mono)',
              fontSize: isDot ? 18 : 22,
              fontWeight: 900,
              letterSpacing: '0.02em',
              willChange: 'transform',
              transition: burst[i] ? 'none' : undefined,
              textShadow: brightness > 0.8 && !isDot
                ? `0 0 12px rgba(255,${g},${b},0.6)`
                : 'none',
            }}
          >
            {char}
          </span>
        )
      })}
    </span>
  )
}
