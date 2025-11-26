/**
 * Device Information Utility
 * Captures real-time device and browser information
 */

export const getDeviceInfo = () => {
  const userAgent = navigator.userAgent;
  const platform = navigator.platform;
  
  // Browser Detection
  const getBrowser = () => {
    if (userAgent.indexOf('Firefox') > -1) return 'Firefox';
    if (userAgent.indexOf('Chrome') > -1 && userAgent.indexOf('Edg') === -1) return 'Chrome';
    if (userAgent.indexOf('Safari') > -1 && userAgent.indexOf('Chrome') === -1) return 'Safari';
    if (userAgent.indexOf('Edg') > -1) return 'Edge';
    if (userAgent.indexOf('Opera') > -1 || userAgent.indexOf('OPR') > -1) return 'Opera';
    return 'Unknown';
  };

  // OS Detection
  const getOS = () => {
    if (userAgent.indexOf('Win') > -1) return 'Windows';
    if (userAgent.indexOf('Mac') > -1) return 'macOS';
    if (userAgent.indexOf('Linux') > -1) return 'Linux';
    if (userAgent.indexOf('Android') > -1) return 'Android';
    if (userAgent.indexOf('iOS') > -1 || userAgent.indexOf('iPhone') > -1 || userAgent.indexOf('iPad') > -1) return 'iOS';
    return 'Unknown';
  };

  // Device Type Detection
  const getDeviceType = () => {
    const width = window.innerWidth;
    if (width < 768) return 'Mobile';
    if (width < 1024) return 'Tablet';
    return 'Desktop';
  };

  // Screen Information
  const getScreenInfo = () => {
    return {
      width: window.screen.width,
      height: window.screen.height,
      availWidth: window.screen.availWidth,
      availHeight: window.screen.availHeight,
      colorDepth: window.screen.colorDepth,
      pixelDepth: window.screen.pixelDepth,
      orientation: window.screen.orientation ? window.screen.orientation.type : 'Unknown'
    };
  };

  // Viewport Information
  const getViewportInfo = () => {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio || 1
    };
  };

  // Network Information
  const getNetworkInfo = () => {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      return {
        effectiveType: connection.effectiveType || 'Unknown',
        downlink: connection.downlink || 'Unknown',
        rtt: connection.rtt || 'Unknown',
        saveData: connection.saveData || false,
        onchange: connection.onchange ? 'Supported' : 'Not Supported'
      };
    }
    return {
      effectiveType: 'Not Available',
      downlink: 'Not Available',
      rtt: 'Not Available',
      saveData: false,
      onchange: 'Not Supported'
    };
  };

  // Language and Timezone
  const getLocaleInfo = () => {
    return {
      language: navigator.language,
      languages: navigator.languages || [navigator.language],
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      timezoneOffset: new Date().getTimezoneOffset()
    };
  };

  // Connection Status
  const getConnectionStatus = () => {
    return navigator.onLine ? 'Online' : 'Offline';
  };

  // Battery Information (if available)
  const getBatteryInfo = async () => {
    if (navigator.getBattery) {
      try {
        const battery = await navigator.getBattery();
        return {
          level: Math.round(battery.level * 100) + '%',
          charging: battery.charging,
          chargingTime: battery.chargingTime === Infinity ? 'N/A' : battery.chargingTime + 's',
          dischargingTime: battery.dischargingTime === Infinity ? 'N/A' : battery.dischargingTime + 's'
        };
      } catch (e) {
        return { error: 'Not available' };
      }
    }
    return { error: 'Not supported' };
  };

  // Get MAC address (limited - browsers don't allow direct access)
  const getMACAddress = () => {
    // Note: Browsers cannot access MAC address directly for security reasons
    // We can generate a fingerprint based on device characteristics
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('MAC fingerprint', 2, 2);
    const canvasFingerprint = canvas.toDataURL();
    
    // Create a device fingerprint (not actual MAC, but unique identifier)
    const fingerprint = btoa(
      userAgent + 
      platform + 
      navigator.language + 
      window.screen.width + 
      window.screen.height + 
      new Date().getTimezoneOffset() +
      canvasFingerprint
    ).substring(0, 17).match(/.{1,2}/g).join(':');
    
    return {
      fingerprint: fingerprint,
      note: 'Browser-generated device fingerprint (MAC not accessible)',
      actualMAC: 'Not accessible (browser security restriction)'
    };
  };

  return {
    browser: getBrowser(),
    browserVersion: userAgent.match(/(?:Firefox|Chrome|Safari|Edg|Opera|OPR)\/(\d+)/)?.[1] || 'Unknown',
    os: getOS(),
    platform: platform,
    deviceType: getDeviceType(),
    userAgent: userAgent,
    screen: getScreenInfo(),
    viewport: getViewportInfo(),
    network: getNetworkInfo(),
    locale: getLocaleInfo(),
    connectionStatus: getConnectionStatus(),
    macAddress: getMACAddress(),
    timestamp: new Date().toISOString(),
    getBatteryInfo: getBatteryInfo
  };
};

// Fetch IP address from backend
export const getIPAddress = async () => {
  try {
    const response = await fetch('/api/device/device-info');
    const data = await response.json();
    return {
      ip: data.ip_address || 'Unknown',
      detectedAt: data.timestamp,
      source: 'Server-detected'
    };
  } catch (error) {
    return {
      ip: 'Unable to detect',
      detectedAt: new Date().toISOString(),
      source: 'Error fetching',
      error: error.message
    };
  }
};

// Note: For React hooks, import and use directly in components
// This utility file only provides the getDeviceInfo function

