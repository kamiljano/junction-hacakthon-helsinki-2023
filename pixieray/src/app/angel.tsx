'use client';

import Image from "next/image";

interface AngelProps {
  blinkCount: number;
}

interface OverlayProps {
  left?: number;
  top?: number;
  bottom?: number;
  right?: number;
  img: string;
  height: number;
  width: number;
}

function Overlay(props: OverlayProps) {
  return <div style={{position: "absolute", zIndex: 999, top: props.top, left: props.left, bottom: props.bottom, right: props.right}}>
    <Image src={props.img} alt={props.img} width={props.width} height={props.height}/>
  </div>
}

const startShowingAngelAt = 3;

export default function Angel({ blinkCount }: AngelProps) {
  const angels: OverlayProps[] = [
    {
      img: '/angel1.gif',
      top: 100,
      left: 100,
      width: 100,
      height: 100,
    },
    {
      img: '/angel2.png',
      bottom: 100,
      right: 100,
      width: 200,
      height: 200,
    },
    {
      img: '/angel3.png',
      bottom: 100,
      left: 100,
      width: 400,
      height: 400,
    },
    {
      img: '/angel4.jpg',
      top: 0,
      left: 0,
      width: window.outerWidth,
      height: window.outerHeight
    },
  ];

  if (blinkCount < startShowingAngelAt) {
    return undefined;
  }

  const blink = blinkCount - startShowingAngelAt >= angels.length ? angels.length - 1 : blinkCount - startShowingAngelAt;

  return <Overlay {...angels[blink]} />;
}
