"""
REIMS AI/ML Stack Verification
Tests all AI/ML components and identifies missing packages
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import importlib
from datetime import datetime

print("\n" + "="*70)
print("REIMS AI/ML STACK VERIFICATION")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

def test_package(package_name, import_name=None, purpose=""):
    """Test if a package is installed"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  PASS {package_name:30} v{version:15} - {purpose}")
        return True, version
    except ImportError:
        print(f"  FAIL {package_name:30} {'NOT INSTALLED':15} - {purpose}")
        return False, None

# Test 1: Local LLM
print("\n" + "="*70)
print("1. Local LLM - Ollama + LLaMA 3.1/Mistral")
print("="*70)

results = {}

# Ollama
results['ollama'], _ = test_package('ollama', 'ollama', 'Ollama API client')

# Test Ollama service
print("\n  Testing Ollama Service...")
try:
    import ollama
    models = ollama.list()
    available_models = [model['name'] for model in models.get('models', [])]
    if available_models:
        print(f"  PASS Ollama service running with {len(available_models)} models")
        for model in available_models:
            print(f"       - {model}")
        results['ollama_service'] = True
    else:
        print("  WARN Ollama service running but no models loaded")
        print("       Run: ollama pull llama3.1:8b")
        results['ollama_service'] = False
except Exception as e:
    print(f"  FAIL Ollama service not running: {e}")
    print("       Start with: ollama serve")
    results['ollama_service'] = False

# Test 2: LangChain
print("\n" + "="*70)
print("2. LangChain - Agent Framework")
print("="*70)

results['langchain'], _ = test_package('langchain', 'langchain', 'LangChain framework')
results['langchain-core'], _ = test_package('langchain-core', 'langchain_core', 'LangChain core')
results['langchain-community'], _ = test_package('langchain-community', 'langchain_community', 'LangChain community')
results['langchain-ollama'], _ = test_package('langchain-ollama', 'langchain_ollama', 'LangChain Ollama integration')

# Test 3: Vector Database
print("\n" + "="*70)
print("3. ChromaDB - Vector Database")
print("="*70)

results['chromadb'], _ = test_package('chromadb', 'chromadb', 'Vector database')

# Test ChromaDB service
print("\n  Testing ChromaDB Service...")
try:
    import chromadb
    client = chromadb.Client()
    print("  PASS ChromaDB client initialized successfully")
    
    # Try to create a test collection
    test_collection = client.create_collection(name="reims_test", get_or_create=True)
    print("  PASS ChromaDB collection creation working")
    client.delete_collection(name="reims_test")
    results['chromadb_service'] = True
except Exception as e:
    print(f"  FAIL ChromaDB service error: {e}")
    results['chromadb_service'] = False

# Test 4: Document Parsing
print("\n" + "="*70)
print("4. Document Parsing Libraries")
print("="*70)

results['pymupdf'], _ = test_package('PyMuPDF', 'fitz', 'PDF parsing (PyMuPDF)')
results['tabula'], _ = test_package('tabula-py', 'tabula', 'PDF table extraction')
results['camelot'], _ = test_package('camelot-py', 'camelot', 'PDF table extraction')
results['pdfplumber'], _ = test_package('pdfplumber', 'pdfplumber', 'PDF parsing alternative')
results['python-docx'], _ = test_package('python-docx', 'docx', 'DOCX parsing')

# Test 5: Machine Learning
print("\n" + "="*70)
print("5. Machine Learning - Anomaly Detection")
print("="*70)

results['scikit-learn'], _ = test_package('scikit-learn', 'sklearn', 'Machine learning library')
results['scipy'], _ = test_package('scipy', 'scipy', 'Scientific computing')
results['numpy'], _ = test_package('numpy', 'numpy', 'Numerical computing')
results['pandas'], _ = test_package('pandas', 'pandas', 'Data analysis')

# Test 6: Embeddings and NLP
print("\n" + "="*70)
print("6. Embeddings & NLP")
print("="*70)

results['sentence-transformers'], _ = test_package('sentence-transformers', 'sentence_transformers', 'Text embeddings')
results['transformers'], _ = test_package('transformers', 'transformers', 'Hugging Face Transformers')
results['spacy'], _ = test_package('spacy', 'spacy', 'NLP library')
results['nltk'], _ = test_package('nltk', 'nltk', 'Natural language toolkit')

# Test 7: Additional AI Tools
print("\n" + "="*70)
print("7. Additional AI/ML Tools")
print("="*70)

results['torch'], _ = test_package('torch', 'torch', 'PyTorch deep learning')
results['faiss'], _ = test_package('faiss-cpu', 'faiss', 'Facebook AI Similarity Search')
results['openai'], _ = test_package('openai', 'openai', 'OpenAI API (optional)')
results['anthropic'], _ = test_package('anthropic', 'anthropic', 'Claude API (optional)')

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Core components (REQUIRED)
core_components = {
    "Local LLM": ['ollama', 'ollama_service'],
    "Agent Framework": ['langchain', 'langchain-core'],
    "Vector Database": ['chromadb', 'chromadb_service'],
    "Document Parsing": ['pymupdf', 'tabula', 'camelot'],
    "ML Libraries": ['scikit-learn', 'scipy', 'numpy', 'pandas']
}

# Recommended components
recommended_components = {
    "Embeddings": ['sentence-transformers'],
    "Advanced NLP": ['spacy', 'transformers'],
    "LangChain Integrations": ['langchain-community', 'langchain-ollama']
}

# Optional components
optional_components = {
    "Deep Learning": ['torch'],
    "Vector Search": ['faiss'],
    "Cloud APIs": ['openai', 'anthropic'],
    "Additional Parsing": ['pdfplumber', 'python-docx', 'nltk']
}

def print_category(title, components, results_dict):
    total = sum(len(items) for items in components.values())
    installed = sum(1 for group in components.values() for item in group if results_dict.get(item, False))
    
    status = "PASS" if installed == total else "WARN" if installed > total//2 else "FAIL"
    print(f"\n{status} {title}: {installed}/{total} installed ({installed/total*100:.0f}%)")
    
    for category, items in components.items():
        cat_installed = sum(1 for item in items if results_dict.get(item, False))
        cat_status = "PASS" if cat_installed == len(items) else "WARN" if cat_installed > 0 else "FAIL"
        print(f"  {cat_status} {category:25} {cat_installed}/{len(items)}")

print_category("CORE COMPONENTS (Required)", core_components, results)
print_category("RECOMMENDED COMPONENTS", recommended_components, results)
print_category("OPTIONAL COMPONENTS", optional_components, results)

# Missing packages
print("\n" + "="*70)
print("MISSING PACKAGES")
print("="*70)

missing_core = []
missing_recommended = []
missing_optional = []

for category, items in core_components.items():
    for item in items:
        if not results.get(item, False):
            missing_core.append(item)

for category, items in recommended_components.items():
    for item in items:
        if not results.get(item, False):
            missing_recommended.append(item)

for category, items in optional_components.items():
    for item in items:
        if not results.get(item, False):
            missing_optional.append(item)

if missing_core:
    print("\nCRITICAL - Missing Core Components:")
    for pkg in missing_core:
        if pkg == 'ollama_service':
            print(f"  - Ollama service (run: ollama serve)")
        elif pkg == 'chromadb_service':
            print(f"  - ChromaDB service issue")
        elif pkg == 'tabula':
            print(f"  - tabula-py (run: pip install tabula-py)")
        else:
            print(f"  - {pkg}")

if missing_recommended:
    print("\nRECOMMENDED - Missing Recommended Components:")
    for pkg in missing_recommended:
        if pkg == 'sentence-transformers':
            print(f"  - {pkg} (run: pip install sentence-transformers)")
        elif pkg == 'langchain-ollama':
            print(f"  - {pkg} (run: pip install langchain-ollama)")
        elif pkg == 'langchain-community':
            print(f"  - {pkg} (run: pip install langchain-community)")
        else:
            print(f"  - {pkg}")

if missing_optional:
    print("\nOPTIONAL - Missing Optional Components:")
    print(f"  {len(missing_optional)} optional packages not installed")
    print("  (Not required for core functionality)")

# Installation commands
print("\n" + "="*70)
print("QUICK FIX COMMANDS")
print("="*70)

if missing_core:
    print("\nInstall Missing Core Components:")
    core_packages = [pkg for pkg in missing_core if not pkg.endswith('_service')]
    if core_packages:
        print(f"  pip install {' '.join(core_packages)}")
    if 'ollama_service' in missing_core:
        print("\n  # Start Ollama service:")
        print("  ollama serve")
        print("\n  # Pull LLaMA 3.1 model:")
        print("  ollama pull llama3.1:8b")

if missing_recommended:
    print("\nInstall Recommended Components:")
    print(f"  pip install {' '.join(missing_recommended)}")

# Final status
print("\n" + "="*70)
print("FINAL STATUS")
print("="*70)

core_installed = len([item for group in core_components.values() for item in group if results.get(item, False)])
core_total = sum(len(items) for items in core_components.values())
core_percentage = core_installed / core_total * 100

if core_percentage >= 90:
    print(f"\nPASS AI/ML Stack: {core_percentage:.0f}% operational")
    print("Your AI/ML stack is ready for production!")
elif core_percentage >= 70:
    print(f"\nWARN AI/ML Stack: {core_percentage:.0f}% operational")
    print("Some core components missing, but basic functionality available.")
elif core_percentage >= 50:
    print(f"\nWARN AI/ML Stack: {core_percentage:.0f}% operational")
    print("Several critical components missing.")
else:
    print(f"\nFAIL AI/ML Stack: {core_percentage:.0f}% operational")
    print("Major components missing. Please install missing packages.")

print("\n" + "="*70)


















