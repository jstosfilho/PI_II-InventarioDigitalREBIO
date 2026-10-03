"use client";

import "maplibre-gl/dist/maplibre-gl.css";
import Map from "react-map-gl/maplibre";
import type { StyleSpecification } from "maplibre-gl";

const maptilerKey = process.env.NEXT_PUBLIC_MAPTILER_KEY;

export const osmStyle: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

export function resolveMapStyle(key?: string): StyleSpecification | string {
  return key
    ? `https://api.maptiler.com/maps/outdoor-v2/style.json?key=${key}`
    : osmStyle;
}

export default function MapView() {
  return (
    <Map
      initialViewState={{ longitude: -48.5, latitude: -27.6, zoom: 8 }}
      mapStyle={resolveMapStyle(maptilerKey)}
      style={{ width: "100%", height: "100%" }}
    />
  );
}
