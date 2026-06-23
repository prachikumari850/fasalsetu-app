import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';

class BoundaryMapWidget extends StatefulWidget {
  final List<LatLng> initialPoints;
  final void Function(List<LatLng> points) onBoundaryChanged;

  const BoundaryMapWidget({
    super.key,
    this.initialPoints = const [],
    required this.onBoundaryChanged,
  });

  @override
  State<BoundaryMapWidget> createState() => _BoundaryMapWidgetState();
}

class _BoundaryMapWidgetState extends State<BoundaryMapWidget> {
  final MapController _mapController = MapController();
  List<LatLng> _points = [];
  bool _isLocating = false;

  // Default center: Uttar Pradesh, India
  static const LatLng _defaultCenter = LatLng(26.8467, 80.9462);

  @override
  void initState() {
    super.initState();
    _points = List.from(widget.initialPoints);
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  Future<void> _locateMe() async {
    if (!mounted) return;
    setState(() => _isLocating = true);

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (mounted) {
          _showError('Location services are disabled.');
          setState(() => _isLocating = false);
        }
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          if (mounted) {
            _showError('Location permission denied.');
            setState(() => _isLocating = false);
          }
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        if (mounted) {
          _showError('Location permission permanently denied.');
          setState(() => _isLocating = false);
        }
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 15),
      );

      // CRITICAL: always check mounted after any async gap
      if (!mounted) return;

      final target = LatLng(position.latitude, position.longitude);
      _mapController.move(target, 16.0);

      setState(() => _isLocating = false);
    } catch (e) {
      // CRITICAL: check mounted in catch block too
      if (!mounted) return;
      _showError('Could not get location. Please tap the map manually.');
      setState(() => _isLocating = false);
    }
  }

  void _onTap(TapPosition _, LatLng point) {
    if (!mounted) return;
    setState(() {
      _points.add(point);
    });
    widget.onBoundaryChanged(_points);
  }

  void _undoLast() {
    if (!mounted || _points.isEmpty) return;
    setState(() => _points.removeLast());
    widget.onBoundaryChanged(_points);
  }

  void _clearAll() {
    if (!mounted) return;
    setState(() => _points.clear());
    widget.onBoundaryChanged(_points);
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppColors.error),
    );
  }

  @override
  Widget build(BuildContext context) {
    final bool hasBoundary = _points.length >= 3;

    return Column(
      children: [
        // Toolbar
        Row(
          children: [
            _ToolButton(
              icon: Icons.my_location,
              label: 'Locate',
              isLoading: _isLocating,
              onTap: _locateMe,
            ),
            const SizedBox(width: 8),
            _ToolButton(
              icon: Icons.undo,
              label: 'Undo',
              onTap: _points.isNotEmpty ? _undoLast : null,
            ),
            const SizedBox(width: 8),
            _ToolButton(
              icon: Icons.clear,
              label: 'Clear',
              onTap: _points.isNotEmpty ? _clearAll : null,
              color: AppColors.error,
            ),
            const Spacer(),
            if (hasBoundary)
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.success.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.success),
                ),
                child: Text(
                  '${_points.length} points',
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),

        // Map
        ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            height: 300,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: _defaultCenter,
                initialZoom: 13.0,
                onTap: _onTap,
              ),
              children: [
                TileLayer(
                  urlTemplate:
                      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.fasalsetu.app',
                ),
                if (_points.length >= 3)
                  PolygonLayer(
                    polygons: [
                      Polygon(
                        points: _points,
                        color: AppColors.primary.withValues(alpha: 0.25),
                        borderColor: AppColors.primary,
                        borderStrokeWidth: 2.5,
                      ),
                    ],
                  ),
                PolylineLayer(
                  polylines: [
                    if (_points.length >= 2)
                      Polyline(
                        points: _points,
                        color: AppColors.primary,
                        strokeWidth: 2.0,
                      ),
                  ],
                ),
                MarkerLayer(
                  markers: _points
                      .asMap()
                      .entries
                      .map(
                        (e) => Marker(
                          point: e.value,
                          width: 20,
                          height: 20,
                          child: Container(
                            decoration: BoxDecoration(
                              color: e.key == 0
                                  ? AppColors.success
                                  : AppColors.primary,
                              shape: BoxShape.circle,
                              border: Border.all(
                                  color: Colors.white, width: 2),
                            ),
                          ),
                        ),
                      )
                      .toList(),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 8),
        Text(
          hasBoundary
              ? 'Boundary ready. Tap to add more points.'
              : 'Tap the map to mark farm corners (min. 3 points)',
          style: TextStyle(
            fontSize: 12,
            color: hasBoundary
                ? AppColors.success
                : AppColors.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _ToolButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;
  final bool isLoading;
  final Color? color;

  const _ToolButton({
    required this.icon,
    required this.label,
    this.onTap,
    this.isLoading = false,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final effective = color ?? AppColors.primary;
    final enabled   = onTap != null && !isLoading;

    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 150),
        opacity: enabled ? 1.0 : 0.4,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: effective.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: effective.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isLoading)
                SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: effective,
                  ),
                )
              else
                Icon(icon, size: 14, color: effective),
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: effective,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}