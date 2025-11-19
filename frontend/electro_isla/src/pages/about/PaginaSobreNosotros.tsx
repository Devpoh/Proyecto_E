/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Sobre Nosotros
 * ═══════════════════════════════════════════════════════════════════════════════
 * Página que presenta la empresa, sus beneficios y cómo trabajamos
 * 
 * 🛡️ REGLAS APLICADAS:
 * - Regla 139: Arquitectura FSD - Capa pages
 * - Regla 127: TypeScript First
 * - Regla 147: Nomenclatura en español
 * - Regla 11: HTML Semántico
 * - Regla 158: Paleta de colores oficial
 * - Regla 146: Microinteracciones GPU-optimized
 */

import React from 'react';
import { FaShoppingCart, FaUserTie, FaTruck, FaHome, FaHeadset, FaTools, FaCreditCard, FaDollarSign, FaLock, FaShieldAlt, FaCheckCircle, FaAward, FaClock } from 'react-icons/fa';
import { Footer } from '@/widgets/footer';
import './PaginaSobreNosotros.css';

export const PaginaSobreNosotros: React.FC = () => {
  return (
    <>
    <main className="pagina-sobre-nosotros">
      {/* ===== HERO SECTION ===== */}
      <section className="hero-section">
        <div className="hero-overlay" aria-hidden="true"></div>
        <div className="hero-content">
          <h1 className="hero-titulo">
            Nuestra <span className="hero-highlight">Pasión</span>: Transformar hogares, crear <span className="hero-highlight">experiencias</span> únicas
          </h1>
          <p className="hero-descripcion">
            Más que una tienda, somos arquitectos de <span className="hero-highlight">sueños</span>. Cada electrodoméstico que elegimos 
            cuenta una historia de <span className="hero-highlight">innovación</span>, durabilidad y confianza para tu familia.
          </p>
        </div>
      </section>

      {/* ===== SECCIÓN: CÓMO TRABAJAMOS ===== */}
      <section className="como-trabajamos-section">
        <div className="container">
          {/* Header de la sección */}
          <div className="section-header">
            <h2 className="section-title">¿Cómo trabajamos?</h2>
            <p className="section-description">
              Elegimos el formato online porque creemos que la <span className="text-highlight">comodidad</span> y la <span className="text-highlight">transparencia</span> son fundamentales. 
              Te ofrecemos una experiencia de compra sin estrés, con <span className="text-highlight">asesoría personalizada</span> y <span className="text-highlight">garantía total</span> en cada paso.
            </p>
          </div>

          {/* Proceso en 3 pasos */}
          <div className="proceso-pasos">
            {/* Paso 1 */}
            <div className="paso-card">
              <div className="paso-icono">
                <FaShoppingCart size={48} />
              </div>
              <h3 className="paso-titulo">Compra Fácil</h3>
              <p className="paso-descripcion">
                Puedes elegir el producto desde la comodidad de tu hogar. 
                Navegación intuitiva y comparación rápida.
              </p>
            </div>

            {/* Paso 2 */}
            <div className="paso-card">
              <div className="paso-icono">
                <FaUserTie size={48} />
              </div>
              <h3 className="paso-titulo">Asesoría Especializada</h3>
              <p className="paso-descripcion">
                Nuestro equipo te ayuda a elegir el electrodoméstico perfecto 
                según tus necesidades y presupuesto.
              </p>
            </div>

            {/* Paso 3 */}
            <div className="paso-card">
              <div className="paso-icono">
                <FaTruck size={48} />
              </div>
              <h3 className="paso-titulo">Entrega e Instalación</h3>
              <p className="paso-descripcion">
                Te lo entregamos rápido y con la instalación incluida. 
                Sin complicaciones, sin sorpresas.
              </p>
            </div>
          </div>

          {/* Flechas hacia abajo */}
          <div className="paso-flecha-container">
            <div className="paso-flecha" aria-hidden="true">↓</div>
          </div>

          {/* Tarjetas de beneficios */}
          <div className="beneficios-grid">
            {/* Beneficio 1 */}
            <article className="beneficio-card">
              <div className="beneficio-icono">
                <FaHome size={48} />
              </div>
              <h3 className="beneficio-titulo">Compra desde Casa</h3>
              <p className="beneficio-descripcion">
                Catálogo completo disponible 24/7. Comparas, eliges y compras cuando quieras, sin presiones.
              </p>
            </article>

            {/* Beneficio 2 */}
            <article className="beneficio-card">
              <div className="beneficio-icono">
                <FaHeadset size={48} />
              </div>
              <h3 className="beneficio-titulo">Expertos a tu Servicio</h3>
              <p className="beneficio-descripcion">
                Asesoramiento personalizado por WhatsApp, teléfono o chat. 
                Te ayudamos a tomar la mejor decisión.
              </p>
            </article>

            {/* Beneficio 3 */}
            <article className="beneficio-card">
              <div className="beneficio-icono">
                <FaTools size={48} />
              </div>
              <h3 className="beneficio-titulo">Instalación Profesional</h3>
              <p className="beneficio-descripcion">
                Equipo técnico certificado. Instalamos tu electrodoméstico y te enseñamos cómo usarlo.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* ===== SECCIÓN: MÉTODOS DE PAGO ===== */}
      <section className="metodos-pago-section">
        <div className="container">
          <div className="seccion-layout">
            {/* Contenido Izquierda */}
            <div className="seccion-contenido">
              <div className="section-header">
                <h2 className="section-title">¿Por qué utilizamos TropiPay · Zelle?</h2>
                <p className="section-description">
                  Entendemos las realidades del mercado cubano y las necesidades de nuestros clientes. Por eso hemos seleccionado cuidadosamente dos métodos de pago confiables que garantizan seguridad y accesibilidad.
                </p>
              </div>

              <div className="metodos-grid">
                <article className="metodo-card">
                  <div className="metodo-icono">
                    <FaCreditCard size={48} />
                  </div>
                  <h3 className="metodo-titulo">TropiPay</h3>
                  <p className="metodo-descripcion">
                    Diseñado específicamente para cubanos
                  </p>
                </article>

                <article className="metodo-card">
                  <div className="metodo-icono">
                    <FaDollarSign size={48} />
                  </div>
                  <h3 className="metodo-titulo">Zelle</h3>
                  <p className="metodo-descripcion">
                    Transferencias bancarias instantáneas
                  </p>
                </article>
              </div>

              <p className="metodos-destacado">
                Hemos pensado en las diferentes necesidades: TropiPay para quienes están en Cuba, Zelle para transferencias rápidas desde Estados Unidos. Así garantizamos que todos puedan comprar de forma segura, sin importar su ubicación o preferencia financiera.
              </p>
            </div>

            {/* Imagen Derecha */}
            <div className="seccion-imagen">
              <img src="/SobreNosotros/pagos.png" alt="Métodos de pago seguros" />
            </div>
          </div>
        </div>
      </section>

      {/* ===== SECCIÓN: SEGURIDAD ===== */}
      <section className="seguridad-section">
        <div className="container">
          <div className="seccion-layout">
            {/* Contenido Izquierda */}
            <div className="seccion-contenido">
              <div className="section-header">
                <h2 className="section-title">Compra Segura • SSL + Encriptación Bancaria • 100% Protegido</h2>
                <p className="section-description">
                  Tu seguridad es nuestra máxima prioridad. Utilizamos la tecnología de encriptación más avanzada del mercado, con certificados SSL de grado bancario y protocolos de seguridad que garantizan que cada transacción esté completamente protegida.
                </p>
              </div>

              <div className="seguridad-grid">
                <article className="seguridad-card">
                  <div className="seguridad-icono">
                    <FaLock size={48} />
                  </div>
                  <h3 className="seguridad-titulo">SSL 256 bits</h3>
                  <p className="seguridad-descripcion">
                    Encriptación de nivel bancario
                  </p>
                </article>

                <article className="seguridad-card">
                  <div className="seguridad-icono">
                    <FaShieldAlt size={48} />
                  </div>
                  <h3 className="seguridad-titulo">Protección Total</h3>
                  <p className="seguridad-descripcion">
                    Datos 100% seguros
                  </p>
                </article>

                <article className="seguridad-card">
                  <div className="seguridad-icono">
                    <FaCheckCircle size={48} />
                  </div>
                  <h3 className="seguridad-titulo">Certificado</h3>
                  <p className="seguridad-descripcion">
                    Estándares internacionales
                  </p>
                </article>
              </div>

              <p className="seguridad-destacado">
                Cada compra está respaldada por encriptación SSL de 256 bits, la misma tecnología que usan los bancos más importantes del mundo. Tus datos personales y financieros están 100% seguros, con protocolos de seguridad que cumplen con los estándares internacionales más exigentes.
              </p>
            </div>

            {/* Imagen Derecha */}
            <div className="seccion-imagen">
              <img src="/SobreNosotros/Seguridad.png" alt="Seguridad en compras online" />
            </div>
          </div>
        </div>
      </section>

      {/* ===== SECCIÓN: GARANTÍA Y SOPORTE ===== */}
      <section className="garantia-section">
        <div className="container">
          <div className="seccion-layout seccion-layout-invertida">
            {/* Imagen Izquierda */}
            <div className="seccion-imagen">
              <img src="/SobreNosotros/garantia.png" alt="Garantía y soporte técnico" />
            </div>

            {/* Contenido Derecha */}
            <div className="seccion-contenido">
              <div className="section-header">
                <h2 className="section-title">Garantía Total • Instalación + Soporte 24/7 • Servicio Completo</h2>
                <p className="section-description">
                  Nuestro compromiso contigo no termina con la compra. Te ofrecemos garantía completa en todos nuestros productos, instalación profesional incluida y un equipo de soporte técnico disponible las 24 horas del día, los 7 días de la semana.
                </p>
              </div>

              <div className="garantia-grid">
                <article className="garantia-card">
                  <div className="garantia-icono">
                    <FaAward size={48} />
                  </div>
                  <h3 className="garantia-titulo">Garantía Extendida</h3>
                  <p className="garantia-descripcion">
                    Cobertura completa en todos los productos
                  </p>
                </article>

                <article className="garantia-card">
                  <div className="garantia-icono">
                    <FaTools size={48} />
                  </div>
                  <h3 className="garantia-titulo">Instalación Profesional</h3>
                  <p className="garantia-descripcion">
                    Técnicos certificados incluidos
                  </p>
                </article>

                <article className="garantia-card">
                  <div className="garantia-icono">
                    <FaClock size={48} />
                  </div>
                  <h3 className="garantia-titulo">Soporte 24/7</h3>
                  <p className="garantia-descripcion">
                    Asistencia inmediata sin costo
                  </p>
                </article>
              </div>

              <p className="garantia-destacado">
                Tu tranquilidad es nuestra responsabilidad. Cada electrodoméstico viene con garantía extendida, instalación realizada por técnicos certificados y soporte continuo. Si tienes algún problema, nuestro equipo especializado estará disponible inmediatamente para solucionarlo, sin costo adicional.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== SECCIÓN: ENVÍO Y ENTREGA ===== */}
      <section className="envio-section">
        <div className="container">
          <div className="seccion-layout">
            {/* Contenido Izquierda */}
            <div className="seccion-contenido">
              <div className="section-header">
                <h2 className="section-title">Envío • Entrega en La Habana</h2>
                <p className="section-description">
                  Llevamos tu electrodoméstico hasta la puerta de tu casa. Cubrimos La Habana con nuestro servicio de entrega rápida y confiable, garantizando que recibas tu compra en perfecto estado.
                </p>
              </div>

              <div className="envio-grid">
                <article className="envio-card">
                  <div className="envio-icono">
                    <FaTruck size={48} />
                  </div>
                  <h3 className="envio-titulo">Entrega Rápida</h3>
                  <p className="envio-descripcion">
                    Servicio de entrega confiable
                  </p>
                </article>

                <article className="envio-card">
                  <div className="envio-icono">
                    <FaShieldAlt size={48} />
                  </div>
                  <h3 className="envio-titulo">Empaque Seguro</h3>
                  <p className="envio-descripcion">
                    Protección total del producto
                  </p>
                </article>

                <article className="envio-card">
                  <div className="envio-icono">
                    <FaCheckCircle size={48} />
                  </div>
                  <h3 className="envio-titulo">Entrega Puntual</h3>
                  <p className="envio-descripcion">
                    Cumplimos con los tiempos
                  </p>
                </article>
              </div>

              <p className="envio-destacado">
                Entrega garantizada sin sorpresas. Tu pedido llegará en La Habana en el tiempo acordado. Nuestro equipo de logística se encarga de todo: empaque seguro, transporte cuidadoso y entrega puntual. Tu única preocupación será disfrutar tu nuevo electrodoméstico.
              </p>
            </div>

            {/* Imagen Derecha */}
            <div className="seccion-imagen">
              <img src="/SobreNosotros/entregas.png" alt="Servicio de entrega" />
            </div>
          </div>
        </div>
      </section>
    </main>

    {/* ===== FOOTER ===== */}
    <Footer />
  </>
  );
};
