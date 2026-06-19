from __future__ import annotations
from dataclasses import asdict
import numpy as np


def geometry_report(cfg) -> dict:
    gap = float(cfg.dot_spacing_mm - cfg.dot_diameter_mm)
    cell_width = float(cfg.dot_spacing_mm)
    cell_height = float(cfg.dot_spacing_mm * 3.0)
    issues = []
    if cfg.dot_diameter_mm <= 0:
        issues.append('dot_diameter_mm must be positive')
    if cfg.dot_spacing_mm <= 0:
        issues.append('dot_spacing_mm must be positive')
    if gap < cfg.safety_gap_mm:
        issues.append('dot edge gap below safety_gap_mm')
    if cfg.geometry.dot_height_mm <= 0:
        issues.append('dot_height_mm must be positive')
    return {
        'geometry': asdict(cfg.geometry),
        'material': asdict(cfg.material),
        'printer': asdict(cfg.printer),
        'edge_gap_mm': gap,
        'cell_width_mm': cell_width,
        'cell_height_mm': cell_height,
        'compliant': len(issues) == 0,
        'issues': issues,
    }


def binary_to_dot_positions_mm(binary, cfg):
    b = np.asarray(binary, dtype=bool)
    ys, xs = np.where(b)
    spacing = float(cfg.dot_spacing_mm)
    positions = []
    for y, x in zip(ys.tolist(), xs.tolist()):
        positions.append({'x_mm': float((x + 0.5) * spacing), 'y_mm': float((y + 0.5) * spacing)})
    return positions


def _neighbor_contact_count(binary, required_gap_mm, cfg) -> dict:
    b = np.asarray(binary, dtype=bool)
    dot_diameter = float(cfg.dot_diameter_mm)
    spacing = float(cfg.dot_spacing_mm)
    offsets = [(0, 1), (1, 0), (1, 1), (1, -1)]
    by_offset = {}
    total = 0
    worst_edge_gap = float('inf')
    for dy, dx in offsets:
        y0a = max(0, dy)
        y1a = b.shape[0] + min(0, dy)
        x0a = max(0, dx)
        x1a = b.shape[1] + min(0, dx)
        a = b[y0a:y1a, x0a:x1a]
        c = b[y0a - dy:y1a - dy, x0a - dx:x1a - dx]
        count = int(np.count_nonzero(a & c))
        center_distance = float(np.hypot(dy * spacing, dx * spacing))
        edge_gap = center_distance - dot_diameter
        if count:
            worst_edge_gap = min(worst_edge_gap, edge_gap)
        if edge_gap < required_gap_mm:
            by_offset[f'{dy},{dx}'] = {'pairs': count, 'edge_gap_mm': edge_gap, 'violating_pairs': count}
            total += count
        else:
            by_offset[f'{dy},{dx}'] = {'pairs': count, 'edge_gap_mm': edge_gap, 'violating_pairs': 0}
    if worst_edge_gap == float('inf'):
        worst_edge_gap = None
    return {'violating_pairs': int(total), 'by_offset': by_offset, 'worst_active_edge_gap_mm': worst_edge_gap}


def validate_tactile_output(binary, cfg) -> dict:
    b = np.asarray(binary, dtype=bool)
    min_diameter = float(getattr(cfg.geometry, 'min_dot_diameter_mm', 0.80))
    min_spacing = float(getattr(cfg.geometry, 'min_dot_spacing_mm', 2.00))
    issues = []
    warnings = []
    if cfg.dot_diameter_mm < min_diameter:
        issues.append({'severity': 'error', 'code': 'dot_diameter_too_small', 'message': f'dot diameter {cfg.dot_diameter_mm:.3f} mm < {min_diameter:.3f} mm'})
    if cfg.dot_spacing_mm < min_spacing:
        issues.append({'severity': 'error', 'code': 'dot_spacing_too_small', 'message': f'dot spacing {cfg.dot_spacing_mm:.3f} mm < {min_spacing:.3f} mm'})
    edge_gap = float(cfg.dot_spacing_mm - cfg.dot_diameter_mm)
    if edge_gap < cfg.safety_gap_mm:
        issues.append({'severity': 'error', 'code': 'edge_gap_below_safety_gap', 'message': f'edge gap {edge_gap:.3f} mm < {cfg.safety_gap_mm:.3f} mm'})
    contacts = _neighbor_contact_count(b, float(cfg.safety_gap_mm), cfg)
    if contacts['violating_pairs']:
        issues.append({'severity': 'error', 'code': 'active_dot_collision', 'message': f'{contacts["violating_pairs"]} active neighbor pairs violate the safety gap'})
    occupancy = float(b.mean()) if b.size else 0.0
    if occupancy > float(getattr(cfg, 'max_local_occupancy', 0.72)):
        warnings.append({'severity': 'warning', 'code': 'global_occupancy_high', 'message': f'global occupancy {occupancy:.3f} exceeds configured local occupancy limit'})
    return {
        'compliant': len(issues) == 0,
        'severity': 'error' if issues else ('warning' if warnings else 'ok'),
        'issues': issues,
        'warnings': warnings,
        'occupancy_ratio': occupancy,
        'dot_count': int(np.count_nonzero(b)),
        'active_collision_report': contacts,
        'geometry': geometry_report(cfg),
    }
