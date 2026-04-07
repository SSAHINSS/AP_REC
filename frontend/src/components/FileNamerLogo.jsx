import { useEffect, useRef } from 'react'

// FILE-NMR — pixel-perfect match to AP-REC
// PS=19, GRID=18, same colors, same dash spacing, same animation
const PIXELS = [
  // F (6 cols, 2px strokes)
  [16,16,"#FFA868"],[34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],[106,16,"#FFA868"],
  [16,34,"#FF9050"],[34,34,"#FF9050"],
  [16,52,"#FF7A38"],[34,52,"#FF7A38"],[52,52,"#FF7A38"],[70,52,"#FF7A38"],[88,52,"#FF7A38"],
  [16,70,"#EE6422"],[34,70,"#EE6422"],
  [16,88,"#DC5418"],[34,88,"#DC5418"],
  [16,106,"#CC4412"],[34,106,"#CC4412"],
  [16,124,"#BE380E"],[34,124,"#BE380E"],
  // I (4 cols, 2px strokes)
  [143,16,"#FFA868"],[161,16,"#FFA868"],[179,16,"#FFA868"],[197,16,"#FFA868"],
  [161,34,"#FF9050"],[179,34,"#FF9050"],
  [161,52,"#FF7A38"],[179,52,"#FF7A38"],
  [161,70,"#EE6422"],[179,70,"#EE6422"],
  [161,88,"#DC5418"],[179,88,"#DC5418"],
  [161,106,"#CC4412"],[179,106,"#CC4412"],
  [143,124,"#BE380E"],[161,124,"#BE380E"],[179,124,"#BE380E"],[197,124,"#BE380E"],
  // L (6 cols, 2px strokes)
  [234,16,"#FFA868"],[252,16,"#FFA868"],
  [234,34,"#FF9050"],[252,34,"#FF9050"],
  [234,52,"#FF7A38"],[252,52,"#FF7A38"],
  [234,70,"#EE6422"],[252,70,"#EE6422"],
  [234,88,"#DC5418"],[252,88,"#DC5418"],
  [234,106,"#CC4412"],[252,106,"#CC4412"],
  [234,124,"#BE380E"],[252,124,"#BE380E"],[270,124,"#BE380E"],[288,124,"#BE380E"],[306,124,"#BE380E"],[324,124,"#BE380E"],
  // E (6 cols, 2px strokes)
  [361,16,"#FFA868"],[379,16,"#FFA868"],[397,16,"#FFA868"],[415,16,"#FFA868"],[433,16,"#FFA868"],[451,16,"#FFA868"],
  [361,34,"#FF9050"],[379,34,"#FF9050"],
  [361,52,"#FF7A38"],[379,52,"#FF7A38"],[397,52,"#FF7A38"],[415,52,"#FF7A38"],[433,52,"#FF7A38"],
  [361,70,"#EE6422"],[379,70,"#EE6422"],
  [361,88,"#DC5418"],[379,88,"#DC5418"],
  [361,106,"#CC4412"],[379,106,"#CC4412"],
  [361,124,"#BE380E"],[379,124,"#BE380E"],[397,124,"#BE380E"],[415,124,"#BE380E"],[433,124,"#BE380E"],[451,124,"#BE380E"],
  // - (dash — exact same spacing as AP-REC dash)
  [506,70,"#EE6422"],[524,70,"#EE6422"],
  [506,88,"#DC5418"],[524,88,"#DC5418"],
  // N (6 cols, 2px strokes)
  [561,16,"#FFA868"],[579,16,"#FFA868"],[633,16,"#FFA868"],[651,16,"#FFA868"],
  [561,34,"#FF9050"],[579,34,"#FF9050"],[597,34,"#FF9050"],[633,34,"#FF9050"],[651,34,"#FF9050"],
  [561,52,"#FF7A38"],[579,52,"#FF7A38"],[597,52,"#FF7A38"],[633,52,"#FF7A38"],[651,52,"#FF7A38"],
  [561,70,"#EE6422"],[579,70,"#EE6422"],[615,70,"#EE6422"],[633,70,"#EE6422"],[651,70,"#EE6422"],
  [561,88,"#DC5418"],[579,88,"#DC5418"],[615,88,"#DC5418"],[633,88,"#DC5418"],[651,88,"#DC5418"],
  [561,106,"#CC4412"],[579,106,"#CC4412"],[633,106,"#CC4412"],[651,106,"#CC4412"],
  [561,124,"#BE380E"],[579,124,"#BE380E"],[633,124,"#BE380E"],[651,124,"#BE380E"],
  // M (8 cols, 2px strokes)
  [688,16,"#FFA868"],[706,16,"#FFA868"],[796,16,"#FFA868"],[814,16,"#FFA868"],
  [688,34,"#FF9050"],[706,34,"#FF9050"],[724,34,"#FF9050"],[778,34,"#FF9050"],[796,34,"#FF9050"],[814,34,"#FF9050"],
  [688,52,"#FF7A38"],[706,52,"#FF7A38"],[724,52,"#FF7A38"],[742,52,"#FF7A38"],[760,52,"#FF7A38"],[778,52,"#FF7A38"],[796,52,"#FF7A38"],[814,52,"#FF7A38"],
  [688,70,"#EE6422"],[706,70,"#EE6422"],[742,70,"#EE6422"],[760,70,"#EE6422"],[796,70,"#EE6422"],[814,70,"#EE6422"],
  [688,88,"#DC5418"],[706,88,"#DC5418"],[796,88,"#DC5418"],[814,88,"#DC5418"],
  [688,106,"#CC4412"],[706,106,"#CC4412"],[796,106,"#CC4412"],[814,106,"#CC4412"],
  [688,124,"#BE380E"],[706,124,"#BE380E"],[796,124,"#BE380E"],[814,124,"#BE380E"],
  // R (6 cols, 2px strokes — identical to AP-REC R)
  [851,16,"#FFA868"],[869,16,"#FFA868"],[887,16,"#FFA868"],[905,16,"#FFA868"],[923,16,"#FFA868"],
  [851,34,"#FF9050"],[869,34,"#FF9050"],[923,34,"#FF9050"],[941,34,"#FF9050"],
  [851,52,"#FF7A38"],[869,52,"#FF7A38"],[923,52,"#FF7A38"],[941,52,"#FF7A38"],
  [851,70,"#EE6422"],[869,70,"#EE6422"],[887,70,"#EE6422"],[905,70,"#EE6422"],[923,70,"#EE6422"],
  [851,88,"#DC5418"],[869,88,"#DC5418"],[887,88,"#DC5418"],[905,88,"#DC5418"],
  [851,106,"#CC4412"],[869,106,"#CC4412"],[905,106,"#CC4412"],[923,106,"#CC4412"],
  [851,124,"#BE380E"],[869,124,"#BE380E"],[923,124,"#BE380E"],[941,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))
function lerp(a,b,t){return Math.round(a+(b-a)*t)}
function hex2(n){return('0'+Math.min(255,Math.max(0,n)).toString(16)).slice(-2)}

export default function FileNamerLogo({ width = '100%', quick = false }) {
  const svgRef   = useRef(null)
  const animated = useRef(false)

  useEffect(() => {
    if (animated.current) return
    animated.current = true
    const svg = svgRef.current
    if (!svg) return
    const rects = Array.from(svg.querySelectorAll('rect'))

    // Quick mode: fast fade-in, no rain
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
    const P = 18; const initDelay = 800; const rowGap = 210; const animDur = '0.98s'
    let lastLand = 0
    rects.forEach(r => {
      const y = parseFloat(r.getAttribute('y')); const x = parseFloat(r.getAttribute('x'))
      const rowIndex = Math.round((maxY - y) / P)
      const jitter = ((x*7 + y*3) % 60) - 30
      let delay = initDelay + 100 + rowIndex*rowGap + jitter
      delay = Math.max(initDelay, delay); lastLand = Math.max(lastLand, delay)
      r.style.animationName = 'apPixelFall'; r.style.animationDuration = animDur
      r.style.animationTimingFunction = 'cubic-bezier(0.22,1,0.36,1)'
      r.style.animationFillMode = 'both'; r.style.animationDelay = delay + 'ms'
    })
    setTimeout(() => {
      const ns = 'http://www.w3.org/2000/svg'
      rects.forEach(r => {
        const y = parseFloat(r.getAttribute('y')); const t = (y-minY)/(maxY-minY)
        const from = r.getAttribute('fill')
        const to = '#'+hex2(lerp(255,190,t))+hex2(lerp(168,56,t))+hex2(lerp(104,14,t))
        const anim = document.createElementNS(ns,'animate')
        anim.setAttribute('attributeName','fill'); anim.setAttribute('from',from)
        anim.setAttribute('to',to); anim.setAttribute('dur','2.2s')
        anim.setAttribute('fill','freeze'); anim.setAttribute('calcMode','spline')
        anim.setAttribute('keyTimes','0;1'); anim.setAttribute('keySplines','0.4 0 0.2 1')
        anim.setAttribute('begin','indefinite'); r.appendChild(anim); anim.beginElement()
      })
    }, lastLand + 1100)
  }, [])

  return (
    <>
      <style>{`
        @keyframes apQuickFade {
          0%   { opacity: 0; transform: translateY(-3px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes apPixelFall {
          0%   { opacity:0; transform:translateY(-160px); }
          80%  { opacity:1; transform:translateY(2px); }
          100% { opacity:1; transform:translateY(0); }
        }
        .fnmr-rect { transform-box:fill-box; transform-origin:center bottom; }
      `}</style>
      <svg ref={svgRef} width={width} viewBox="0 0 976 158"
        xmlns="http://www.w3.org/2000/svg" shapeRendering="crispEdges">
        <defs>
          <filter id="fnmr-ds" x="-25%" y="-25%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="12" floodColor="#FF5010" floodOpacity="0.09"/>
            <feDropShadow dx="4" dy="6" stdDeviation="2" floodColor="#1A0500" floodOpacity="1"/>
          </filter>
        </defs>
        <g filter="url(#fnmr-ds)">
          {PIXELS.map(([x,y,fill],i) => (
            <rect key={i} className="fnmr-rect" x={x} y={y} width={19} height={19} fill={fill}/>
          ))}
        </g>
      </svg>
    </>
  )
}
