/* ============================================
   HARI MARG — Global Application JavaScript
   ============================================ */

// ---- Language Toggle & Translations (EN/MR) ----
const HariMarg = {
  lang: localStorage.getItem('hm_lang') || 'en',

  translations: {
    // Navigation
    'home': { en: 'Home', mr: 'मुख्यपृष्ठ' },
    'route': { en: 'Route', mr: 'मार्ग' },
    'near_me': { en: 'Near Me', mr: 'माझ्याजवळ' },
    'weather': { en: 'Weather', mr: 'हवामान' },
    'track_dindi': { en: 'Track Dindi', mr: 'दिंडी ट्रॅक करा' },
    'seva': { en: 'Seva', mr: 'सेवा' },
    'emergency': { en: 'Emergency', mr: 'आपत्कालीन' },
    'profile': { en: 'Profile', mr: 'प्रोफाइल' },

    // Homepage Hero
    'hero_title_main': { en: 'Hari Marg', mr: 'हरी मार्ग' },
    'hero_title_sub': { en: 'Your Digital Wari Companion', mr: 'तुमचा डिजिटल वारी सोबती' },
    'hero_desc': { 
      en: 'Walk the sacred road to Pandharpur with confidence — live palkhi routes, nearby seva stops, and weather along the way, all in one devoted companion.',
      mr: 'पंढरपूरच्या पवित्र मार्गावर विश्वासाने चाला — थेट पालखी मार्ग, जवळची सेवा केंद्रे आणि हवामान सल्ला, सर्व एकाच सोबत्यामध्ये.' 
    },
    'fetch_location': { en: 'Fetch My Location', mr: 'माझे स्थान शोधा' },
    'explore_route': { en: 'Explore Route', mr: 'मार्ग पहा' },
    
    // Hero Stats
    'stat_1_val': { en: '250 km', mr: '२५० किमी' },
    'stat_1_lbl': { en: 'Sacred route', mr: 'पवित्र मार्ग' },
    'stat_2_val': { en: '21 days', mr: '२१ दिवस' },
    'stat_2_lbl': { en: 'Traditional Wari', mr: 'पारंपारिक वारी' },
    'stat_3_val': { en: '9 lakh+', mr: '९ लाख+' },
    'stat_3_lbl': { en: 'Warkaris walking', mr: 'वारकरी सहभागी' },

    // Floating Chips
    'chip_next_stop_lbl': { en: 'Next stop', mr: 'पुढील मुक्काम' },
    'chip_next_stop_val': { en: 'Wakhari · 4 km', mr: 'वाखरी · ४ किमी' },
    'chip_today_lbl': { en: 'Today', mr: 'आजचे हवामान' },
    'chip_today_val': { en: '28° · Light rain', mr: '२८° · हलका पाऊस' },

    // Map Card
    'map_card_title': { en: 'Pandharpur Wari Live Map', mr: 'पंढरपूर वारी थेट नकाशा' },
    'map_card_subtitle': { en: 'Track real-time Palkhi positions & route stops', mr: 'पालखीचे थेट स्थान आणि मार्ग थांबे पहा' },
    'map_tap_instruction': { en: '📍 Tap anywhere on the map to set your location manually', mr: '📍 नकाशावर कुठेही स्पर्श करून आपले स्थान ठरवा' },
    'listen': { en: '📢 Listen', mr: '📢 ऐका' },

    // Features Section
    'features_heading': { en: 'Everything for your Wari', mr: 'तुमच्या वारीसाठी सर्वकाही' },
    'features_subheading': { 
      en: 'From the first step in Alandi to darshan at Pandharpur, Hari Marg walks with you.',
      mr: 'आळंदीतील पहिल्या पावलापासून पंढरपुरातील दर्शनापर्यंत, हरी मार्ग तुमच्यासोबत आहे.'
    },

    // Feature Cards
    'f1_title': { en: 'Wari Route', mr: 'वारी मार्ग' },
    'f1_desc': { en: 'Follow the live palkhi path from Alandi & Dehu to Pandharpur.', mr: 'आळंदी आणि देहूपासून पंढरपूरपर्यंतच्या पालखी मार्गाचे थेट अनुसरण करा.' },
    'f2_title': { en: 'Near Me', mr: 'माझ्याजवळ' },
    'f2_desc': { en: 'Find seva camps, water points, and rest stops around you.', mr: 'तुमच्या सभोवतालची सेवा शिबिरे, पाणी केंद्र आणि विश्रामस्थाने शोधा.' },
    'f3_title': { en: 'Weather', mr: 'हवामान' },
    'f3_desc': { en: 'Monsoon forecasts and heat alerts along the day\'s march.', mr: 'दिवसभराच्या वाटचालीत पावसाचा अंदाज आणि उष्णतेचे इशारे.' },
    'f4_title': { en: 'My Journey', mr: 'माझा प्रवास' },
    'f4_desc': { en: 'Track distance walked, dindi group, and darshan slots.', mr: 'चाललेले अंतर, दिंडी गट आणि दर्शन वेळापत्रक ट्रॅक करा.' },
    'f5_title': { en: 'Track Dindi', mr: 'दिंडी ट्रॅक करा' },
    'f5_desc': { en: 'Lookup your dindi ID, see leader info and member status.', mr: 'तुमचा दिंडी आयडी शोधा, प्रमुख माहिती आणि सदस्य स्थिती पहा.' },
    'f6_title': { en: 'Seva & Daan', mr: 'सेवा आणि दान' },
    'f6_desc': { en: 'Find free food, medical centers & offer seva to Warkaris.', mr: 'मोफत अन्नदान, वैद्यकीय केंद्र शोधा आणि वारकऱ्यांना सेवा द्या.' },
    'f7_title': { en: 'AI Emergency', mr: 'एआय आपत्कालीन' },
    'f7_desc': { en: 'Fast 1-tap protocols for heatstroke, dehydration & heavy rain.', mr: 'उष्माघात, निर्जलीकरण आणि मुसळधार पावसासाठी १-टॅप मार्गदर्शन.' },
    'f8_title': { en: 'Sacred Gallery', mr: 'पवित्र गॅलरी' },
    'f8_desc': { en: 'Devotional moments, dindi photos and certificate of completion.', mr: 'भक्ती क्षण, दिंडीची छायाचित्रे आणि पूर्तता प्रमाणपत्र.' },

    // Footer
    'footer_text': { en: 'Made with devotion for the Warkari sangha · Pandharpur Wari', mr: 'वारकरी संघासाठी भक्तीभावाने तयार केले · पंढरपूर वारी २०२६' },

    // Common
    'loading': { en: 'Loading...', mr: 'लोड होत आहे...' },
    'safe': { en: 'Safe', mr: 'सुरक्षित' },
    'caution': { en: 'Caution', mr: 'सावधान' },
    'danger': { en: 'Danger', mr: 'धोका' },
    'alandi_route': { en: 'Alandi Route', mr: 'आळंदी मार्ग' },
    'dehu_route': { en: 'Dehu Route', mr: 'देहू मार्ग' },
  },

  t(key) {
    const entry = this.translations[key];
    if (!entry) return key;
    return entry[this.lang] || entry['en'] || key;
  },

  toggleLang() {
    this.lang = this.lang === 'en' ? 'mr' : 'en';
    localStorage.setItem('hm_lang', this.lang);
    this.applyTranslations();
    this.showToast(this.lang === 'mr' ? 'भाषा बदलली: मराठी' : 'Language changed: English');
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: this.lang } }));
  },

  applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });
    
    // Update language toggle button text
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
      langBtn.textContent = this.lang === 'en' ? 'मराठी' : 'EN';
    }
  },

  // ---- Toast Notifications ----
  showToast(message, duration = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
  },

  // ---- Geolocation ----
  currentLocation: null,

  getLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.currentLocation = {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          };
          resolve(this.currentLocation);
        },
        (err) => {
          this.currentLocation = { lat: 18.5204, lng: 73.8567 };
          resolve(this.currentLocation);
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  },

  // ---- TTS Playback ----
  currentAudio: null,

  async speak(text, lang = 'mr') {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }

    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        this.currentAudio = new Audio(url);
        this.currentAudio.play();
      } else {
        this.browserSpeak(text, lang);
      }
    } catch (err) {
      this.browserSpeak(text, lang);
    }
  },

  browserSpeak(text, lang = 'mr') {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang === 'mr' ? 'mr-IN' : 'en-IN';
      utterance.rate = 0.9;
      speechSynthesis.speak(utterance);
    }
  },

  init() {
    this.applyTranslations();

    // Request location in background
    this.getLocation();
  }
};

document.addEventListener('DOMContentLoaded', () => HariMarg.init());
