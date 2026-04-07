import { useEffect, useRef } from 'react'

const PIXELS = [
  // F
  [16,16,"#FFA868"],[34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],[106,16,"#FFA868"],
  [16,34,"#FF9050"],[34,34,"#FF9050"],
  [16,52,"#FF7A38"],[34,52,"#FF7A38"],[52,52,"#FF7A38"],[70,52,"#FF7A38"],[88,52,"#FF7A38"],
  [16,70,"#EE6422"],[34,70,"#EE6422"],
  [16,88,"#DC5418"],[34,88,"#DC5418"],
  [16,106,"#CC4412"],[34,106,"#CC4412"],
  [16,124,"#BE380E"],[34,124,"#BE380E"],
  // I
  [143,16,"#FFA868"],[161,16,"#FFA868"],[179,16,"#FFA868"],[197,16,"#FFA868"],
  [161,34,"#FF9050"],[179,34,"#FF9050"],
  [161,52,"#FF7A38"],[179,52,"#FF7A38"],
  [161,70,"#EE6422"],[179,70,"#EE6422"],
  [161,88,"#DC5418"],[179,88,"#DC5418"],
  [161,106,"#CC4412"],[179,106,"#CC4412"],
  [143,124,"#BE380E"],[161,124,"#BE380E"],[179,124,"#BE380E"],[197,124,"#BE380E"],
  // L
  [234,16,"#FFA868"],[252,16,"#FFA868"],
  [234,34,"#FF9050"],[252,34,"#FF9050"],
  [234,52,"#FF7A38"],[252,52,"#FF7A38"],
  [234,70,"#EE6422"],[252,70,"#EE6422"],
  [234,88,"#DC5418"],[252,88,"#DC5418"],
  [234,106,"#CC4412"],[252,106,"#CC4412"],
  [234,124,"#BE380E"],[252,124,"#BE380E"],[270,124,"#BE380E"],[288,124,"#BE380E"],[306,124,"#BE380E"],[324,124,"#BE380E"],
  // E
  [361,16,"#FFA868"],[379,16,"#FFA868"],[397,16,"#FFA868"],[415,16,"#FFA868"],[433,16,"#FFA868"],[451,16,"#FFA868"],
  [361,34,"#FF9050"],[379,34,"#FF9050"],
  [361,52,"#FF7A38"],[379,52,"#FF7A38"],[397,52,"#FF7A38"],[415,52,"#FF7A38"],[433,52,"#FF7A38"],
  [361,70,"#EE6422"],[379,70,"#EE6422"],
  [361,88,"#DC5418"],[379,88,"#DC5418"],
  [361,106,"#CC4412"],[379,106,"#CC4412"],
  [361,124,"#BE380E"],[379,124,"#BE380E"],[397,124,"#BE380E"],[415,124,"#BE380E"],[433,124,"#BE380E"],[451,124,"#BE380E"],
  // _
  [488,106,"#CC4412"],[506,106,"#CC4412"],[524,106,"#CC4412"],[542,106,"#CC4412"],[560,106,"#CC4412"],[578,106,"#CC4412"],
  [488,124,"#BE380E"],[506,124,"#BE380E"],[524,124,"#BE380E"],[542,124,"#BE380E"],[560,124,"#BE380E"],[578,124,"#BE380E"],
  // N
  [615,16,"#FFA868"],[633,16,"#FFA868"],[687,16,"#FFA868"],[705,16,"#FFA868"],
  [615,34,"#FF9050"],[633,34,"#FF9050"],[651,34,"#FF9050"],[687,34,"#FF9050"],[705,34,"#FF9050"],
  [615,52,"#FF7A38"],[633,52,"#FF7A38"],[651,52,"#FF7A38"],[687,52,"#FF7A38"],[705,52,"#FF7A38"],
  [615,70,"#EE6422"],[633,70,"#EE6422"],[669,70,"#EE6422"],[687,70,"#EE6422"],[705,70,"#EE6422"],
  [615,88,"#DC5418"],[633,88,"#DC5418"],[669,88,"#DC5418"],[687,88,"#DC5418"],[705,88,"#DC5418"],
  [615,106,"#CC4412"],[633,106,"#CC4412"],[687,106,"#CC4412"],[705,106,"#CC4412"],
  [615,124,"#BE380E"],[633,124,"#BE380E"],[687,124,"#BE380E"],[705,124,"#BE380E"],
  // M
  [742,16,"#FFA868"],[760,16,"#FFA868"],[850,16,"#FFA868"],[868,16,"#FFA868"],
  [742,34,"#FF9050"],[760,34,"#FF9050"],[778,34,"#FF9050"],[832,34,"#FF9050"],[850,34,"#FF9050"],[868,34,"#FF9050"],
  [742,52,"#FF7A38"],[760,52,"#FF7A38"],[778,52,"#FF7A38"],[796,52,"#FF7A38"],[814,52,"#FF7A38"],[832,52,"#FF7A38"],[850,52,"#FF7A38"],[868,52,"#FF7A38"],
  [742,70,"#EE6422"],[760,70,"#EE6422"],[796,70,"#EE6422"],[814,70,"#EE6422"],[850,70,"#EE6422"],[868,70,"#EE6422"],
  [742,88,"#DC5418"],[760,88,"#DC5418"],[850,88,"#DC5418"],[868,88,"#DC5418"],
  [742,106,"#CC4412"],[760,106,"#CC4412"],[850,106,"#CC4412"],[868,106,"#CC4412"],
  [742,124,"#BE380E"],[760,124,"#BE380E"],[850,124,"#BE380E"],[868,124,"#BE380E"],
  // R
  [905,16,"#FFA868"],[923,16,"#FFA868"],[941,16,"#FFA868"],[959,16,"#FFA868"],[977,16,"#FFA868"],
  [905,34,"#FF9050"],[923,34,"#FF9050"],[977,34,"#FF9050"],[995,34,"#FF9050"],
  [905,52,"#FF7A38"],[923,52,"#FF7A38"],[977,52,"#FF7A38"],[995,52,"#FF7A38"],
  [905,70,"#EE6422"],[923,70,"#EE6422"],[941,70,"#EE6422"],[959,70,"#EE6422"],[977,70,"#EE6422"],
  [905,88,"#DC5418"],[923,88,"#DC5418"],[941,88,"#DC5418"],[959,88,"#DC5418"],
  [905,106,"#CC4412"],[923,106,"#CC4412"],[959,106,"#CC4412"],[977,106,"#CC4412"],
  [905,124,"#BE380E"],[923,124,"#BE380E"],[977,124,"#BE380E"],[995,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))
function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function hex2(n) { return ('0' + Math.min(255, Math.max(0, n)).toString(16)).slice(-2) }

export default function FileNamerLogo({ width = '100%' }) {
  const svgRef   = useRef(null)
  const animated = useRef(false)

  useEffect(() => {
    if (animated.current) return
    animated.current = true
    const svg = svgRef.current
    if (!svg) return
    const rects     = Array.from(svg.querySelectorAll('rect'))
    const P         = 18
    const initDelay = 800
    const rowGap    = 210
    const animDur   = '0.98s'
    let lastLand    = 0
    rects.forEach(r => {
      const y        = parseFloat(r.getAttribute('y'))
      const x        = parseFloat(r.getAttribute('x'))
      const rowIndex = Math.round((maxY - y) / P)
      const jitter   = ((x * 7 + y * 3) % 60) - 30
      let delay      = initDelay + 100 + rowIndex * rowGap + jitter
      delay          = Math.max(initDelay, delay)
      lastLand       = Math.max(lastLand, delay)
      r.style.animationName           = 'apPixelFall'
      r.style.animationDuration       = animDur
      r.style.animationTimingFunction = 'cubic-bezier(0.22,1,0.36,1)'
      r.style.animationFillMode       = 'both'
      r.style.animationDelay          = delay + 'ms'
    })
    const mergeStart = lastLand + 1100
    const ns = 'http://www.w3.org/2000/svg'
    setTimeout(() => {
      rects.forEach(r => {
        const y    = parseFloat(r.getAttribute('y'))
        const t    = (y - minY) / (maxY - minY)
        const from = r.getAttribute('fill')
        const to   = '#' + hex2(lerp(255,190,t)) + hex2(lerp(168,56,t)) + hex2(lerp(104,14,t))
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
        .fnmr-rect { transform-box: fill-box; transform-origin: center bottom; }
      `}</style>
      <svg
        ref={svgRef}
        width={width}
        viewBox="0 0 1030 158"
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
            <rect key={i} className="fnmr-rect" x={x} y={y} width={19} height={19} fill={fill} />
          ))}
        </g>
      </svg>
    </>
  )
}
