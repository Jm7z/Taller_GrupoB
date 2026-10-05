"""Adaptador de compatibilidad: implementación vigente en concentracion.indices."""

import sys
from concentracion import indices as _modulo

sys.modules[__name__] = _modulo
