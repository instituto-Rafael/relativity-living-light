import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import ptBR from './locales/pt.json'
import enUS from './locales/en.json'
import esES from './locales/es.json'
import frFR from './locales/fr.json'
import deDE from './locales/de.json'

const resources = {
  'pt-BR': { translation: ptBR },
  'en-US': { translation: enUS },
  'es-ES': { translation: esES },
  'fr-FR': { translation: frFR },
  'de-DE': { translation: deDE },
}

const savedLanguage = localStorage.getItem('language') || 'pt-BR'

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'en-US',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
