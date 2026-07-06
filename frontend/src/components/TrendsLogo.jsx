import { useEffect, useRef } from 'react'

// Every pixel from the original SVG — [x, y, fill]
const PIXELS = [
  [16,16,"#FFA868"],[34,16,"#FFA868"],[52,16,"#FFA868"],[70,16,"#FFA868"],[88,16,"#FFA868"],
  [106,16,"#FFA868"],[16,34,"#FF9050"],[34,34,"#FF9050"],[16,52,"#FF7A38"],[34,52,"#FF7A38"],
  [16,70,"#EE6422"],[34,70,"#EE6422"],[52,70,"#EE6422"],[70,70,"#EE6422"],[88,70,"#EE6422"],
  [16,88,"#DC5418"],[34,88,"#DC5418"],[16,106,"#CC4412"],[34,106,"#CC4412"],
  [16,124,"#BE380E"],[34,124,"#BE380E"],[52,124,"#BE380E"],[70,124,"#BE380E"],
  [88,124,"#BE380E"],[106,124,"#BE380E"],[142,16,"#FFA868"],[160,16,"#FFA868"],
  [214,16,"#FFA868"],[232,16,"#FFA868"],[142,34,"#FF9050"],[160,34,"#FF9050"],
  [214,34,"#FF9050"],[232,34,"#FF9050"],[160,52,"#FF7A38"],[178,52,"#FF7A38"],
  [196,52,"#FF7A38"],[214,52,"#FF7A38"],[178,70,"#EE6422"],[196,70,"#EE6422"],
  [160,88,"#DC5418"],[178,88,"#DC5418"],[196,88,"#DC5418"],[214,88,"#DC5418"],
  [142,106,"#CC4412"],[160,106,"#CC4412"],[214,106,"#CC4412"],[232,106,"#CC4412"],
  [142,124,"#BE380E"],[160,124,"#BE380E"],[214,124,"#BE380E"],[232,124,"#BE380E"],
  [268,16,"#FFA868"],[286,16,"#FFA868"],[304,16,"#FFA868"],[322,16,"#FFA868"],
  [340,16,"#FFA868"],[268,34,"#FF9050"],[286,34,"#FF9050"],[340,34,"#FF9050"],
  [358,34,"#FF9050"],[268,52,"#FF7A38"],[286,52,"#FF7A38"],[340,52,"#FF7A38"],
  [358,52,"#FF7A38"],[268,70,"#EE6422"],[286,70,"#EE6422"],[304,70,"#EE6422"],
  [322,70,"#EE6422"],[340,70,"#EE6422"],[268,88,"#DC5418"],[286,88,"#DC5418"],
  [268,106,"#CC4412"],[286,106,"#CC4412"],[268,124,"#BE380E"],[286,124,"#BE380E"],
  [394,16,"#FFA868"],[412,16,"#FFA868"],[430,16,"#FFA868"],[448,16,"#FFA868"],
  [466,16,"#FFA868"],[484,16,"#FFA868"],[394,34,"#FF9050"],[412,34,"#FF9050"],
  [394,52,"#FF7A38"],[412,52,"#FF7A38"],[394,70,"#EE6422"],[412,70,"#EE6422"],
  [430,70,"#EE6422"],[448,70,"#EE6422"],[466,70,"#EE6422"],[394,88,"#DC5418"],
  [412,88,"#DC5418"],[394,106,"#CC4412"],[412,106,"#CC4412"],[394,124,"#BE380E"],
  [412,124,"#BE380E"],[430,124,"#BE380E"],[448,124,"#BE380E"],[466,124,"#BE380E"],
  [484,124,"#BE380E"],[520,16,"#FFA868"],[538,16,"#FFA868"],[592,16,"#FFA868"],
  [610,16,"#FFA868"],[520,34,"#FF9050"],[538,34,"#FF9050"],[556,34,"#FF9050"],
  [592,34,"#FF9050"],[610,34,"#FF9050"],[520,52,"#FF7A38"],[538,52,"#FF7A38"],
  [556,52,"#FF7A38"],[592,52,"#FF7A38"],[610,52,"#FF7A38"],[520,70,"#EE6422"],
  [538,70,"#EE6422"],[574,70,"#EE6422"],[592,70,"#EE6422"],[610,70,"#EE6422"],
  [520,88,"#DC5418"],[538,88,"#DC5418"],[574,88,"#DC5418"],[592,88,"#DC5418"],
  [610,88,"#DC5418"],[520,106,"#CC4412"],[538,106,"#CC4412"],[592,106,"#CC4412"],
  [610,106,"#CC4412"],[520,124,"#BE380E"],[538,124,"#BE380E"],[592,124,"#BE380E"],
  [610,124,"#BE380E"],[646,16,"#FFA868"],[664,16,"#FFA868"],[682,16,"#FFA868"],
  [700,16,"#FFA868"],[718,16,"#FFA868"],[736,16,"#FFA868"],[646,34,"#FF9050"],
  [664,34,"#FF9050"],[646,52,"#FF7A38"],[664,52,"#FF7A38"],[646,70,"#EE6422"],
  [664,70,"#EE6422"],[682,70,"#EE6422"],[700,70,"#EE6422"],[718,70,"#EE6422"],
  [736,70,"#EE6422"],[718,88,"#DC5418"],[736,88,"#DC5418"],[718,106,"#CC4412"],
  [736,106,"#CC4412"],[646,124,"#BE380E"],[664,124,"#BE380E"],[682,124,"#BE380E"],
  [700,124,"#BE380E"],[718,124,"#BE380E"],[736,124,"#BE380E"],[772,16,"#FFA868"],
  [790,16,"#FFA868"],[808,16,"#FFA868"],[826,16,"#FFA868"],[844,16,"#FFA868"],
  [862,16,"#FFA868"],[772,34,"#FF9050"],[790,34,"#FF9050"],[772,52,"#FF7A38"],
  [790,52,"#FF7A38"],[772,70,"#EE6422"],[790,70,"#EE6422"],[808,70,"#EE6422"],
  [826,70,"#EE6422"],[844,70,"#EE6422"],[772,88,"#DC5418"],[790,88,"#DC5418"],
  [772,106,"#CC4412"],[790,106,"#CC4412"],[772,124,"#BE380E"],[790,124,"#BE380E"],
  [808,124,"#BE380E"],[826,124,"#BE380E"],[844,124,"#BE380E"],[862,124,"#BE380E"],
  [952,16,"#FFA868"],[970,16,"#FFA868"],[988,16,"#FFA868"],[1006,16,"#FFA868"],
  [1024,16,"#FFA868"],[1042,16,"#FFA868"],[988,34,"#FF9050"],[1006,34,"#FF9050"],
  [988,52,"#FF7A38"],[1006,52,"#FF7A38"],[988,70,"#EE6422"],[1006,70,"#EE6422"],
  [988,88,"#DC5418"],[1006,88,"#DC5418"],[988,106,"#CC4412"],[1006,106,"#CC4412"],
  [988,124,"#BE380E"],[1006,124,"#BE380E"],[1078,16,"#FFA868"],[1096,16,"#FFA868"],
  [1114,16,"#FFA868"],[1132,16,"#FFA868"],[1150,16,"#FFA868"],[1078,34,"#FF9050"],
  [1096,34,"#FF9050"],[1150,34,"#FF9050"],[1168,34,"#FF9050"],[1078,52,"#FF7A38"],
  [1096,52,"#FF7A38"],[1150,52,"#FF7A38"],[1168,52,"#FF7A38"],[1078,70,"#EE6422"],
  [1096,70,"#EE6422"],[1114,70,"#EE6422"],[1132,70,"#EE6422"],[1150,70,"#EE6422"],
  [1078,88,"#DC5418"],[1096,88,"#DC5418"],[1114,88,"#DC5418"],[1132,88,"#DC5418"],
  [1078,106,"#CC4412"],[1096,106,"#CC4412"],[1132,106,"#CC4412"],[1150,106,"#CC4412"],
  [1078,124,"#BE380E"],[1096,124,"#BE380E"],[1150,124,"#BE380E"],[1168,124,"#BE380E"],
  [1204,16,"#FFA868"],[1222,16,"#FFA868"],[1240,16,"#FFA868"],[1258,16,"#FFA868"],
  [1276,16,"#FFA868"],[1294,16,"#FFA868"],[1204,34,"#FF9050"],[1222,34,"#FF9050"],
  [1204,52,"#FF7A38"],[1222,52,"#FF7A38"],[1204,70,"#EE6422"],[1222,70,"#EE6422"],
  [1240,70,"#EE6422"],[1258,70,"#EE6422"],[1276,70,"#EE6422"],[1204,88,"#DC5418"],
  [1222,88,"#DC5418"],[1204,106,"#CC4412"],[1222,106,"#CC4412"],[1204,124,"#BE380E"],
  [1222,124,"#BE380E"],[1240,124,"#BE380E"],[1258,124,"#BE380E"],[1276,124,"#BE380E"],
  [1294,124,"#BE380E"],[1330,16,"#FFA868"],[1348,16,"#FFA868"],[1402,16,"#FFA868"],
  [1420,16,"#FFA868"],[1330,34,"#FF9050"],[1348,34,"#FF9050"],[1366,34,"#FF9050"],
  [1402,34,"#FF9050"],[1420,34,"#FF9050"],[1330,52,"#FF7A38"],[1348,52,"#FF7A38"],
  [1366,52,"#FF7A38"],[1402,52,"#FF7A38"],[1420,52,"#FF7A38"],[1330,70,"#EE6422"],
  [1348,70,"#EE6422"],[1384,70,"#EE6422"],[1402,70,"#EE6422"],[1420,70,"#EE6422"],
  [1330,88,"#DC5418"],[1348,88,"#DC5418"],[1384,88,"#DC5418"],[1402,88,"#DC5418"],
  [1420,88,"#DC5418"],[1330,106,"#CC4412"],[1348,106,"#CC4412"],[1402,106,"#CC4412"],
  [1420,106,"#CC4412"],[1330,124,"#BE380E"],[1348,124,"#BE380E"],[1402,124,"#BE380E"],
  [1420,124,"#BE380E"],[1456,16,"#FFA868"],[1474,16,"#FFA868"],[1492,16,"#FFA868"],
  [1510,16,"#FFA868"],[1528,16,"#FFA868"],[1456,34,"#FF9050"],[1474,34,"#FF9050"],
  [1528,34,"#FF9050"],[1546,34,"#FF9050"],[1456,52,"#FF7A38"],[1474,52,"#FF7A38"],
  [1528,52,"#FF7A38"],[1546,52,"#FF7A38"],[1456,70,"#EE6422"],[1474,70,"#EE6422"],
  [1528,70,"#EE6422"],[1546,70,"#EE6422"],[1456,88,"#DC5418"],[1474,88,"#DC5418"],
  [1528,88,"#DC5418"],[1546,88,"#DC5418"],[1456,106,"#CC4412"],[1474,106,"#CC4412"],
  [1528,106,"#CC4412"],[1546,106,"#CC4412"],[1456,124,"#BE380E"],[1474,124,"#BE380E"],
  [1492,124,"#BE380E"],[1510,124,"#BE380E"],[1528,124,"#BE380E"],[1582,16,"#FFA868"],
  [1600,16,"#FFA868"],[1618,16,"#FFA868"],[1636,16,"#FFA868"],[1654,16,"#FFA868"],
  [1672,16,"#FFA868"],[1582,34,"#FF9050"],[1600,34,"#FF9050"],[1582,52,"#FF7A38"],
  [1600,52,"#FF7A38"],[1582,70,"#EE6422"],[1600,70,"#EE6422"],[1618,70,"#EE6422"],
  [1636,70,"#EE6422"],[1654,70,"#EE6422"],[1672,70,"#EE6422"],[1654,88,"#DC5418"],
  [1672,88,"#DC5418"],[1654,106,"#CC4412"],[1672,106,"#CC4412"],[1582,124,"#BE380E"],
  [1600,124,"#BE380E"],[1618,124,"#BE380E"],[1636,124,"#BE380E"],[1654,124,"#BE380E"],
  [1672,124,"#BE380E"],
]

const minY = Math.min(...PIXELS.map(p => p[1]))
const maxY = Math.max(...PIXELS.map(p => p[1]))

function lerp(a, b, t) { return Math.round(a + (b - a) * t) }
function hex2(n) { return ('0' + Math.min(255, Math.max(0, n)).toString(16)).slice(-2) }

export default function TrendsLogo({ width = '100%', quick = false }) {
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
        r.style.animationName = 'trQuickFade'
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

      r.style.animationName = 'trPixelFall'
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
        @keyframes trQuickFade {
          0%   { opacity: 0; transform: translateY(-3px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes trPixelFall {
          0%   { opacity: 0; transform: translateY(-160px); }
          80%  { opacity: 1; transform: translateY(2px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .tr-logo-rect {
          transform-box: fill-box;
          transform-origin: center bottom;
        }
      `}</style>
      <svg
        ref={svgRef}
        width={width}
        viewBox="0 0 1706 158"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="crispEdges"
      >
        <defs>
          <filter id="tr-ds" x="-25%" y="-25%" width="160%" height="160%">
            <feDropShadow dx="0" dy="0" stdDeviation="12" floodColor="#FF5010" floodOpacity="0.09"/>
            <feDropShadow dx="4" dy="6" stdDeviation="2" floodColor="#1A0500" floodOpacity="1"/>
          </filter>
        </defs>
        <g filter="url(#tr-ds)">
          {PIXELS.map(([x, y, fill], i) => (
            <rect
              key={i}
              className="tr-logo-rect"
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
