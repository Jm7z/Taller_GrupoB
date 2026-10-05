"""Adaptador de compatibilidad: implementación vigente en concentracion.graficos."""

import sys
from concentracion import graficos as _modulo

sys.modules[__name__] = _modulo
