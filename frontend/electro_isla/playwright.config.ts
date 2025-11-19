// @ts-check
// @ts-ignore
const { defineConfig, devices } = require('@playwright/test');

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎭 CONFIGURACIÓN DE PLAYWRIGHT
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Configuración para tests E2E del carrito de compras
 */

// @ts-ignore
module.exports = defineConfig({
  testDir: './tests/e2e',
  
  // Número máximo de workers en paralelo
  workers: 1,
  
  // Timeout para cada test (ms)
  timeout: 30 * 1000,
  
  // Timeout para expect (ms)
  expect: {
    timeout: 5000,
  },
  
  // Configuración de reportes
  reporter: [
    ['html'],
    ['list'],
  ],
  
  // Configuración de uso
  use: {
    // URL base para los tests
    baseURL: 'http://localhost:3000',
    
    // Tomar screenshot en caso de fallo
    screenshot: 'only-on-failure',
    
    // Grabar video en caso de fallo
    video: 'retain-on-failure',
    
    // Trace para debugging
    trace: 'on-first-retry',
  },
  
  // Proyectos (navegadores)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  
  // Servidor web para tests (opcional)
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    // @ts-ignore
    reuseExistingServer: !process.env.CI,
  },
});
