import { useCallback, useState } from "react";

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse";

export function useReverseGeocode() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const geocode = useCallback(async (lat, lng) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        lat,
        lon: lng,
        format: "json",
        addressdetails: 1,
      });

      const res = await fetch(`${NOMINATIM_URL}?${params}`, {
        headers: {
          "Accept-Language": "es",
        },
      });

      if (!res.ok) {
        throw new Error(`Error HTTP: ${res.status}`);
      }

      const data = await res.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const obj = {
        displayName: data.display_name,
        address: data.address,
        lat: parseFloat(data.lat),
        lng: parseFloat(data.lon),
      };
      setResult(obj);
      return obj;
    } catch (err) {
      setError(err.message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  return { geocode, result, loading, error };
}
