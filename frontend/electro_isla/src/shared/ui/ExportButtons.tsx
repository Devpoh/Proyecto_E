/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📤 EXPORT BUTTONS - Componente reutilizable para exportar PDF/Excel
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { FiFileText, FiFile } from 'react-icons/fi';
import './ExportButtons.css';

interface ExportButtonsProps {
  onExportPDF: () => void;
  onExportExcel: () => void;
  pdfLabel?: string;
  excelLabel?: string;
  disabled?: boolean;
}

export const ExportButtons = ({ 
  onExportPDF, 
  onExportExcel, 
  pdfLabel = 'Exportar PDF',
  excelLabel = 'Exportar Excel',
  disabled = false
}: ExportButtonsProps) => {
  return (
    <div className="export-buttons">
      <button
        className="export-btn export-btn-pdf"
        onClick={onExportPDF}
        disabled={disabled}
        title={pdfLabel}
      >
        <FiFileText />
        <span>{pdfLabel}</span>
      </button>
      <button
        className="export-btn export-btn-excel"
        onClick={onExportExcel}
        disabled={disabled}
        title={excelLabel}
      >
        <FiFile />
        <span>{excelLabel}</span>
      </button>
    </div>
  );
};
