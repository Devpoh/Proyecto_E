import { useState, useEffect } from 'react';
import styles from './Hero.module.css';

const Hero = () => {
  const images = [
    'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=600&fit=crop',
    'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1200&h=600&fit=crop',
    'https://images.unsplash.com/photo-1540553016722-983e48a2cd10?w=1200&h=600&fit=crop',
    'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=1200&h=600&fit=crop',
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [images.length]);

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  return (
    <section className={styles.heroSection}>
      <div
        className={styles.carouselContainer}
        style={{
          transform: `translateX(-${currentIndex * 100}%)`,
        }}
      >
        {images.map((image, index) => (
          <div key={index} className={styles.slide}>
            <img
              src={image}
              alt={`Slide ${index + 1}`}
              className={styles.slideImage}
            />
            <div className={styles.overlay} />
          </div>
        ))}
      </div>

      <div className={styles.contentOverlay}>
        <h1 className={styles.title}>Bienvenido a Electro Isla</h1>
        <p className={styles.subtitle}>Tu tienda de electrónica de confianza</p>
        <button className={styles.ctaButton}>Explorar Productos</button>
      </div>

      <button
        onClick={goToPrevious}
        className={`${styles.navArrow} ${styles.prevArrow}`}
        aria-label="Slide anterior"
      >
        ‹
      </button>

      <button
        onClick={goToNext}
        className={`${styles.navArrow} ${styles.nextArrow}`}
        aria-label="Siguiente slide"
      >
        ›
      </button>

      <div className={styles.dotsContainer}>
        {images.map((_, index) => (
          <button
            key={index}
            onClick={() => goToSlide(index)}
            className={`${styles.dot} ${currentIndex === index ? styles.active : ''}`}
            aria-label={`Ir al slide ${index + 1}`}
          />
        ))}
      </div>
    </section>
  );
};

export default Hero;
