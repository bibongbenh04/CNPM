window.onSpotifyWebPlaybackSDKReady = () => {
    const token = '[BQB-hjK_laWCNy_GLgNIPU5WHFvi1KuKFiwpu6HlfnxT5Uo6188KPCWYScBBtD8-_sHfhhUAiYas0hTPSA27XI85o098yxA8W6JRD2ji6a0KE5KpQwtym3wBMpGBtmNjDkYFFsf2FoPSZ5iYaYdeEd_C1kEBYRlNoLAqX9-TavGVuZTcwJ7M9wJWS1wAlDcsMr10ahC2Wbm8l3KNZIQvuCxhmtb4qbKp-PTxRQ]';
    const player = new Spotify.Player({
      name: 'Web Playback SDK Quick Start Player',
      getOAuthToken: cb => { cb(token); }
    });
  }

console.log("1")