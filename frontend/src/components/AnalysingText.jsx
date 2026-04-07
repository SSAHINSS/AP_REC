import { useState, useEffect, useRef } from 'react'

const TARGET = 'RE-NAMING...'
const GLYPHS = '!@#$%^&*?><[]{}|/\\~`0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
const LOCK_INTERVAL = 120
const SCRAMBLE_SPEED = 40
const LOCK_COLOR = '#FF7030'
const SCRAMBLE_COLORS = ['#FF9050','#FF7A38','#EE6422','#FFA868','#FF5010','#FFB870']

function randGlyph() {
  return GLYPHS[Math.floor(Math.random() * GLYPHS.length)]
}

export default function AnalysingText() {
  const [display,  setDisplay]  = useState(() => TARGET.split('').map(() => randGlyph()))
  const [locked,   setLocked]   = useState(() => new Array(TARGET.length).fill(false))
  const [colors,   setColors]   = useState(() => TARGET.split('').map(() =>
    SCRAMBLE_COLORS[Math.floor(Math.random() * SCRAMBLE_COLORS.length)]
  ))
  const [glowIdx,  setGlowIdx]  = useState(-1)
  const lockedRef  = useRef(new Array(TARGET.length).fill(false))
  const frameRef   = useRef(null)
  const lockTimers = useRef([])

  useEffect(() => {
    function scramble() {
      setDisplay(prev => prev.map((ch, i) =>
        lockedRef.current[i] ? ch : randGlyph()
      ))
      setColors(prev => prev.map((c, i) =>
        lockedRef.current[i] ? LOCK_COLOR :
        SCRAMBLE_COLORS[Math.floor(Math.random() * SCRAMBLE_COLORS.length)]
      ))
      frameRef.current = setTimeout(scramble, SCRAMBLE_SPEED)
    }
    frameRef.current = setTimeout(scramble, SCRAMBLE_SPEED)

    TARGET.split('').forEach((char, i) => {
      const t = setTimeout(() => {
        lockedRef.current[i] = true
        setLocked(prev => { const n = [...prev]; n[i] = true; return n })
        setDisplay(prev => { const n = [...prev]; n[i] = char; return n })
        setColors(prev => { const n = [...prev]; n[i] = LOCK_COLOR; return n })
        setGlowIdx(i)
        setTimeout(() => setGlowIdx(g => g === i ? -1 : g), 200)
      }, 300 + i * LOCK_INTERVAL)
      lockTimers.current.push(t)
    })

    return () => {
      clearTimeout(frameRef.current)
      lockTimers.current.forEach(clearTimeout)
    }
  }, [])

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 1, letterSpacing: '0.08em' }}>
      {display.map((char, i) => {
        const isLocked = locked[i]
        const isDot    = TARGET[i] === '.' || TARGET[i] === '-'
        const isGlow   = glowIdx === i

        return (
          <span key={i} style={{
            display: 'inline-block',
            fontFamily: 'var(--mono)',
            fontSize: isDot ? 16 : 22,
            fontWeight: 900,
            color: colors[i],
            minWidth: isDot ? 10 : 16,
            textAlign: 'center',
            transform: isGlow ? 'scale(1.4)' : isLocked ? 'scale(1)' : `scale(${0.85 + Math.random() * 0.3})`,
            transition: isGlow ? 'transform 0.1s' : isLocked ? 'transform 0.15s' : 'none',
          }}>
            {char}
          </span>
        )
      })}
    </span>
  )
}
