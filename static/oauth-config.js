var OAuthConfig = (function() {
    'use strict';
  
    var clientId = '9556eb2bb1524439ba0171dd57c869f5';
    var redirectUri;
    if (location.host === 'localhost:8000') {
      redirectUri = 'http://localhost:8000/callback';
    } else {
      redirectUri = '//';
    }
    var host = /http[s]?:\/\/[^/]+/.exec(redirectUri)[0];
    return {
      clientId: clientId,
      redirectUri: redirectUri,
      host: host
    };
  })();