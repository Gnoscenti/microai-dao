
import React from 'react'
export function Separator({ className='' }:{className?:string}){
  return <div className={`w-full h-px bg-white/10 ${className}`} />
}
