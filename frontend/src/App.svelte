<script lang="ts">
  import { onMount } from 'svelte';

  let code: string = '';
  let title: string = '';
  let description: string = '';
  let imageData: string | null = null;
  let videoElement: HTMLVideoElement;
  let canvasElement: HTMLCanvasElement;
  let stream: MediaStream | null = null;
  let error: string = '';
  let loading: boolean = false;

  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    code = params.get('code') || '';

    if (!code) {
      error = "Il manque le code de la session dans l'URL";
    }
  });

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment',
          width: { ideal: 1000 },
          height: { ideal: 1000 }
        }
      });
      videoElement.srcObject = stream;
      error = '';
    } catch (err) {
      error = "Impossible d'accéder à l'appareil photo";
      console.error(err);
    }
  }

  function takePicture() {
    if (videoElement && canvasElement) {
      const width = videoElement.videoWidth;
      const height = videoElement.videoHeight;
      
      canvasElement.width = width;
      canvasElement.height = height;
      
      const context = canvasElement.getContext('2d');
      if (context) {
        context.drawImage(videoElement, 0, 0, width, height);
        imageData = canvasElement.toDataURL('image/jpeg');
      
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
          stream = null;
        }
      }
    }
  }

  async function handleSubmit() {
    if (!code) {
      error = 'Il manque le code';
      return;
    }
    if (!title) {
      error = 'Il manque le titre';
      return;
    }
    if (!description) {
      error = 'Il manque la description';
      return;
    }
    if (!imageData) {
      error = 'Il manque la photo';
      return;
    }

    loading = true;
    error = '';

    try {
      const response = await fetch('/wikipitch/actions/register_session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          code,
          title,
          description,
          imageData
        })
      });

      const data = await response.json();

      if (response.ok) {
        window.location.href = data.redirect_url;
      } else {
        error = data.error || 'Une erreur est survenue';
      }
    } catch (err) {
      error = 'Erreur de connexion';
      console.error(err);
    } finally {
      loading = false;
    }
  }
</script>

<main>
  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>

    <div class="field">
      <label for="title">Donne un titre à ta session</label>
      <input
        id="title"
        bind:value={title}
        required
        disabled={loading}
      />
    </div>

    <div class="field">
      <label for="description">Explique en quelques mots</label>
      <textarea
        id="description"
        bind:value={description}
        disabled={loading}
      ></textarea>
    </div>

    <div class="camera-section">
      <label for="description">Prends en photo ta page A4</label>
      {#if !imageData}
        <video
          bind:this={videoElement}
          autoplay
          playsinline
        >
          <track kind="captions" label="Captions" src="" default />
        </video>
        <canvas bind:this={canvasElement} style="display: none;" ></canvas>
        <button
          type="button"
          on:click={startCamera}
          disabled={loading || !!stream}
        >
          Activer l'appareil photo
        </button>
        {#if stream}
          <button
            type="button"
            on:click={takePicture}
            disabled={loading}
          >
            Prendre une photo
          </button>
        {/if}
      {:else}
        <img src={imageData} alt="Captured" />
        <button
          type="button"
          on:click={() => {
            imageData = null;
            startCamera();
          }}
          disabled={loading}
        >
          Si la photo n'est pas bonne, cliquez ici pour recommencer
        </button>
      {/if}
    </div>

    <div class="field">
      <label for="code">Code</label>
      <input
        id="code"
        bind:value={code}
        required
        disabled="disabled"
      />
    </div>

    <button
      type="submit"
      disabled={loading || !title || !description || !imageData}
    >
      {loading ? 'Envoi en cours...' : "C'est bon : on met à jour le wiki"}
    </button>
  </form>
</main>

<footer>
  Powered by <a href="https://github.com/Oaz/WikiPitch" target="_blank">WikiPitch</a>
</footer>

<style>
  main {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .error {
    color: red;
    margin-bottom: 20px;
  }

  .field {
    margin-bottom: 20px;
  }

  label {
    display: block;
    margin-bottom: 5px;
  }

  input, textarea {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
  }

  .camera-section {
    margin: 20px 0;
    text-align: center;
    width: 100%;
    height: auto;
  }

  video {
    width: 100%;
    object-fit: cover;
    margin-bottom: 10px;
  }

  img {
    width: 100%;
    object-fit: cover;
    margin-bottom: 10px;
  }

  button {
    padding: 10px 20px;
    margin: 5px;
  }

  button[type="submit"] {
    width: 100%;
    background: #4CAF50;
    color: white;
    border: none;
    padding: 15px;
    font-size: 16px;
    cursor: pointer;
  }

  button[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
  }

  footer {
    text-align: center;
    margin-top: 20px;
    padding: 10px;
    font-size: 14px;
    color: #666;
  }

  footer a {
    color: #4CAF50;
    text-decoration: none;
  }

  footer a:hover {
    text-decoration: underline;
  }
</style>