/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENT - AnimatedTitle
 * ═══════════════════════════════════════════════════════════════════════════════
 * Título con línea dorada animada que aparece al entrar en viewport
 */

import { useEffect, useRef, useState } from 'react';
import './AnimatedTitle.css';

interface AnimatedTitleProps {
  text: string;
}

export const AnimatedTitle = ({ text }: AnimatedTitleProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const underlineRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold: 0.5,
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      if (containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, []);

  // Ajustar ancho de la línea al ancho del título
  useEffect(() => {
    if (titleRef.current && underlineRef.current) {
      const titleWidth = titleRef.current.offsetWidth;
      underlineRef.current.style.width = `${titleWidth}px`;
    }
  }, [text]);

  return (
    <div className="titulo-container" ref={containerRef}>
      <h1 className="titulo" ref={titleRef}>{text}</h1>
      <div className={`titulo-underline ${isVisible ? 'active' : ''}`} ref={underlineRef}></div>
    </div>
  );
};
