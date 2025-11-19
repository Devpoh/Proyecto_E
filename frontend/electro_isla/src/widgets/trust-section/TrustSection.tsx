/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛡️ WIDGET - TrustSection
 * ═══════════════════════════════════════════════════════════════════════════════
 * Sección de confianza y beneficios con iconos y badges
 * Las tarjetas son clickeables y navegan a la página de Sobre Nosotros
 */

import { useNavigate } from 'react-router-dom';
import { FiCreditCard, FiLock, FiCheckCircle, FiTruck } from 'react-icons/fi';
import './TrustSection.css';

export const TrustSection = () => {
  const navigate = useNavigate();

  const handleBenefitClick = () => {
    navigate('/nosotros');
  };

  const benefits = [
    {
      icon: FiCreditCard,
      title: 'Múltiples Pagos',
      description: 'TropiPay - Zelle',
      badge: 'PAGA COMO PREFIERAS',
      color: '#ffb800',
    },
    {
      icon: FiLock,
      title: 'Compra Segura',
      description: 'SSL + Encriptación bancaria',
      badge: '100% PROTEGIDO',
      color: '#ffb800'
    },
    {
      icon: FiCheckCircle,
      title: 'Garantía Total',
      description: 'Instalación + Soporte 24/7',
      badge: 'SERVICIO COMPLETO',
      color: '#ffb800',
      isGray: true
    },
    {
      icon: FiTruck,
      title: 'Entregas Seguras',
      description: 'A toda la isla en 24-48h',
      badge: 'ENTREGA SEGURA',
      color: '#ffb800'
    }
  ];

  return (
    <section className="trust-section">
      <div className="trust-container">
        <div className="trust-benefits">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <button 
                key={index} 
                className="trust-benefit-item"
                onClick={handleBenefitClick}
                aria-label={`Ir a más información sobre ${benefit.title}`}
              >
                <div className="trust-benefit-icon" style={{ color: benefit.color }}>
                  <Icon size={32} />
                </div>
                <div className="trust-benefit-content">
                  <h3 className="trust-benefit-title">{benefit.title}</h3>
                  <p className="trust-benefit-description">{benefit.description}</p>
                  <span className="trust-benefit-badge" style={{ backgroundColor: benefit.color }}>
                    {benefit.badge}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="trust-divider"></div>

        <div className="trust-footer">
          <p className="trust-footer-text">
            <strong>Electrónica Isla</strong> - Tu confianza es nuestra prioridad
          </p>
        </div>
      </div>
    </section>
  );
};
