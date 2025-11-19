/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📅 DATE RANGE FILTER - Componente reutilizable para filtros de fecha
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { FiCalendar } from 'react-icons/fi';
import './DateRangeFilter.css';

export type DateRangeOption = 'today' | 'week' | 'month' | '3months' | '6months' | 'year' | 'all';

interface DateRangeFilterProps {
  value: DateRangeOption;
  onChange: (value: DateRangeOption) => void;
  label?: string;
}

const dateRangeOptions: { value: DateRangeOption; label: string }[] = [
  { value: 'today', label: 'Hoy' },
  { value: 'week', label: 'Última Semana' },
  { value: 'month', label: 'Último Mes' },
  { value: '3months', label: 'Últimos 3 Meses' },
  { value: '6months', label: 'Últimos 6 Meses' },
  { value: 'year', label: 'Último Año' },
  { value: 'all', label: 'Todo el Tiempo' },
];

export const DateRangeFilter = ({ 
  value, 
  onChange, 
  label = 'Período de Tiempo' 
}: DateRangeFilterProps) => {
  return (
    <div className="date-range-filter">
      <label className="date-range-label">
        <FiCalendar />
        <span>{label}</span>
      </label>
      <select
        className="date-range-select"
        value={value}
        onChange={(e) => onChange(e.target.value as DateRangeOption)}
      >
        {dateRangeOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

/**
 * Función helper para calcular las fechas según el rango seleccionado
 */
export const getDateRange = (option: DateRangeOption): { desde: string | null; hasta: string | null } => {
  const now = new Date();
  const hasta = now.toISOString();
  let desde: Date | null = null;

  switch (option) {
    case 'today':
      desde = new Date(now.setHours(0, 0, 0, 0));
      break;
    case 'week':
      desde = new Date(now.setDate(now.getDate() - 7));
      break;
    case 'month':
      desde = new Date(now.setMonth(now.getMonth() - 1));
      break;
    case '3months':
      desde = new Date(now.setMonth(now.getMonth() - 3));
      break;
    case '6months':
      desde = new Date(now.setMonth(now.getMonth() - 6));
      break;
    case 'year':
      desde = new Date(now.setFullYear(now.getFullYear() - 1));
      break;
    case 'all':
      return { desde: null, hasta: null };
  }

  return {
    desde: desde ? desde.toISOString() : null,
    hasta,
  };
};
