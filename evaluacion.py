"""Adaptador de compatibilidad: implementación vigente en concentracion.evaluacion."""

import sys
from concentracion import evaluacion as _modulo

sys.modules[__name__] = _modulo
