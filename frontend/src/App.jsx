import { useState } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [image, setImage] = useState(null);
  const [previews, setPreviews] = useState([]);
  const [links, setLinks] = useState({});

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
      setImage(URL.createObjectURL(file));
      const formData = new FormData();
      formData.append('image', file);

      try {
        const response = await fetch(`${API_URL}/process-image`, {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        setPreviews([
          { url: result.social_media, title: 'Sociální sítě (1:1, 1080x1080)' },
          { url: result.carousel, title: 'Carousel (16:9, 1920x1080)' },
          { url: result.banner, title: 'Banner (300x250)' },
        ]);
        setLinks(result);
      } catch (error) {
        console.error('Chyba při zpracování obrázku:', error);
        alert('Došlo k chybě při zpracování obrázku.');
      }
    } else {
      alert('Prosím nahrajte obrázek ve formátu JPEG nebo PNG.');
    }
  };

  const downloadImage = (url, title) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.png`;
    link.click();
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Úprava obrázků</h1>
      <input
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleImageUpload}
        className="mb-4"
      />
      {image && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Nahráný obrázek:</h2>
          <img src={image} alt="Nahráný obrázek" className="max-w-xs" />
        </div>
      )}
      {previews.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Náhledy:</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {previews.map((preview, index) => (
              <div key={index} className="border p-2">
                <h3 className="text-lg">{preview.title}</h3>
                <img src={preview.url} alt={preview.title} className="max-w-full" />
                <button
                  onClick={() => downloadImage(preview.url, preview.title)}
                  className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Stáhnout
                </button>
              </div>
            ))}
          </div>
          <h2 className="text-xl font-semibold mt-4">Odkazy:</h2>
          <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
            {JSON.stringify(links, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
