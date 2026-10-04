import unittest
from inventario.geography import parse_file, length_m, validate_geometry, MAX_FILE_SIZE


class GeographyTest(unittest.TestCase):
    def test_gpx_multiple_segments_are_not_joined(self):
        data=b'<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg><trkpt lon="0" lat="0"/><trkpt lon="0.01" lat="0"/></trkseg><trkseg><trkpt lon="10" lat="0"/><trkpt lon="10.01" lat="0"/></trkseg></trk></gpx>'
        geometry=parse_file(data,'trilha.gpx','trilha')
        self.assertEqual(geometry['type'],'MultiLineString')
        self.assertAlmostEqual(length_m(geometry),2223.9,delta=1)

    def test_gpx_route(self):
        geometry=parse_file(b'<gpx><rte><rtept lon="-46" lat="-23"/><rtept lon="-46.1" lat="-23.1"/></rte></gpx>','rota.GPX','trilha')
        self.assertEqual(geometry['coordinates'][0],[-46,-23])

    def test_gpx_waypoint(self):
        geometry=parse_file(b'<gpx><wpt lon="-46" lat="-23"/></gpx>','ponto.gpx','nascente')
        self.assertEqual(geometry,{'type':'Point','coordinates':[-46,-23]})
        self.assertIsNone(length_m(geometry))

    def test_kml_line_altitude_and_namespace(self):
        geometry=parse_file(b'<kml xmlns="http://www.opengis.net/kml/2.2"><Placemark><LineString><coordinates>-46,-23,10 -46.01,-23.01,20</coordinates></LineString></Placemark></kml>','trilha.kml','trilha')
        self.assertEqual(geometry['coordinates'],[[-46,-23],[-46.01,-23.01]])

    def test_kml_single_point(self):
        self.assertEqual(parse_file(b'<kml><Placemark><Point><coordinates>1,2,3</coordinates></Point></Placemark></kml>','ponto.kml','nascente')['coordinates'],[1,2])

    def test_multiple_springs_rejected(self):
        with self.assertRaises(ValueError):
            parse_file(b'<gpx><wpt lon="1" lat="2"/><wpt lon="3" lat="4"/></gpx>','pontos.gpx','nascente')

    def test_dtd_and_entities_rejected(self):
        with self.assertRaises(ValueError):
            parse_file(b'<!DOCTYPE gpx [<!ENTITY x SYSTEM "file:///etc/passwd">]><gpx>&x;</gpx>','ponto.gpx','nascente')

    def test_invalid_inputs_rejected(self):
        for content,name in [(b'','a.gpx'),(b'<gpx>','a.gpx'),(b'<kml/>','a.gpx'),(b'<gpx/>','a.zip'),(b'<kml><Point><coordinates>181,0</coordinates></Point></kml>','a.kml'),(b'<gpx><wpt lat="0"/></gpx>','a.gpx')]:
            with self.subTest(name=name,content=content),self.assertRaises(ValueError):
                parse_file(content,name,'nascente')

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            parse_file(b'x'*(MAX_FILE_SIZE+1),'a.gpx','trilha')

    def test_degenerate_multiline_rejected(self):
        with self.assertRaises(ValueError):
            validate_geometry({'type':'MultiLineString','coordinates':[[[0,0],[1,1]],[[2,2],[2,2]]]},'trilha')
