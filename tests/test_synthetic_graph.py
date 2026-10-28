"""Offline semantic checks for the new synthetic teaching illustration only."""
from pathlib import Path
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / 'demo/build_synthetic_music_graph.py'
spec = importlib.util.spec_from_file_location('synthetic_demo', GENERATOR)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class DocumentLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])


class SyntheticGraphTests(unittest.TestCase):
    def setUp(self):
        self.data = demo.make_dataset()
        self.nodes = self.data['nodes']

    def test_provenance_and_neutral_identity(self):
        self.assertIs(self.data['synthetic'], True)
        self.assertEqual([n['id'] for n in self.nodes], [f'S{i:02d}' for i in range(1, 19)])
        self.assertIn('Leiden', self.data['does_not_run'])
        self.assertIn('Ward', self.data['does_not_run'])
        for node in self.nodes:
            self.assertEqual(set(node), {'id', 'surface_group', 'pattern_group', 'surface', 'pattern', 'x', 'y'})
            for name in ('surface', 'pattern'):
                self.assertEqual(len(node[name]), 3)
                self.assertTrue(all(math.isfinite(x) and x > 0 for x in node[name]))

    def test_cosine_identity_and_symmetry(self):
        for node in self.nodes:
            self.assertAlmostEqual(demo.cosine(node['surface'], node['surface']), 1)
        a, b = self.nodes[0], self.nodes[-1]
        self.assertAlmostEqual(demo.score(a, b, .3), demo.score(b, a, .3))

    def test_weight_endpoints_and_interpolation(self):
        a, b = self.nodes[0], self.nodes[4]
        surface = demo.cosine(a['surface'], b['surface'])
        pattern = demo.cosine(a['pattern'], b['pattern'])
        self.assertAlmostEqual(demo.score(a, b, 1), surface)
        self.assertAlmostEqual(demo.score(a, b, 0), pattern)
        self.assertAlmostEqual(demo.score(a, b, .25), .25 * surface + .75 * pattern)

    def test_graph_validity(self):
        edges = demo.build_edges(self.nodes)
        pairs = [(e['source'], e['target']) for e in edges]
        ids = {node['id'] for node in self.nodes}
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertTrue(all(a < b and a in ids and b in ids for a, b in pairs))
        self.assertTrue(all(.55 <= e['similarity'] <= 1 for e in edges))

    def test_threshold_is_a_filter(self):
        def pairs(t):
            return {(e['source'], e['target']) for e in demo.build_edges(self.nodes, .65, 3, t)}
        self.assertLessEqual(pairs(.9), pairs(.5))
        self.assertEqual(demo.build_edges(self.nodes, .65, 2, 1), [])

    def test_k_preserves_existing_edges(self):
        def pairs(k):
            return {(e['source'], e['target']) for e in demo.build_edges(self.nodes, .65, k, .2)}
        self.assertLessEqual(pairs(1), pairs(3))

    def test_views_change_the_assigned_neighborhood(self):
        source = self.nodes[0]
        def top(weight):
            return max((n for n in self.nodes if n['id'] != source['id']), key=lambda n: demo.score(source, n, weight))
        self.assertEqual(top(1)['surface_group'], source['surface_group'])
        self.assertEqual(top(0)['pattern_group'], source['pattern_group'])
        self.assertNotEqual(demo.build_edges(self.nodes, 1, 2, .5), demo.build_edges(self.nodes, 0, 2, .5))

    def test_invalid_controls_rejected(self):
        for weight, k, threshold in [(-.1, 2, .5), (1.1, 2, .5), (.5, 0, .5), (.5, 18, .5), (.5, 2, 1.1)]:
            with self.assertRaises(ValueError):
                demo.build_edges(self.nodes, weight, k, threshold)

    def test_fixed_layout_is_in_bounds(self):
        for node in self.nodes:
            self.assertTrue(20 < node['x'] < 700 and 20 < node['y'] < 490)

    def test_bundled_json_and_js_agree(self):
        expected = self.data
        actual = json.loads((ROOT / 'demo/synthetic_graph.json').read_text(encoding='utf-8'))
        self.assertEqual(actual, expected)
        wrapper = (ROOT / 'site/synthetic-data.js').read_text(encoding='utf-8')
        self.assertTrue(wrapper.startswith('window.SYNTHETIC_MUSIC = '))
        self.assertEqual(json.loads(wrapper.split(' = ', 1)[1].rstrip().removesuffix(';')), expected)

    def test_generator_reproducible_without_external_packages(self):
        # Temp files stay inside this repository and are removed on context exit.
        with tempfile.TemporaryDirectory(prefix='synthetic_test_', dir=ROOT / 'tests') as directory:
            temporary = Path(directory).resolve()
            self.assertTrue(temporary.is_relative_to((ROOT / 'tests').resolve()))
            a, b = temporary / 'a', temporary / 'b'
            for output in (a, b):
                subprocess.run([sys.executable, '-B', str(GENERATOR), '--out', str(output)], check=True, capture_output=True)
            self.assertEqual({p.name: p.read_bytes() for p in a.iterdir()}, {p.name: p.read_bytes() for p in b.iterdir()})
            self.assertEqual((a / 'synthetic-neighborhoods.svg').read_bytes(), (ROOT / 'figures/synthetic-neighborhoods.svg').read_bytes())

    def test_local_links_and_no_remote_assets(self):
        document = ROOT / 'site/offline.html'
        parsed = DocumentLinks()
        parsed.feed(document.read_text(encoding='utf-8'))
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        for link in parsed.links:
            parts = urlsplit(link)
            self.assertFalse(parts.scheme or parts.netloc, f'Remote link/asset: {link}')
            if parts.path:
                target = (document.parent / unquote(parts.path)).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()), f'Link escapes repository: {link}')
                self.assertTrue(target.is_file(), f'Missing target: {link}')
            elif parts.fragment:
                self.assertIn(parts.fragment, parsed.ids)
        for path in ROOT.rglob('*.md'):
            for link in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
                parts = urlsplit(link)
                if not parts.scheme and parts.path:
                    self.assertTrue((path.parent / parts.path).is_file(), f'Missing Markdown target: {path.name} -> {link}')

    def test_no_browser_network_or_persistence_calls(self):
        script = (ROOT / 'site/explorer.js').read_text(encoding='utf-8')
        self.assertIsNone(re.search(r'\b(fetch|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage)\b', script))
        self.assertNotIn('innerHTML', script)


if __name__ == '__main__':
    unittest.main(verbosity=2)
