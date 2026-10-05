"""Adaptador de compatibilidad: implementación vigente en concentracion.simulacion."""

import sys
from concentracion import simulacion as _modulo

sys.modules[__name__] = _modulo
