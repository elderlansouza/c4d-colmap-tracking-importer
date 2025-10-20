## v1.1 – 2025-10-01
- Initial public release with Redshift camera, baked PSR/focal, axis fixes, Matrix-on-Vertices, camera duplication + constraint, and scene setup.
## v1.2 – 2025-11-15
-  Fixed occasional 360° rotation jumps caused by Euler angle wrapping during camera keyframe baking.
	•	Added _unwrap_angle() and _unwrap_hpb() helpers to detect and correct discontinuities in HPB (heading/pitch/bank) values.
	•	Updated bake_keys_to_camera() to automatically unwrap rotations before inserting keyframes, ensuring smooth continuous motion across frames.
## v1.3 – 2025-10-20
- Renamed all scene elements for clarity and consistency:  
	• Root null renamed to **GLoMap_Scene_Orient** (was *GLoMap_Import*).  
	• Animated RS camera renamed to **RS_GLoMap_Animated_Camera**.  
	• Render/follow copy renamed to **RS_GLoMap_Render_Camera**.  
	• MoGraph Matrix object renamed to **SparceCloud_Matrix_Previs** (was *Matrix_SparseVertices*).  
- Updated final success dialog to reference the new Matrix object name.  
- Expanded and standardized **framerate presets** for faster setup: added options for 23.98, 24, 25, 29.97, 30, 48, 50, 59.94, 60, 100, 120, and Custom.  
- Optimized dialog layout for compact width (**350 px**) for consistency across versions.  
- No functional or mathematical changes — import logic, keyframe baking, constraint setup, and render configuration remain identical to v1.2.