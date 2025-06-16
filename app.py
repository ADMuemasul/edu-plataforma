#!/usr/bin/env python3
"""
EDU PLATAFORMA - Sistema Educacional Completo
Deploy limpo para Railway
"""

import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar sistema completo
from app import app

# Para Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 