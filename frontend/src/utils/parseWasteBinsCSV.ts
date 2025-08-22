export interface BinLocation {
  name: string;
  lat: number;
  lng: number;
}

export function parseWasteBinsCSV(csv: string): BinLocation[] {
  const lines = csv.split('\n');
  const header = lines[0].split(',');
  const nameIdx = header.indexOf('Landfill Name');
  const locIdx = header.indexOf('Landfill Location (Lat, Long)');
  const bins: BinLocation[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',');
    if (values.length > locIdx) {
      const name = values[nameIdx];
      const loc = values[locIdx].replace(/"/g, '').split(',');
      const lat = parseFloat(loc[0]);
      const lng = parseFloat(loc[1]);
      if (!isNaN(lat) && !isNaN(lng) && typeof name === 'string') {
        bins.push({ name, lat, lng });
      }
    }
  }
  return bins as BinLocation[];
}
