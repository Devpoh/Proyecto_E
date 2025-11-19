import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiSearch } from 'react-icons/fi';
import styles from './SearchBar.module.css';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Buscar productos...',
  onSearch,
  className = ''
}) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setIsLoading(true);
      
      // Simular loading de 0.6 segundos
      setTimeout(() => {
        // Si está en productos, solo actualiza la búsqueda
        if (location.pathname === '/productos') {
          if (onSearch) {
            onSearch(query.trim());
          }
        } else {
          // Si no está en productos, navega con la búsqueda
          navigate(`/productos?busqueda=${encodeURIComponent(query.trim())}`);
        }
        setIsLoading(false);
        setQuery('');
      }, 600);
    }
  };

  return (
    <form 
      className={`${styles.searchForm} ${className}`} 
      onSubmit={handleSubmit}
      role="search"
    >
      <div className={styles.searchContainer}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className={styles.searchInput}
          aria-label="Buscar productos"
        />
        <button 
          type="submit" 
          className={styles.searchButton}
          aria-label="Buscar"
          disabled={isLoading}
        >
          <FiSearch className={styles.searchIcon} style={{ opacity: isLoading ? 0.5 : 1 }} />
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
