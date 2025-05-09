import * as L from "leaflet";
import "leaflet-control-geocoder"; // Import leaflet-control-geocoder

// Extend the geocoder control to support the 'on' method (event handling)
declare module "leaflet" {
  namespace Control {
    // Define geocoder control as Evented (adds event handling capability)
    export function geocoder(options?: any): L.Control & L.Evented;
  }
}
