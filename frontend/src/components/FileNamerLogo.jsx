import { useEffect, useRef } from 'react'

// Identical system to AnimatedLogo.jsx: PS=19, grid step=18, same colors
const PIXELS = [
  // F
  [16,16,"#FFA868"],[34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],
  [16,34,"#FF9050"],
  [16,52,"#FF7A38"],[34,52,"#FF7A38"],[52,52,"#FF7A38"],[70,52,"#FF7A38"],
  [16,70,"#EE6422"],
  [16,88,"#DC5418"],
  [16,106,"#CC4412"],
  [16,124,"#BE380E"],
  // I
  [124,16,"#FFA868"],[142,16,"#FFA868"],[160,16,"#FFA868"],
  [142,34,"#FF9050"],
  [142,52,"#FF7A38"],
  [142,70,"#EE6422"],
  [142,88,"#DC5418"],
  [142,106,"#CC4412"],
  [124,124,"#BE380E"],[142,124,"#BE380E"],[160,124,"#BE380E"],
  // L
  [196,16,"#FFA868"],
  [196,34,"#FF9050"],
  [196,52,"#FF7A38"],
  [196,70,"#EE6422"],
  [196,88,"#DC5418"],
  [196,106,"#CC4412"],
  [196,124,"#BE380E"],[214,124,"#BE380E"],[232,124,"#BE380E"],[250,124,"#BE380E"],[268,124,"#BE380E"],
  // E
  [304,16,"#FFA868"],[322,16,"#FFA868"],[340,16,"#FFA868"],[358,16,"#FFA868"],[376,16,"#FFA868"],[394,16,"#FFA868"],
  [304,34,"#FF9050"],
  [304,52,"#FF7A38"],[322,52,"#FF7A38"],[340,52,"#FF7A38"],[358,52,"#FF7A38"],[376,52,"#FF7A38"],
  [304,70,"#EE6422"],
  [304,88,"#DC5418"],
  [304,106,"#CC4412"],
  [304,124,"#BE380E"],[322,124,"#BE380E"],[340,124,"#BE380E"],[358,124,"#BE380E"],[376,124,"#BE380E"],[394,124,"#BE380E"],
  // _ (underscore — bottom 2 rows)
  [448,106,"#CC4412"],[466,106,"#CC4412"],[484,106,"#CC4412"],[502,106,"#CC4412"],
  [448,124,"#BE380E"],[466,124,"#BE380E"],[484,124,"#BE380E"],[502,124,"#BE380E"],
  // N
  [538,16,"#FFA868"],[610,16,"#FFA868"],
  [538,34,"#FF9050"],[556,34,"#FF9050"],[610,34,"#FF9050"],
  [538,52,"#FF7A38"],[574,52,"#FF7A38"],[610,52,"#FF7A38"],
  [538,70,"#EE6422"],[592,70,"#EE6422"],[610,70,"#EE6422"],
  [538,88,"#DC5418"],[610,88,"#DC5418"],
  [538,106,"#CC4412"],[610,106,"#CC4412"],
  [538,124,"#BE380E"],[610,124,"#BE380E"],
  // M
  [646,16,"#FFA868"],[754,16,"#FFA868"],
  [646,34,"#FF9050"],[664,34,"#FF9050"],[736,34,"#FF9050"],[754,34,"#FF9050"],
  [646,52,"#FF7A38"],[682,52,"#FF7A38"],[718,52,"#FF7A38"],[754,52,"#FF7A38"],
  [646,70,"#EE6422"],[700,70,"#EE6422"],[754,70,"#EE6422"],
  [646,88,"#DC5418"],[754,88,"#DC5418"],
  [646,106,"#CC4412"],[754,106,"#CC4412"],
  [646,124,"#BE380E"],[754,124,"#BE380E"],
  // R
  [790,16,"#FFA868"],[808,16,"#FFA868"],[826,16,"#FFA868"],[844,16,"#FFA868"],[862,16,"#FFA868"],
  [790,34,"#FF9050"],[808,34,"#FF9050"],[862,34,"#FF9050"],[880,34,"#FF9050"],
  [790,52,"#FF7A38"],[808,52,"#FF7A38"],[862,52,"#FF7A38"],[880,52,"#FF7A38"],
  [790,70,"#EE6422"],[808,70,"#EE6422"],[826,70,"#EE6422"],[844,70,"#EE6422"],[862,70,"#EE6422"],
  [790,88,"#DC5418"],[808,88,"#DC5418"],[826,88,"#DC5418"],[844,88,"#DC5418"],
  [790,106,"#CC4412"],[808,106,"#CC4412"],[844,106,"#CC4412"],[862,106,"#CC4412"],
  [790,124,"#BE380E"],[808,124,"#BE380E"],[862,124,"#BE380E"],[880,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))

function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function hex2(n) { return ('0' + Math.min(255, Math.max(0, n)).toString(16)).slice(-2) }

export default function FileNamerLogo({ width = '100%' }) {
  const svgRef  = useRef(null)
  const animated = useRef(false)

  useEffect(() => {
    if (animated.current) return
    animated.current = true
    const svg = svgRef.current
    if (!svg) return
    const rects = Array.from(svg.querySelectorAll('rect'))
    const P = 18
    const initDelay = 800
    const rowGap    = 210
    const animDur   = '0.98s'
    let lastLand = 0

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

    const mergeStart = lastLand + 1100
    const ns = 'http://www.w3.org/2000/svg'
    setTimeout(() => {
      rects.forEach(r => {
        const y = parseFloat(r.getAttribute('y'))
        const t = (y - minY) / (maxY - minY)
        const from = r.getAttribute('fill')
        const to = '#' + hex2(lerp(255,190,t)) + hex2(lerp(168,56,t)) + hex2(lerp(104,14,t))
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
        @keyframes apPixelFall {
          0%   { opacity: 0; transform: translateY(-160px); }
          80%  { opacity: 1; transform: translateY(2px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .fnmr-rect {
          transform-box: fill-box;
          transform-origin: center bottom;
        }
      `}</style>
      <svg
        ref={svgRef}
        width={width}
        viewBox="0 0 915 158"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="crispEdges"
      >
        <defs>
          <filter id="fnmr-ds" x="-25%" y="-25%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="12" floodColor="#FF5010" floodOpacity="0.09"/>
            <feDropShadow dx="4" dy="6" stdDeviation="2" floodColor="#1A0500" floodOpacity="1"/>
          </filter>
        </defs>
        <g filter="url(#fnmr-ds)">
          {PIXELS.map(([x, y, fill], i) => (
            <rect
              key={i}
              className="fnmr-rect"
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
