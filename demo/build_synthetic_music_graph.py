"""A clean-room teaching illustration; no audio or research data are read.

Python standard library only. This is generic cosine/top-k wiring, not Leiden,
Ward, an audio representation, or a reproduced research experiment.
"""
from pathlib import Path
import argparse
import json
import math


def make_dataset():
    nodes = []
    for index in range(18):
        surface_group = index // 6
        pattern_group = index % 3
        def view(group, phase):
            # Nonnegative toy features. Groups are assigned, never discovered.
            return [round((1.0 if axis == group else 0.12) +
                          0.035 * (1 + math.sin((index + 1) * (axis + 2) + phase)), 8)
                    for axis in range(3)]
        angle = -math.pi / 2 + index * 2 * math.pi / 18
        nodes.append({
            'id': f'S{index + 1:02d}',
            'surface_group': surface_group,
            'pattern_group': pattern_group,
            'surface': view(surface_group, 0.0),
            'pattern': view(pattern_group, 1.7),
            'x': round(360 + 206 * math.cos(angle), 4),
            'y': round(250 + 206 * math.sin(angle), 4),
        })
    return {
        'title': 'Synthetic neighborhoods — illustrative only',
        'synthetic': True,
        'data_origin': 'Deterministic arithmetic authored for this portfolio; no audio, people or research data.',
        'method': 'Weighted cosine of two toy views; undirected union of top-k neighbors above a threshold.',
        'layout': 'Fixed circle, unrelated to feature distances.',
        'does_not_run': ['Leiden', 'Ward', 'audio embedding', 'historical genealogy inference'],
        'default': {'surface_weight': 0.65, 'k': 2, 'threshold': 0.55},
        'nodes': nodes,
    }


def cosine(a, b):
    numerator = sum(x * y for x, y in zip(a, b))
    denominator = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    if denominator == 0:
        raise ValueError('Zero-length vector is undefined in this illustration.')
    return max(-1.0, min(1.0, numerator / denominator))


def score(a, b, surface_weight):
    return surface_weight * cosine(a['surface'], b['surface']) + (1 - surface_weight) * cosine(a['pattern'], b['pattern'])


def build_edges(nodes, surface_weight=0.65, k=2, threshold=0.55):
    if not 0 <= surface_weight <= 1 or not 1 <= k < len(nodes) or not 0 <= threshold <= 1:
        raise ValueError('Controls outside their valid range.')
    edges = {}
    for a in nodes:
        ranked = sorted(((score(a, b, surface_weight), b['id']) for b in nodes if b['id'] != a['id']),
                        key=lambda pair: (-pair[0], pair[1]))
        for similarity, target in ranked[:k]:
            if similarity >= threshold:
                pair = tuple(sorted((a['id'], target)))
                edges[pair] = similarity
    return [{'source': pair[0], 'target': pair[1], 'similarity': round(similarity, 10)}
            for pair, similarity in sorted(edges.items())]


def svg_preview(data):
    nodes = data['nodes']
    byid = {node['id']: node for node in nodes}
    defaults = data['default']
    edges = build_edges(nodes, defaults['surface_weight'], defaults['k'], defaults['threshold'])
    colors = ['#80619c', '#387f81', '#95652e']
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620" role="img" aria-labelledby="t d">',
        '<title id="t">Synthetic neighborhoods, not a research result</title>',
        '<desc id="d">Eighteen invented nodes, two hand-constructed feature views, generic weighted cosine and top-k wiring. Fixed circle layout. Colors show assigned toy surface groups, not communities. No real music is represented. Leiden and Ward are not run.</desc>',
        '<rect width="900" height="620" fill="#fafbf8"/>',
        '<text x="36" y="40" font-family="Arial,sans-serif" font-size="14" letter-spacing="2" fill="#80619c">SYNTHETIC / ILLUSTRATIVE ONLY</text>',
        '<text x="36" y="78" font-family="Arial,sans-serif" font-size="26" fill="#142435">A different representation changes the neighborhood.</text>',
        '<g transform="translate(85,55)">',
    ]
    for edge in edges:
        a, b = byid[edge['source']], byid[edge['target']]
        parts.append(f'<line x1="{a["x"]}" y1="{a["y"]}" x2="{b["x"]}" y2="{b["y"]}" stroke="#c8c4d1" stroke-width="1.6"/>')
    for node in nodes:
        parts.append(f'<circle cx="{node["x"]}" cy="{node["y"]}" r="17" fill="{colors[node["surface_group"]]}"/>')
        parts.append(f'<text x="{node["x"]}" y="{node["y"] + 4}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="700" fill="#fff">{node["id"]}</text>')
    parts.extend([
        '</g>',
        '<text x="36" y="562" font-family="Arial,sans-serif" font-size="14" fill="#142435">Fixed illustrative layout · assigned colors · no community detection · no historical edges</text>',
        '<text x="36" y="589" font-family="Arial,sans-serif" font-size="13" fill="#596671">Toy views only. No audio, track metadata, study results or participant data.</text>',
        '</svg>',
    ])
    return '\n'.join(parts) + '\n'


def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    data = make_dataset()
    serialized = json.dumps(data, indent=2, ensure_ascii=True) + '\n'
    (output / 'synthetic_graph.json').write_text(serialized, encoding='utf-8', newline='\n')
    (output / 'synthetic-data.js').write_text('window.SYNTHETIC_MUSIC = ' + serialized.rstrip() + ';\n', encoding='utf-8', newline='\n')
    (output / 'synthetic-neighborhoods.svg').write_text(svg_preview(data), encoding='utf-8', newline='\n')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Destination for newly generated teaching artifacts.')
    arguments = parser.parse_args()
    data = generate(arguments.out)
    print(f'Synthetic illustration generated: {len(data["nodes"])} invented nodes. No study reproduced.')
