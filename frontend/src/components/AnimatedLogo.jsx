import { useEffect, useRef } from 'react'

// Every pixel from the original SVG — [x, y, fill]
const PIXELS = [
  [34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],
  [16,34,"#FF9050"],[34,34,"#FF9050"],[88,34,"#FF9050"],[106,34,"#FF9050"],
  [16,52,"#FF7A38"],[34,52,"#FF7A38"],[88,52,"#FF7A38"],[106,52,"#FF7A38"],
  [16,70,"#EE6422"],[34,70,"#EE6422"],[52,70,"#EE6422"],[70,70,"#EE6422"],[88,70,"#EE6422"],[106,70,"#EE6422"],
  [16,88,"#DC5418"],[34,88,"#DC5418"],[88,88,"#DC5418"],[106,88,"#DC5418"],
  [16,106,"#CC4412"],[34,106,"#CC4412"],[88,106,"#CC4412"],[106,106,"#CC4412"],
  [16,124,"#BE380E"],[34,124,"#BE380E"],[88,124,"#BE380E"],[106,124,"#BE380E"],
  // P
  [142,16,"#FFA868"],[160,16,"#FFA868"],[178,16,"#FFA868"],[196,16,"#FFA868"],[214,16,"#FFA868"],
  [142,34,"#FF9050"],[160,34,"#FF9050"],[214,34,"#FF9050"],[232,34,"#FF9050"],
  [142,52,"#FF7A38"],[160,52,"#FF7A38"],[214,52,"#FF7A38"],[232,52,"#FF7A38"],
  [142,70,"#EE6422"],[160,70,"#EE6422"],[178,70,"#EE6422"],[196,70,"#EE6422"],[214,70,"#EE6422"],
  [142,88,"#DC5418"],[160,88,"#DC5418"],
  [142,106,"#CC4412"],[160,106,"#CC4412"],
  [142,124,"#BE380E"],[160,124,"#BE380E"],
  // underscore / dash
  [286,70,"#EE6422"],[304,70,"#EE6422"],
  [286,88,"#DC5418"],[304,88,"#DC5418"],
  // R
  [340,16,"#FFA868"],[358,16,"#FFA868"],[376,16,"#FFA868"],[394,16,"#FFA868"],[412,16,"#FFA868"],
  [340,34,"#FF9050"],[358,34,"#FF9050"],[412,34,"#FF9050"],[430,34,"#FF9050"],
  [340,52,"#FF7A38"],[358,52,"#FF7A38"],[412,52,"#FF7A38"],[430,52,"#FF7A38"],
  [340,70,"#EE6422"],[358,70,"#EE6422"],[376,70,"#EE6422"],[394,70,"#EE6422"],[412,70,"#EE6422"],
  [340,88,"#DC5418"],[358,88,"#DC5418"],[376,88,"#DC5418"],[394,88,"#DC5418"],
  [340,106,"#CC4412"],[358,106,"#CC4412"],[394,106,"#CC4412"],[412,106,"#CC4412"],
  [340,124,"#BE380E"],[358,124,"#BE380E"],[412,124,"#BE380E"],[430,124,"#BE380E"],
  // E
  [466,16,"#FFA868"],[484,16,"#FFA868"],[502,16,"#FFA868"],[520,16,"#FFA868"],[538,16,"#FFA868"],[556,16,"#FFA868"],
  [466,34,"#FF9050"],[484,34,"#FF9050"],
  [466,52,"#FF7A38"],[484,52,"#FF7A38"],
  [466,70,"#EE6422"],[484,70,"#EE6422"],[502,70,"#EE6422"],[520,70,"#EE6422"],[538,70,"#EE6422"],
  [466,88,"#DC5418"],[484,88,"#DC5418"],
  [466,106,"#CC4412"],[484,106,"#CC4412"],
  [466,124,"#BE380E"],[484,124,"#BE380E"],[502,124,"#BE380E"],[520,124,"#BE380E"],[538,124,"#BE380E"],[556,124,"#BE380E"],
  // C
  [610,16,"#FFA868"],[628,16,"#FFA868"],[646,16,"#FFA868"],[664,16,"#FFA868"],[682,16,"#FFA868"],
  [592,34,"#FF9050"],[610,34,"#FF9050"],
  [592,52,"#FF7A38"],[610,52,"#FF7A38"],
  [592,70,"#EE6422"],[610,70,"#EE6422"],
  [592,88,"#DC5418"],[610,88,"#DC5418"],
  [592,106,"#CC4412"],[610,106,"#CC4412"],
  [610,124,"#BE380E"],[628,124,"#BE380E"],[646,124,"#BE380E"],[664,124,"#BE380E"],[682,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))

function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function hex2(n) { return ('0' + Math.min(255, Math.max(0, n)).toString(16)).slice(-2) }

export default function AnimatedLogo({ width = '100%', quick = false }) {
  const svgRef = useRef(null)
  const animated = useRef(false)

  useEffect(() => {
    if (animated.current) return
    animated.current = true

    const svg = svgRef.current
    if (!svg) return

    const rects = Array.from(svg.querySelectorAll('rect'))

    // Quick mode: simple fast fade-in, no rain
    if (quick) {
      rects.forEach((r, i) => {
        r.style.animationName = 'apQuickFade'
        r.style.animationDuration = '0.35s'
        r.style.animationTimingFunction = 'ease-out'
        r.style.animationFillMode = 'both'
        r.style.animationDelay = `${i * 1.5}ms`
      })
      return
    }
    const P = 18
    const initDelay = 800
    const rowGap = 210
    const animDur = '0.98s'
    let lastLand = 0

    // Phase 1 — rain falls bottom rows first
    rects.forEach(r => {
      const y = parseFloat(r.getAttribute('y'))
      const x = parseFloat(r.getAttribute('x'))
      const rowIndex = Math.round((maxY - y) / P)
      const jitter = ((x * 7 + y * 3) % 60) - 30
      let delay = initDelay + 100 + rowIndex * rowGap + jitter
      delay = Math.max(initDelay, delay)
      lastLand = Math.max(lastLand, delay)

      r.style.animationName = 'apPixelFall'
      r.style.animationDuration = animDur
      r.style.animationTimingFunction = 'cubic-bezier(0.22,1,0.36,1)'
      r.style.animationFillMode = 'both'
      r.style.animationDelay = delay + 'ms'
    })

    // Phase 2 — gradient merge via SVG SMIL
    const mergeStart = lastLand + 1100
    const ns = 'http://www.w3.org/2000/svg'

    setTimeout(() => {
      rects.forEach(r => {
        const y = parseFloat(r.getAttribute('y'))
        const t = (y - minY) / (maxY - minY)
        const from = r.getAttribute('fill')
        const to = '#' + hex2(lerp(255, 190, t)) + hex2(lerp(168, 56, t)) + hex2(lerp(104, 14, t))

        const anim = document.createElementNS(ns, 'animate')
        anim.setAttribute('attributeName', 'fill')
        anim.setAttribute('from', from)
        anim.setAttribute('to', to)
        anim.setAttribute('dur', '2.2s')
        anim.setAttribute('fill', 'freeze')
        anim.setAttribute('calcMode', 'spline')
        anim.setAttribute('keyTimes', '0;1')
        anim.setAttribute('keySplines', '0.4 0 0.2 1')
        anim.setAttribute('begin', 'indefinite')
        r.appendChild(anim)
        anim.beginElement()
      })
    }, mergeStart)
  }, [])

  return (
    <>
      <style>{`
        @keyframes apQuickFade {
          0%   { opacity: 0; transform: translateY(-3px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes apPixelFall {
          0%   { opacity: 0; transform: translateY(-160px); }
          80%  { opacity: 1; transform: translateY(2px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .ap-logo-rect {
          transform-box: fill-box;
          transform-origin: center bottom;
        }
      `}</style>
      <svg
        ref={svgRef}
        width={width}
        viewBox="0 0 716 158"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="crispEdges"
      >
        <defs>
          <filter id="ap-ds" x="-25%" y="-25%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="12" floodColor="#FF5010" floodOpacity="0.09"/>
            <feDropShadow dx="4" dy="6" stdDeviation="2" floodColor="#1A0500" floodOpacity="1"/>
          </filter>
        </defs>
        <g filter="url(#ap-ds)">
          {PIXELS.map(([x, y, fill], i) => (
            <rect
              key={i}
              className="ap-logo-rect"
              x={x} y={y}
              width={19} height={19}
              fill={fill}
            />
          ))}
        </g>
      </svg>
    </>
  )
}
