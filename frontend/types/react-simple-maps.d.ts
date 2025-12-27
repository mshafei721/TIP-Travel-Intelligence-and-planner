declare module 'react-simple-maps' {
  import { ComponentType, ReactNode } from 'react';

  export interface ComposableMapProps {
    projection?: string;
    projectionConfig?: {
      rotate?: [number, number, number];
      scale?: number;
      center?: [number, number];
    };
    width?: number;
    height?: number;
    style?: React.CSSProperties;
    className?: string;
    children?: ReactNode;
  }

  export interface GeographiesProps {
    geography: string | object;
    children: (data: { geographies: Geography[] }) => ReactNode;
  }

  export interface Geography {
    rsmKey: string;
    id?: string;
    properties: {
      name: string;
      NAME?: string;
      ISO_A2?: string;
      ISO_A3?: string;
      [key: string]: unknown;
    };
    geometry: object;
  }

  export interface GeographyProps {
    geography: Geography;
    style?: {
      default?: React.CSSProperties;
      hover?: React.CSSProperties;
      pressed?: React.CSSProperties;
    };
    onMouseEnter?: (event: React.MouseEvent) => void;
    onMouseLeave?: (event: React.MouseEvent) => void;
    onClick?: (event: React.MouseEvent) => void;
    className?: string;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
  }

  export interface ZoomableGroupProps {
    center?: [number, number];
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    translateExtent?: [[number, number], [number, number]];
    onMoveStart?: (event: { coordinates: [number, number]; zoom: number }) => void;
    onMove?: (event: { coordinates: [number, number]; zoom: number }) => void;
    onMoveEnd?: (event: { coordinates: [number, number]; zoom: number }) => void;
    children?: ReactNode;
  }

  export interface SphereProps {
    id?: string;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
  }

  export interface GraticuleProps {
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    step?: [number, number];
  }

  export const ComposableMap: ComponentType<ComposableMapProps>;
  export const Geographies: ComponentType<GeographiesProps>;
  export const Geography: ComponentType<GeographyProps>;
  export const ZoomableGroup: ComponentType<ZoomableGroupProps>;
  export const Sphere: ComponentType<SphereProps>;
  export const Graticule: ComponentType<GraticuleProps>;
}
