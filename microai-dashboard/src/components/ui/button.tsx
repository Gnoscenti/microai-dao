
import React from 'react'
type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'default'|'secondary'|'outline', size?: 'sm'|'md'|'lg'}
export function Button({ className='', variant='default', size='md', ...props }:Props){
  const base = 'inline-flex items-center justify-center gap-1 font-medium transition rounded-md focus:outline-none'
  const color = variant==='secondary' ? 'bg-zinc-800 text-zinc-100 hover:bg-zinc-700' :
                variant==='outline' ? 'border border-zinc-600/60 text-zinc-100 hover:bg-zinc-800/40' :
                'bg-fuchsia-600 hover:bg-fuchsia-500 text-white'
  const sz = size==='sm' ? 'text-sm px-3 py-1.5 rounded-full' : size==='lg' ? 'text-base px-5 py-3' : 'text-sm px-4 py-2'
  return <button className={`${base} ${color} ${sz} ${className}`} {...props} />
}
