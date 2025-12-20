import json
import os
import locale
from typing import Dict, Any, Optional

class I18n:
    _instance = None
    _translations: Dict[str, Any] = {}
    _current_locale: str = 'en'
    _locale_dir: str = ''

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18n, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Default to system locale or fallback to 'en'
        sys_locale = locale.getdefaultlocale()[0]
        self._current_locale = sys_locale if sys_locale else 'en'
        
        # Determine locale directory (assuming standard structure relative to this file)
        # This file is in src/utils/i18n.py -> ../../locales
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._locale_dir = os.path.join(base_dir, 'locales')
        
        self.load_translations()

    def set_locale(self, locale_code: str):
        self._current_locale = locale_code
        self.load_translations()

    def load_translations(self):
        """Loads the translation file for the current locale."""
        # Clean locale code (e.g., pt_BR -> pt_BR, or en_US -> en)
        # Simplification: Try full code, then short code
        codes_to_try = [self._current_locale]
        if '_' in self._current_locale:
            codes_to_try.append(self._current_locale.split('_')[0])
            
        loaded = False
        for code in codes_to_try:
            file_path = os.path.join(self._locale_dir, f"{code}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._translations = json.load(f)
                    loaded = True
                    break
                except Exception as e:
                    print(f"Error loading locale {code}: {e}")
        
        if not loaded:
            # Fallback to empty or default English if crucial
            self._translations = {}

    def t(self, key: str, **kwargs) -> str:
        """Get translation for key. Supports nested keys (e.g. 'error.file_not_found')"""
        keys = key.split('.')
        val = self._translations
        
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                val = None
                break
        
        if val is None:
            return key # Return key if not found
        
        if isinstance(val, str):
            try:
                return val.format(**kwargs)
            except KeyError:
                return val
        
        return str(val)

# Global instance for easy access
i18n = I18n()
t = i18n.t
