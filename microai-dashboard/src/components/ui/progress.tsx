
import React from 'react'
export function Progress({ value=0, className='' }:{ value:number, className?:string }){
  return (
    <div className={`w-full h-2 rounded-full bg-zinc-800/80 overflow-hidden ${className}`}>
      <div className="h-full bg-emerald-500" style={{ width: `${Math.min(100, Math.max(0, value))}%`}} />
    </div>
  )
}
