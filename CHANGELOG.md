## v1.1 – 2025-10-01
- Initial public release with Redshift camera, baked PSR/focal, axis fixes, Matrix-on-Vertices, camera duplication + constraint, and scene setup.
## v1.2 – 2025-11-15
-  Fixed occasional 360° rotation jumps caused by Euler angle wrapping during camera keyframe baking.
	•	Added _unwrap_angle() and _unwrap_hpb() helpers to detect and correct discontinuities in HPB (heading/pitch/bank) values.
	•	Updated bake_keys_to_camera() to automatically unwrap rotations before inserting keyframes, ensuring smooth continuous motion across frames.
