export default function Logo({ size = 48 }) {
  // 19×19 pixel art grid — same pixels as the Streamlit version
  const pixels = [
    // row, col, shade  (shade: 0=darkest .. 4=lightest)
    // ── $ sign ──
    [1,8,2],[1,9,3],[1,10,2],
    [2,7,1],[2,8,3],[2,9,4],[2,10,3],[2,11,1],
    [3,7,2],[3,8,3],[3,9,2],[3,11,2],
    [4,7,2],[4,8,3],[4,9,3],[4,10,2],
    [5,8,2],[5,9,3],[5,10,3],[5,11,2],
    [6,7,1],[6,9,2],[6,10,3],[6,11,2],
    [7,7,2],[7,8,3],[7,9,4],[7,10,3],[7,11,1],
    [8,8,2],[8,9,3],[8,10,2],
    // ── check mark ──
    [11,12,3],[11,13,4],
    [12,11,2],[12,12,3],[12,13,3],[12,14,2],
    [13,5,2],[13,10,2],[13,11,3],[13,12,4],[13,13,2],
    [14,5,3],[14,6,2],[14,9,2],[14,10,3],[14,11,2],
    [15,5,4],[15,6,3],[15,7,2],[15,8,2],[15,9,3],[15,10,2],
    [16,6,3],[16,7,4],[16,8,3],[16,9,2],
    [17,7,2],[17,8,3],
  ]

  const shades = ['#8B3010','#C03808','#E85520','#FF7030','#FFA868']
  const px = size / 19
  const W = size
  const H = size

  return (
    <svg
      width={W} height={H}
      viewBox={`0 0 ${W} ${H}`}
      xmlns="http://www.w3.org/2000/svg"
      style={{ filter: 'drop-shadow(3px 4px 5px rgba(10,1,0,0.65))' }}
      shapeRendering="crispEdges"
    >
      {pixels.map(([r, c, s], i) => (
        <rect
          key={i}
          x={c * px - 0.5}
          y={r * px - 0.5}
          width={px + 1}
          height={px + 1}
          fill={shades[s]}
        />
      ))}
    </svg>
  )
}
