import { useEffect, useRef } from 'react'

// Pixel size 19, grid 18 — identical to AnimatedLogo (AP_REC)
const PIXELS = [
  // F
  [16,16,"#FFA868"],[34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],
  [16,34,"#FF9050"],
  [16,52,"#FF7A38"],[34,52,"#FF7A38"],[52,52,"#FF7A38"],[70,52,"#FF7A38"],
  [16,70,"#EE6422"],[16,88,"#DC5418"],[16,106,"#CC4412"],[16,124,"#BE380E"],
  // I
  [125,16,"#FFA868"],[143,16,"#FFA868"],[161,16,"#FFA868"],
  [143,34,"#FF9050"],[143,52,"#FF7A38"],[143,70,"#EE6422"],[143,88,"#DC5418"],[143,106,"#CC4412"],
  [125,124,"#BE380E"],[143,124,"#BE380E"],[161,124,"#BE380E"],
  // L
  [198,16,"#FFA868"],[198,34,"#FF9050"],[198,52,"#FF7A38"],[198,70,"#EE6422"],
  [198,88,"#DC5418"],[198,106,"#CC4412"],
  [198,124,"#BE380E"],[216,124,"#BE380E"],[234,124,"#BE380E"],[252,124,"#BE380E"],[270,124,"#BE380E"],
  // E
  [307,16,"#FFA868"],[325,16,"#FFA868"],[343,16,"#FFA868"],[361,16,"#FFA868"],[379,16,"#FFA868"],
  [307,34,"#FF9050"],
  [307,52,"#FF7A38"],[325,52,"#FF7A38"],[343,52,"#FF7A38"],[361,52,"#FF7A38"],
  [307,70,"#EE6422"],[307,88,"#DC5418"],[307,106,"#CC4412"],
  [307,124,"#BE380E"],[325,124,"#BE380E"],[343,124,"#BE380E"],[361,124,"#BE380E"],[379,124,"#BE380E"],
  // _ (underscore — rows 5 and 6 only)
  [416,106,"#CC4412"],[434,106,"#CC4412"],[452,106,"#CC4412"],[470,106,"#CC4412"],
  [416,124,"#BE380E"],[434,124,"#BE380E"],[452,124,"#BE380E"],[470,124,"#BE380E"],
  // N
  [507,16,"#FFA868"],[579,16,"#FFA868"],
  [507,34,"#FF9050"],[525,34,"#FF9050"],[579,34,"#FF9050"],
  [507,52,"#FF7A38"],[543,52,"#FF7A38"],[579,52,"#FF7A38"],
  [507,70,"#EE6422"],[561,70,"#EE6422"],[579,70,"#EE6422"],
  [507,88,"#DC5418"],[579,88,"#DC5418"],
  [507,106,"#CC4412"],[579,106,"#CC4412"],
  [507,124,"#BE380E"],[579,124,"#BE380E"],
  // M
  [616,16,"#FFA868"],[706,16,"#FFA868"],
  [616,34,"#FF9050"],[634,34,"#FF9050"],[688,34,"#FF9050"],[706,34,"#FF9050"],
  [616,52,"#FF7A38"],[652,52,"#FF7A38"],[670,52,"#FF7A38"],[706,52,"#FF7A38"],
  [616,70,"#EE6422"],[706,70,"#EE6422"],
  [616,88,"#DC5418"],[706,88,"#DC5418"],
  [616,106,"#CC4412"],[706,106,"#CC4412"],
  [616,124,"#BE380E"],[706,124,"#BE380E"],
  // R
  [743,16,"#FFA868"],[761,16,"#FFA868"],[779,16,"#FFA868"],[797,16,"#FFA868"],[815,16,"#FFA868"],
  [743,34,"#FF9050"],[761,34,"#FF9050"],[815,34,"#FF9050"],[833,34,"#FF9050"],
  [743,52,"#FF7A38"],[761,52,"#FF7A38"],[815,52,"#FF7A38"],[833,52,"#FF7A38"],
  [743,70,"#EE6422"],[761,70,"#EE6422"],[779,70,"#EE6422"],[797,70,"#EE6422"],[815,70,"#EE6422"],
  [743,88,"#DC5418"],[761,88,"#DC5418"],[779,88,"#DC5418"],[797,88,"#DC5418"],
  [743,106,"#CC4412"],[761,106,"#CC4412"],[797,106,"#CC4412"],[815,106,"#CC4412"],
  [743,124,"#BE380E"],[761,124,"#BE380E"],[815,124,"#BE380E"],[833,124,"#BE380E"],
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
        viewBox="0 0 868 158"
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
