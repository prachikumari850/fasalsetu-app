import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:fasalsetu/core/constants/app_colors.dart';
import 'package:fasalsetu/core/constants/app_constants.dart';

class BoundaryMapWidget extends StatefulWidget {
  final List<LatLng> points;
  final void Function(List<LatLng> points, LatLng center) onPointsChanged;

  const BoundaryMapWidget({
    super.key,
    required this.points,
    required this.onPointsChanged,
  });

  @override
  State<BoundaryMapWidget> createState() => _BoundaryMapWidgetState();
}

class _BoundaryMapWidgetState extends State<BoundaryMapWidget> {
  final MapController _mapController = MapController();
  LatLng _center = LatLng(
    AppConstants.indiaLat,
    AppConstants.indiaLng,
  );
  bool _locating = false;

  @override
  void initState() {
    super.initState();
    _getUserLocation();
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  Future<void> _getUserLocation() async {
    setState(() => _locating = true);
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) return;

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) return;
      }
      if (permission == LocationPermission.deniedForever) return;

      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      final userLocation = LatLng(position.latitude, position.longitude);
      setState(() => _center = userLocation);
      _mapController.move(userLocation, AppConstants.defaultMapZoom);
    } finally {
      if (mounted) setState(() => _locating = false);
    }
  }

  void _addPoint(LatLng point) {
    final newPoints = [...widget.points, point];
    final center = LatLng(
      newPoints.map((p) => p.latitude).reduce((a, b) => a + b) /
          newPoints.length,
      newPoints.map((p) => p.longitude).reduce((a, b) => a + b) /
          newPoints.length,
    );
    widget.onPointsChanged(newPoints, center);
  }

  void _removeLastPoint() {
    if (widget.points.isEmpty) return;
    final newPoints = widget.points.sublist(0, widget.points.length - 1);
    final center = newPoints.isEmpty
        ? _center
        : LatLng(
            newPoints.map((p) => p.latitude).reduce((a, b) => a + b) /
                newPoints.length,
            newPoints.map((p) => p.longitude).reduce((a, b) => a + b) /
                newPoints.length,
          );
    widget.onPointsChanged(newPoints, center);
  }

  void _clearPoints() {
    widget.onPointsChanged([], _center);
  }

  List<LatLng> get _polygonPoints {
    if (widget.points.length < 3) return [];
    return [...widget.points, widget.points.first];
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Map
        ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: SizedBox(
            height: 320,
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: _center,
                    initialZoom: AppConstants.defaultMapZoom,
                    onTap: (_, point) => _addPoint(point),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.fasalsetu.fasalsetu',
                    ),

                    // Polygon fill
                    if (_polygonPoints.length >= 3)
                      PolygonLayer(
                        polygons: [
                          Polygon(
                            points: _polygonPoints,
                            color: AppColors.primary.withOpacity(0.2),
                            borderColor: AppColors.primary,
                            borderStrokeWidth: 2.5,
                          ),
                        ],
                      ),

                    // Boundary markers
                    MarkerLayer(
                      markers: widget.points.asMap().entries.map((entry) {
                        final index = entry.key;
                        final point = entry.value;
                        return Marker(
                          point: point,
                          width: 28,
                          height: 28,
                          child: Container(
                            decoration: BoxDecoration(
                              color: index == 0
                                  ? AppColors.secondary
                                  : AppColors.primary,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: Colors.white,
                                width: 2,
                              ),
                            ),
                            child: Center(
                              child: Text(
                                '${index + 1}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),

                // Loading indicator
                if (_locating)
                  const Positioned(
                    top: 12,
                    left: 0,
                    right: 0,
                    child: Center(
                      child: Card(
                        child: Padding(
                          padding: EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              SizedBox(
                                width: 14,
                                height: 14,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: AppColors.primary,
                                ),
                              ),
                              SizedBox(width: 8),
                              Text('Finding location...',
                                  style: TextStyle(fontSize: 12)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),

                // My location button
                Positioned(
                  right: 12,
                  bottom: 12,
                  child: FloatingActionButton.small(
                    heroTag: 'location_btn',
                    onPressed: _getUserLocation,
                    backgroundColor: Colors.white,
                    child: const Icon(
                      Icons.my_location_rounded,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 12),

        // Action buttons
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: widget.points.isEmpty ? null : _removeLastPoint,
                icon: const Icon(Icons.undo_rounded, size: 16),
                label: const Text('Undo'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.warning,
                  side: BorderSide(
                    color: widget.points.isEmpty
                        ? AppColors.border
                        : AppColors.warning,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: widget.points.isEmpty ? null : _clearPoints,
                icon: const Icon(Icons.clear_rounded, size: 16),
                label: const Text('Clear All'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.error,
                  side: BorderSide(
                    color: widget.points.isEmpty
                        ? AppColors.border
                        : AppColors.error,
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
