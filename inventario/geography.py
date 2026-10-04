"""Geometrias WGS84 e importação de um recurso por arquivo."""
import math
from pathlib import Path
from defusedxml import ElementTree as ET

MAX_FILE_SIZE = 15 * 1024 * 1024


def validate_geometry(geometry, kind):
    if not isinstance(geometry, dict):
        raise ValueError('Informe uma geometria válida.')
    geo_type = geometry.get('type')
    coords = geometry.get('coordinates')
    if kind == 'nascente':
        if geo_type != 'Point':
            raise ValueError('Uma nascente deve conter um único ponto.')
        segments = [[coords]]
    elif geo_type == 'LineString':
        segments = [coords]
    elif geo_type == 'MultiLineString' and isinstance(coords, list) and coords:
        segments = coords
    else:
        raise ValueError('Uma trilha deve conter LineString ou MultiLineString.')
    total = 0
    for points in segments:
        minimum = 1 if kind == 'nascente' else 2
        if not isinstance(points, list) or len(points) < minimum:
            raise ValueError('Cada segmento de trilha precisa de dois pontos distintos.')
        total += len(points)
        for point in points:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError('Cada coordenada deve conter longitude e latitude.')
            if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in point):
                raise ValueError('Coordenadas devem ser números finitos.')
            if not -180 <= point[0] <= 180 or not -90 <= point[1] <= 90:
                raise ValueError('Longitude ou latitude fora dos limites.')
        if kind == 'trilha' and len({tuple(p) for p in points}) < 2:
            raise ValueError('Cada segmento precisa de dois pontos distintos.')
    if total > 100000:
        raise ValueError('Limite de 100.000 pontos por registro.')
    return {'type': geo_type, 'coordinates': coords}


def length_m(geometry):
    if geometry['type'] == 'Point':
        return None
    segments = [geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']
    total = 0.0
    for points in segments:
        for first, second in zip(points, points[1:]):
            lon1, lat1, lon2, lat2 = map(math.radians, first + second)
            value = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
            total += 6371008.8 * 2 * math.asin(math.sqrt(min(1.0, value)))
    return round(total, 1)


def parse_file(content, filename, kind):
    if kind not in ('trilha', 'nascente'):
        raise ValueError('Selecione Trilha ou Nascente antes de importar.')
    suffix = Path(filename).suffix.lower()
    if suffix not in ('.gpx', '.kml'):
        raise ValueError('Selecione um arquivo .gpx ou .kml.')
    if not content or len(content) > MAX_FILE_SIZE:
        raise ValueError('O arquivo deve ter conteúdo e no máximo 15 MB.')
    try:
        root = ET.fromstring(content, forbid_dtd=True, forbid_entities=True, forbid_external=True)
        local = lambda tag: tag.rsplit('}', 1)[-1]
        lines, points = [], []
        if suffix == '.gpx':
            if local(root.tag) != 'gpx':
                raise ValueError('Conteúdo não corresponde a um arquivo GPX.')
            for node in root.iter():
                if local(node.tag) in ('trkseg', 'rte'):
                    segment = [[float(p.attrib['lon']), float(p.attrib['lat'])] for p in node if local(p.tag) in ('trkpt', 'rtept')]
                    if segment:
                        lines.append(segment)
                elif local(node.tag) == 'wpt':
                    points.append([float(node.attrib['lon']), float(node.attrib['lat'])])
        else:
            if local(root.tag) != 'kml':
                raise ValueError('Conteúdo não corresponde a um arquivo KML.')
            for node in root.iter():
                if local(node.tag) in ('Point', 'LineString'):
                    coordinate_nodes = [child for child in node if local(child.tag) == 'coordinates']
                    if len(coordinate_nodes) != 1 or not coordinate_nodes[0].text:
                        raise ValueError('Geometria KML sem coordenadas.')
                    values = []
                    for token in coordinate_nodes[0].text.split():
                        parts = token.split(',')
                        if len(parts) not in (2,3):
                            raise ValueError('Coordenadas KML inválidas.')
                        values.append([float(parts[0]), float(parts[1])])
                    if local(node.tag) == 'Point':
                        if len(values) != 1:
                            raise ValueError('Um ponto KML deve conter uma coordenada.')
                        points.extend(values)
                    else:
                        lines.append(values)
        if kind == 'nascente':
            if len(points) != 1 or lines:
                raise ValueError('Para nascente, importe um arquivo com um único ponto, sem trilhas.')
            geometry = {'type':'Point', 'coordinates':points[0]}
        else:
            if not lines:
                raise ValueError('Nenhum percurso encontrado. Use track/route GPX ou LineString KML.')
            geometry = {'type':'LineString' if len(lines)==1 else 'MultiLineString', 'coordinates':lines[0] if len(lines)==1 else lines}
        return validate_geometry(geometry, kind)
    except ValueError:
        raise
    except Exception as error:
        raise ValueError('Arquivo XML inválido, inseguro ou com coordenadas ausentes.') from error
