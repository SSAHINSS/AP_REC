import { useEffect, useRef } from 'react'

// Every pixel from the original SVG — [x, y, fill]
const PIXELS = [
  [34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],[16,34,"#FF9050"],
  [34,34,"#FF9050"],[88,34,"#FF9050"],[106,34,"#FF9050"],[16,52,"#FF7A38"],[34,52,"#FF7A38"],
  [88,52,"#FF7A38"],[106,52,"#FF7A38"],[16,70,"#EE6422"],[34,70,"#EE6422"],[52,70,"#EE6422"],
  [70,70,"#EE6422"],[88,70,"#EE6422"],[106,70,"#EE6422"],[16,88,"#DC5418"],[34,88,"#DC5418"],
  [88,88,"#DC5418"],[106,88,"#DC5418"],[16,106,"#CC4412"],[34,106,"#CC4412"],[88,106,"#CC4412"],
  [106,106,"#CC4412"],[16,124,"#BE380E"],[34,124,"#BE380E"],[88,124,"#BE380E"],[106,124,"#BE380E"],
  [160,16,"#FFA868"],[178,16,"#FFA868"],[196,16,"#FFA868"],[214,16,"#FFA868"],[232,16,"#FFA868"],
  [142,34,"#FF9050"],[160,34,"#FF9050"],[142,52,"#FF7A38"],[160,52,"#FF7A38"],[142,70,"#EE6422"],
  [160,70,"#EE6422"],[142,88,"#DC5418"],[160,88,"#DC5418"],[142,106,"#CC4412"],[160,106,"#CC4412"],
  [160,124,"#BE380E"],[178,124,"#BE380E"],[196,124,"#BE380E"],[214,124,"#BE380E"],[232,124,"#BE380E"],
  [286,16,"#FFA868"],[304,16,"#FFA868"],[322,16,"#FFA868"],[340,16,"#FFA868"],[358,16,"#FFA868"],
  [268,34,"#FF9050"],[286,34,"#FF9050"],[268,52,"#FF7A38"],[286,52,"#FF7A38"],[268,70,"#EE6422"],
  [286,70,"#EE6422"],[268,88,"#DC5418"],[286,88,"#DC5418"],[268,106,"#CC4412"],[286,106,"#CC4412"],
  [286,124,"#BE380E"],[304,124,"#BE380E"],[322,124,"#BE380E"],[340,124,"#BE380E"],[358,124,"#BE380E"],
  [394,16,"#FFA868"],[412,16,"#FFA868"],[430,16,"#FFA868"],[448,16,"#FFA868"],[466,16,"#FFA868"],
  [394,34,"#FF9050"],[412,34,"#FF9050"],[466,34,"#FF9050"],[484,34,"#FF9050"],[394,52,"#FF7A38"],
  [412,52,"#FF7A38"],[466,52,"#FF7A38"],[484,52,"#FF7A38"],[394,70,"#EE6422"],[412,70,"#EE6422"],
  [430,70,"#EE6422"],[448,70,"#EE6422"],[466,70,"#EE6422"],[394,88,"#DC5418"],[412,88,"#DC5418"],
  [430,88,"#DC5418"],[448,88,"#DC5418"],[394,106,"#CC4412"],[412,106,"#CC4412"],[448,106,"#CC4412"],
  [466,106,"#CC4412"],[394,124,"#BE380E"],[412,124,"#BE380E"],[466,124,"#BE380E"],[484,124,"#BE380E"],
  [520,16,"#FFA868"],[538,16,"#FFA868"],[592,16,"#FFA868"],[610,16,"#FFA868"],[520,34,"#FF9050"],
  [538,34,"#FF9050"],[592,34,"#FF9050"],[610,34,"#FF9050"],[520,52,"#FF7A38"],[538,52,"#FF7A38"],
  [592,52,"#FF7A38"],[610,52,"#FF7A38"],[520,70,"#EE6422"],[538,70,"#EE6422"],[592,70,"#EE6422"],
  [610,70,"#EE6422"],[520,88,"#DC5418"],[538,88,"#DC5418"],[592,88,"#DC5418"],[610,88,"#DC5418"],
  [520,106,"#CC4412"],[538,106,"#CC4412"],[592,106,"#CC4412"],[610,106,"#CC4412"],[538,124,"#BE380E"],
  [556,124,"#BE380E"],[574,124,"#BE380E"],[592,124,"#BE380E"],[664,16,"#FFA868"],[682,16,"#FFA868"],
  [700,16,"#FFA868"],[718,16,"#FFA868"],[646,34,"#FF9050"],[664,34,"#FF9050"],[718,34,"#FF9050"],
  [736,34,"#FF9050"],[646,52,"#FF7A38"],[664,52,"#FF7A38"],[718,52,"#FF7A38"],[736,52,"#FF7A38"],
  [646,70,"#EE6422"],[664,70,"#EE6422"],[682,70,"#EE6422"],[700,70,"#EE6422"],[718,70,"#EE6422"],
  [736,70,"#EE6422"],[646,88,"#DC5418"],[664,88,"#DC5418"],[718,88,"#DC5418"],[736,88,"#DC5418"],
  [646,106,"#CC4412"],[664,106,"#CC4412"],[718,106,"#CC4412"],[736,106,"#CC4412"],[646,124,"#BE380E"],
  [664,124,"#BE380E"],[718,124,"#BE380E"],[736,124,"#BE380E"],[772,16,"#FFA868"],[790,16,"#FFA868"],
  [772,34,"#FF9050"],[790,34,"#FF9050"],[772,52,"#FF7A38"],[790,52,"#FF7A38"],[772,70,"#EE6422"],
  [790,70,"#EE6422"],[772,88,"#DC5418"],[790,88,"#DC5418"],[772,106,"#CC4412"],[790,106,"#CC4412"],
  [772,124,"#BE380E"],[790,124,"#BE380E"],[808,124,"#BE380E"],[826,124,"#BE380E"],[844,124,"#BE380E"],
  [862,124,"#BE380E"],[898,16,"#FFA868"],[916,16,"#FFA868"],[934,16,"#FFA868"],[952,16,"#FFA868"],
  [970,16,"#FFA868"],[988,16,"#FFA868"],[898,34,"#FF9050"],[916,34,"#FF9050"],[898,52,"#FF7A38"],
  [916,52,"#FF7A38"],[898,70,"#EE6422"],[916,70,"#EE6422"],[934,70,"#EE6422"],[952,70,"#EE6422"],
  [970,70,"#EE6422"],[988,70,"#EE6422"],[970,88,"#DC5418"],[988,88,"#DC5418"],[970,106,"#CC4412"],
  [988,106,"#CC4412"],[898,124,"#BE380E"],[916,124,"#BE380E"],[934,124,"#BE380E"],[952,124,"#BE380E"],
  [970,124,"#BE380E"],[988,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))

function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function hex2(n) { return ('0' + Math.min(255, Math.max(0, n)).toString(16)).slice(-2) }

export default function AccrualLogo({ width = '100%', quick = false }) {
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
        r.style.animationName = 'acQuickFade'
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

      r.style.animationName = 'acPixelFall'
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
        @keyframes acQuickFade {
          0%   { opacity: 0; transform: translateY(-3px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes acPixelFall {
          0%   { opacity: 0; transform: translateY(-160px); }
          80%  { opacity: 1; transform: translateY(2px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .ac-logo-rect {
          transform-box: fill-box;
          transform-origin: center bottom;
        }
      `}</style>
      <svg
        ref={svgRef}
        width={width}
        viewBox="0 0 1006 158"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="crispEdges"
      >
        <defs>
          <filter id="ac-ds" x="-25%" y="-25%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="12" floodColor="#FF5010" floodOpacity="0.09"/>
            <feDropShadow dx="4" dy="6" stdDeviation="2" floodColor="#1A0500" floodOpacity="1"/>
          </filter>
        </defs>
        <g filter="url(#ac-ds)">
          {PIXELS.map(([x, y, fill], i) => (
            <rect
              key={i}
              className="ac-logo-rect"
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
