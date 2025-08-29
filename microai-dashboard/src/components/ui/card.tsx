
import React from 'react'
export function Card({ className='', children }:{className?:string, children:React.ReactNode}){
  return <div className={`rounded-2xl border border-white/10 bg-zinc-900/60 ${className}`}>{children}</div>
}
export function CardContent({ className='', children }:{className?:string, children:React.ReactNode}){
  return <div className={`p-4 ${className}`}>{children}</div>
}
