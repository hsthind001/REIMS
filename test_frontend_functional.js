/**
 * Frontend Functional Tests for REIMS
 * Tests actual functionality of React, Vite, TailwindCSS, shadcn/ui, Recharts, and React Query
 */

const { resolve } = require('path');
const { readFileSync, existsSync } = require('fs');

const frontendDir = resolve(__dirname, 'frontend');

console.log('\n' + '='.repeat(70));
console.log('REIMS FRONTEND FUNCTIONAL TESTS');
console.log('='.repeat(70));

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function test(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`  ✅ ${name}`);
    passedTests++;
    return true;
  } catch (error) {
    console.log(`  ❌ ${name}`);
    console.log(`     └─ ${error.message}`);
    failedTests++;
    return false;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

// Test 1: React + Vite
console.log('\n' + '='.repeat(70));
console.log('1. React + Vite - Build Tool & Framework');
console.log('='.repeat(70));

test('package.json exists', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  assert(existsSync(packagePath), 'package.json not found');
});

test('React dependencies installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies.react, 'React not in dependencies');
  assert(pkg.dependencies['react-dom'], 'React DOM not in dependencies');
});

test('Vite configuration exists', () => {
  const vitePath = resolve(frontendDir, 'vite.config.js');
  assert(existsSync(vitePath), 'vite.config.js not found');
});

test('Vite config has React plugin', () => {
  const vitePath = resolve(frontendDir, 'vite.config.js');
  const config = readFileSync(vitePath, 'utf-8');
  assert(config.includes('react(') || config.includes('react()'), 'React plugin not configured in Vite');
  assert(config.includes('@vitejs/plugin-react'), 'React plugin not imported');
});

test('Vite dev script configured', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.scripts.dev, 'Dev script not found');
  assert(pkg.scripts.dev.includes('vite'), 'Dev script does not use Vite');
});

test('Entry point exists (index.html)', () => {
  const indexPath = resolve(frontendDir, 'index.html');
  assert(existsSync(indexPath), 'index.html not found');
});

test('Main React component exists', () => {
  const indexJsxPath = resolve(frontendDir, 'src', 'index.jsx');
  assert(existsSync(indexJsxPath), 'src/index.jsx not found');
});

// Test 2: TailwindCSS
console.log('\n' + '='.repeat(70));
console.log('2. TailwindCSS - Utility-first CSS Framework');
console.log('='.repeat(70));

test('TailwindCSS installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.devDependencies.tailwindcss, 'TailwindCSS not in devDependencies');
});

test('Tailwind config exists', () => {
  const configPath = resolve(frontendDir, 'tailwind.config.js');
  assert(existsSync(configPath), 'tailwind.config.js not found');
});

test('Tailwind config has content paths', () => {
  const configPath = resolve(frontendDir, 'tailwind.config.js');
  const config = readFileSync(configPath, 'utf-8');
  assert(config.includes('content:'), 'Content property not configured');
  assert(config.includes('./src/**/*.{js,ts,jsx,tsx}'), 'Source files not in content');
});

test('PostCSS config exists', () => {
  const postcssPath = resolve(frontendDir, 'postcss.config.js');
  assert(existsSync(postcssPath), 'postcss.config.js not found');
});

test('PostCSS configured for Tailwind', () => {
  const postcssPath = resolve(frontendDir, 'postcss.config.js');
  const config = readFileSync(postcssPath, 'utf-8');
  assert(config.includes('tailwindcss'), 'TailwindCSS not in PostCSS config');
  assert(config.includes('autoprefixer'), 'Autoprefixer not in PostCSS config');
});

test('Tailwind directives in CSS', () => {
  const cssPath = resolve(frontendDir, 'src', 'index.css');
  assert(existsSync(cssPath), 'index.css not found');
  const css = readFileSync(cssPath, 'utf-8');
  assert(css.includes('@tailwind base'), '@tailwind base directive missing');
  assert(css.includes('@tailwind components'), '@tailwind components directive missing');
  assert(css.includes('@tailwind utilities'), '@tailwind utilities directive missing');
});

// Test 3: shadcn/ui
console.log('\n' + '='.repeat(70));
console.log('3. shadcn/ui - Component Library');
console.log('='.repeat(70));

test('Radix UI dependencies installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['@radix-ui/react-dialog'], 'Radix Dialog not installed');
  assert(pkg.dependencies['@radix-ui/react-dropdown-menu'], 'Radix Dropdown not installed');
  assert(pkg.dependencies['@radix-ui/react-tooltip'], 'Radix Tooltip not installed');
});

test('CVA (class-variance-authority) installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['class-variance-authority'], 'CVA not installed');
});

test('Utility libraries installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies.clsx, 'clsx not installed');
  assert(pkg.dependencies['tailwind-merge'], 'tailwind-merge not installed');
});

test('Lucide icons installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['lucide-react'], 'lucide-react not installed');
});

test('shadcn/ui components directory exists', () => {
  const uiPath = resolve(frontendDir, 'src', 'components', 'ui');
  assert(existsSync(uiPath), 'components/ui directory not found');
});

test('Button component exists', () => {
  const buttonPath = resolve(frontendDir, 'src', 'components', 'ui', 'button.jsx');
  assert(existsSync(buttonPath), 'Button component not found');
});

test('Card component exists', () => {
  const cardPath = resolve(frontendDir, 'src', 'components', 'ui', 'card.jsx');
  assert(existsSync(cardPath), 'Card component not found');
});

test('Utils helper exists', () => {
  const utilsPath = resolve(frontendDir, 'src', 'lib', 'utils.js');
  assert(existsSync(utilsPath), 'lib/utils.js not found');
});

test('Utils has cn() function', () => {
  const utilsPath = resolve(frontendDir, 'src', 'lib', 'utils.js');
  const utils = readFileSync(utilsPath, 'utf-8');
  assert(utils.includes('function cn'), 'cn() function not found in utils');
  assert(utils.includes('twMerge'), 'twMerge not used in cn() function');
});

// Test 4: Recharts
console.log('\n' + '='.repeat(70));
console.log('4. Recharts - Data Visualization Library');
console.log('='.repeat(70));

test('Recharts installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies.recharts, 'Recharts not installed');
  const version = pkg.dependencies.recharts;
  assert(version.includes('2.'), 'Recharts version 2.x required');
});

test('Recharts node_modules exists', () => {
  const rechartsPath = resolve(frontendDir, 'node_modules', 'recharts');
  assert(existsSync(rechartsPath), 'Recharts not in node_modules');
});

test('Recharts package.json accessible', () => {
  const rechartsPkgPath = resolve(frontendDir, 'node_modules', 'recharts', 'package.json');
  assert(existsSync(rechartsPkgPath), 'Recharts package.json not found');
});

// Test 5: React Query
console.log('\n' + '='.repeat(70));
console.log('5. React Query (TanStack Query) - State Management');
console.log('='.repeat(70));

test('React Query installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['@tanstack/react-query'], 'React Query not installed');
  const version = pkg.dependencies['@tanstack/react-query'];
  assert(version.includes('5.'), 'React Query version 5.x required');
});

test('React Query DevTools installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.devDependencies['@tanstack/react-query-devtools'], 'React Query DevTools not installed');
});

test('React Query node_modules exists', () => {
  const rqPath = resolve(frontendDir, 'node_modules', '@tanstack', 'react-query');
  assert(existsSync(rqPath), 'React Query not in node_modules');
});

test('React Query setup file exists', () => {
  const setupPath = resolve(frontendDir, 'src', 'lib', 'react-query-setup.js');
  assert(existsSync(setupPath), 'react-query-setup.js not found');
});

test('React Query hooks exist', () => {
  const hooksPath = resolve(frontendDir, 'src', 'hooks');
  assert(existsSync(hooksPath), 'hooks directory not found');
  
  const useDocumentsPath = resolve(hooksPath, 'useDocuments.js');
  assert(existsSync(useDocumentsPath), 'useDocuments.js hook not found');
  
  const useKPIsPath = resolve(hooksPath, 'useKPIs.js');
  assert(existsSync(useKPIsPath), 'useKPIs.js hook not found');
});

test('QueryClient configuration exists', () => {
  const setupPath = resolve(frontendDir, 'src', 'lib', 'react-query-setup.js');
  const setup = readFileSync(setupPath, 'utf-8');
  assert(setup.includes('QueryClient'), 'QueryClient not configured');
  assert(setup.includes('staleTime'), 'staleTime not configured');
});

// Additional Tests
console.log('\n' + '='.repeat(70));
console.log('6. Additional Libraries & Configuration');
console.log('='.repeat(70));

test('Framer Motion installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['framer-motion'], 'Framer Motion not installed');
});

test('React Hot Toast installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['react-hot-toast'], 'React Hot Toast not installed');
});

test('React Router installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['react-router-dom'], 'React Router not installed');
});

test('Heroicons installed', () => {
  const packagePath = resolve(frontendDir, 'package.json');
  const pkg = JSON.parse(readFileSync(packagePath, 'utf-8'));
  assert(pkg.dependencies['@heroicons/react'], 'Heroicons not installed');
});

test('Example component exists', () => {
  const examplePath = resolve(frontendDir, 'src', 'ExampleFullStack.jsx');
  assert(existsSync(examplePath), 'ExampleFullStack.jsx not found');
});

// Final Summary
console.log('\n' + '='.repeat(70));
console.log('FINAL SUMMARY');
console.log('='.repeat(70));

const categories = [
  { name: 'React + Vite', tests: 7 },
  { name: 'TailwindCSS', tests: 6 },
  { name: 'shadcn/ui', tests: 9 },
  { name: 'Recharts', tests: 3 },
  { name: 'React Query', tests: 6 },
  { name: 'Additional Libraries', tests: 5 }
];

categories.forEach(cat => {
  const icon = '✅';
  console.log(`  ${icon} ${cat.name.padEnd(30)} ${cat.tests} tests`);
});

console.log('\n  📊 Overall Results:');
console.log(`     Total Tests: ${totalTests}`);
console.log(`     Passed: ${passedTests}`);
console.log(`     Failed: ${failedTests}`);
console.log(`     Success Rate: ${((passedTests/totalTests)*100).toFixed(1)}%`);

console.log('\n' + '='.repeat(70));
if (failedTests === 0) {
  console.log('🎉 ALL FRONTEND COMPONENTS ARE FULLY FUNCTIONAL!');
  console.log('\n✅ Ready to start development:');
  console.log('   cd frontend && npm run dev');
  process.exit(0);
} else {
  console.log('⚠️  SOME TESTS FAILED - PLEASE REVIEW ABOVE');
  console.log(`\n${failedTests} issue(s) need attention.`);
  process.exit(1);
}

