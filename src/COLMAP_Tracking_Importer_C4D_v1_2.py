# -*- coding: utf-8 -*-
# COLMAP/GLoMap (TXT) -> Redshift Camera + Matrix-on-Vertices (no Cloner/TP) in Cinema 4D
# Latest stable: V1.1 (no background auto-assign)
# - Imports COLMAP TXT from scene/sparse[/model_id].
# - Builds Redshift Camera with baked PSR+focal keys.
# - Fixed axes:
#     * World basis (COLMAP -> C4D): Flip Y
#     * Camera-local fix: Flip Y (right-multiply)
# - Imports sparse as a PolygonObject and creates a MoGraph Matrix object in Object→Vertex mode.
# - Duplicates RS Camera to root, adds Constraint Tag (Transform Targets via B-family IDs; PSR fallback).
# - Sets timeline & preview range; render output resolution and Film Aspect = Custom.
# - Final concise success message with resolution, duration, and Matrix distribution note.
# MIT

import os, math, c4d
from c4d import gui, utils

# ------------------------ Filesystem helpers ------------------------

def find_sparse_txt_folder(scene_folder):
    sparse = os.path.join(scene_folder, "sparse")
    if not os.path.isdir(sparse):
        return None
    def has_txt(path):
        return (os.path.isfile(os.path.join(path, "cameras.txt")) and
                os.path.isfile(os.path.join(path, "images.txt")) and
                os.path.isfile(os.path.join(path, "points3D.txt")))
    if has_txt(sparse):
        return sparse
    try:
        for name in sorted(os.listdir(sparse)):
            p = os.path.join(sparse, name)
            if os.path.isdir(p) and has_txt(p):
                return p
    except Exception:
        pass
    return None

# ------------------------ COLMAP parsers ------------------------

def parse_cameras_txt(path):
    cams = {}
    if not os.path.isfile(path): return cams
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'): continue
            p = s.split()
            cams[int(p[0])] = {
                "model": p[1], "width": float(p[2]), "height": float(p[3]),
                "params": list(map(float, p[4:]))
            }
    return cams

def parse_images_txt(path):
    imgs = []
    if not os.path.isfile(path): return imgs
    with open(path, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line: break
            s = line.strip()
            if not s or s.startswith('#'): continue
            p = s.split()
            if len(p) < 10: continue
            imgs.append({
                "image_id": int(p[0]),
                "qw": float(p[1]), "qx": float(p[2]), "qy": float(p[3]), "qz": float(p[4]),
                "tx": float(p[5]), "ty": float(p[6]), "tz": float(p[7]),
                "camera_id": int(p[8]),
                "name": " ".join(p[9:])
            })
            _ = f.readline()  # skip 2D points line
    imgs.sort(key=lambda d: d["image_id"])
    return imgs

def parse_points3D_txt(path):
    pts = []
    if not os.path.isfile(path): return pts
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'): continue
            p = line.split()
            if len(p) < 4: continue
            pts.append((float(p[1]), float(p[2]), float(p[3])))
    return pts

# ------------------------ Math / transforms ------------------------

def quat_to_matrix(qw,qx,qy,qz):
    n = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
    if n == 0.0: qw,qx,qy,qz = 1.0,0.0,0.0,0.0
    else: qw,qx,qy,qz = qw/n, qx/n, qy/n, qz/n
    xx,yy,zz = qx*qx, qy*qy, qz*qz
    xy,xz,yz = qx*qy, qx*qz, qy*qz
    wx,wy,wz = qw*qx, qw*qy, qw*qz
    r00 = 1.0 - 2.0*(yy+zz); r01 = 2.0*(xy - wz);   r02 = 2.0*(xz + wy)
    r10 = 2.0*(xy + wz);     r11 = 1.0 - 2.0*(xx+zz); r12 = 2.0*(yz - wx)
    r20 = 2.0*(xz - wy);     r21 = 2.0*(yz + wx);     r22 = 1.0 - 2.0*(xx+yy)
    m = c4d.Matrix()
    m.v1 = c4d.Vector(r00, r10, r20)
    m.v2 = c4d.Vector(r01, r11, r21)
    m.v3 = c4d.Vector(r02, r12, r22)
    return m

def mm_from_pixels(f_in_px, sensor_width_mm, img_width_px, fx_override=None):
    fpx = fx_override if fx_override is not None else f_in_px
    if img_width_px <= 0: return 36.0
    return (fpx * sensor_width_mm) / float(img_width_px)

def build_cam_params(cdef, sensor_width_mm):
    model = cdef["model"].upper(); width = cdef["width"]; p = cdef["params"]
    if model in ("SIMPLE_PINHOLE","SIMPLE_RADIAL","SIMPLE_RADIAL_1","SIMPLE_RADIAL_FISHEYE"):
        return mm_from_pixels(p[0], sensor_width_mm, width)
    if model in ("PINHOLE","OPENCV","FULL_OPENCV","OPENCV_FISHEYE"):
        return mm_from_pixels(None, sensor_width_mm, width, fx_override=p[0])
    return mm_from_pixels(p[0], sensor_width_mm, width)

# Fixed axes
B_WORLD = [[1,0,0],[0,-1,0],[0,0,1]]  # Flip Y

def apply_B_to_vec(v, B):
    return c4d.Vector(
        B[0][0]*v.x + B[0][1]*v.y + B[0][2]*v.z,
        B[1][0]*v.x + B[1][1]*v.y + B[1][2]*v.z,
        B[2][0]*v.x + B[2][1]*v.y + B[2][2]*v.z
    )

def apply_B_to_matrix(m, B):
    out = c4d.Matrix()
    out.v1 = apply_B_to_vec(m.v1, B)
    out.v2 = apply_B_to_vec(m.v2, B)
    out.v3 = apply_B_to_vec(m.v3, B)
    out.off= apply_B_to_vec(m.off, B)
    return out

def right_multiply_flip_y(M):
    fix = c4d.Matrix()
    fix.v1 = c4d.Vector( 1, 0, 0)
    fix.v2 = c4d.Vector( 0,-1, 0)
    fix.v3 = c4d.Vector( 0, 0, 1)
    fix.off = c4d.Vector(0,0,0)
    return M * fix

def colmap_to_c4d_matrix(qw,qx,qy,qz, tx,ty,tz):
    R = quat_to_matrix(qw,qx,qy,qz)
    Rt = c4d.Matrix()
    Rt.v1 = c4d.Vector(R.v1.x, R.v2.x, R.v3.x)
    Rt.v2 = c4d.Vector(R.v1.y, R.v2.y, R.v3.y)
    Rt.v3 = c4d.Vector(R.v1.z, R.v2.z, R.v3.z)
    C = -(Rt.MulV(c4d.Vector(tx,ty,tz)))
    M = c4d.Matrix(); M.v1, M.v2, M.v3, M.off = Rt.v1, Rt.v2, Rt.v3, C
    Mw = apply_B_to_matrix(M, B_WORLD)
    return right_multiply_flip_y(Mw)

# ---------- Angle unwrapping helpers (keep rotations continuous) ----------

def _unwrap_angle(prev, curr):
    """
    Shift 'curr' by +/- 2π so that it stays as close as possible to 'prev'.
    Works in radians (Cinema 4D's HPB).
    """
    if prev is None:
        return curr
    twopi = 2.0 * math.pi
    delta = curr - prev
    while delta > math.pi:
        curr -= twopi
        delta -= twopi
    while delta <= -math.pi:
        curr += twopi
        delta += twopi
    return curr

def _unwrap_hpb(prev_hpb, curr_hpb):
    """
    Unwrap each component of the HPB vector (X=H, Y=P, Z=B) against previous.
    Returns (unwrapped_hpb, new_prev_hpb)
    """
    if prev_hpb is None:
        return curr_hpb, curr_hpb
    h = _unwrap_angle(prev_hpb.x, curr_hpb.x)
    p = _unwrap_angle(prev_hpb.y, curr_hpb.y)
    b = _unwrap_angle(prev_hpb.z, curr_hpb.z)
    unwrapped = c4d.Vector(h, p, b)
    return unwrapped, unwrapped

# ------------------------ Keyframing ------------------------

def _id_pos_x(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))

def _id_pos_y(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0))

def _id_pos_z(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))

def _id_rot_h(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))

def _id_rot_p(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0))

def _id_rot_b(): return c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_ROTATION, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))

def _id_focus(): return c4d.DescID(c4d.DescLevel(c4d.CAMERAOBJECT_FOCUS, c4d.DTYPE_REAL, 0))

def ensure_track(op, did):
    tr = op.FindCTrack(did)
    if tr is None:
        tr = c4d.CTrack(op, did)
        op.InsertTrackSorted(tr)
    return tr

def insert_key(track, time, value):
    c = track.GetCurve(); k = c4d.CKey(); k.SetTime(c, time); k.SetValue(c, value); c.InsertKey(k)

def bake_keys_to_camera(cam, keyframes, sensor_mm):
    tr_px = ensure_track(cam, _id_pos_x()); tr_py = ensure_track(cam, _id_pos_y()); tr_pz = ensure_track(cam, _id_pos_z())
    tr_h  = ensure_track(cam, _id_rot_h()); tr_p  = ensure_track(cam, _id_rot_p());  tr_b  = ensure_track(cam, _id_rot_b())
    tr_f  = ensure_track(cam, _id_focus())

    prev_hpb = None  # track previous (already unwrapped) angles

    for t, mg, fl_mm in keyframes:
        # Preserve existing behavior for transform/focus/aperture
        cam.SetMg(mg)
        cam[c4d.CAMERAOBJECT_FOCUS]    = fl_mm
        cam[c4d.CAMERAOBJECT_APERTURE] = sensor_mm

        # Convert to HPB (radians), then unwrap to avoid 360° jumps
        hpb_raw = utils.MatrixToHPB(mg, c4d.ROTATIONORDER_DEFAULT)
        hpb_unwrapped, prev_hpb = _unwrap_hpb(prev_hpb, hpb_raw)

        # Key position
        insert_key(tr_px, t, mg.off.x)
        insert_key(tr_py, t, mg.off.y)
        insert_key(tr_pz, t, mg.off.z)

        # Key rotation (unwrapped)
        insert_key(tr_h,  t, hpb_unwrapped.x)
        insert_key(tr_p,  t, hpb_unwrapped.y)
        insert_key(tr_b,  t, hpb_unwrapped.z)

        # Key focus
        insert_key(tr_f,  t, fl_mm)

# ------------------------ Redshift camera discovery ------------------------

def find_rs_camera_object_id():
    try: plist = c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_OBJECT, True)
    except Exception: return None
    if not plist: return None
    for plug in plist:
        try: name = plug.GetName()
        except Exception: continue
        if isinstance(name, str):
            low = name.lower()
            if "camera" in low and ("redshift" in low or low.startswith("rs")):
                try: return plug.GetID()
                except Exception: pass
    return None

# ------------------------ Sparse import helpers ------------------------

def import_point_cloud(doc, points, parent=None):
    """Create a PolygonObject with one point per COLMAP 3D point (already scaled/axis-fixed)."""
    if not points: return None
    pts_c4d = [apply_B_to_vec(c4d.Vector(x,y,z), B_WORLD) for (x,y,z) in points]
    obj = c4d.PolygonObject(len(pts_c4d), 0)
    obj.SetName("GLoMap_SparseCloud")
    obj.SetAllPoints(pts_c4d)
    (obj.InsertUnder(parent) if parent else doc.InsertObject(obj))
    obj.Message(c4d.MSG_UPDATE)
    return obj

def add_matrix_on_sparse_vertices(doc, sparse_obj, parent=None):
    """
    Create a MoGraph Matrix object and configure:
      - Mode: Object (enum 0 on your build)
      - Draw Size: 0.5
      - Object link: sparse_obj
      - Distribution: Vertex (resolved by reading the parameter's cycle)
    """
    if sparse_obj is None:
        return None

    mtx = c4d.BaseObject(c4d.Omgmatrix)
    mtx.SetName("Matrix_SparseVertices")
    (mtx.InsertUnder(parent) if parent else doc.InsertObject(mtx))

    def DID(i, dtype, creator):
        return c4d.DescID(c4d.DescLevel(i, dtype, creator))

    # Mode -> Object (2010 / 1018639) == 0 on your build
    mtx.SetParameter(DID(2010, c4d.DTYPE_LONG, 1018639), 0, c4d.DESCFLAGS_SET_0)

    # Generate -> Matrices Only (optional)
    try:
        mtx.SetParameter(DID(1020, c4d.DTYPE_LONG, 1018545), 3, c4d.DESCFLAGS_SET_0)
    except Exception:
        pass

    # Draw Size -> 0.5
    mtx.SetParameter(DID(1025, c4d.DTYPE_REAL, 1018545), 0.5, c4d.DESCFLAGS_SET_0)

    # Object link (primary + legacy compat)
    mtx.SetParameter(DID(1015, c4d.DTYPE_BASELISTLINK, 1018740), sparse_obj, c4d.DESCFLAGS_SET_0)
    try:
        mtx.SetParameter(DID(2114, c4d.DTYPE_BASELISTLINK, 1018639), sparse_obj, c4d.DESCFLAGS_SET_0)
    except Exception:
        pass

    # Distribution -> resolve "Vertex" by reading the cycle (enum) list
    dist_did = DID(1100, c4d.DTYPE_LONG, 1018571)
    try:
        desc = c4d.Description()
        if mtx.GetDescription(desc, c4d.DESCFLAGS_DESC_0):
            for did, bc in desc:
                if isinstance(did, c4d.DescID) and did.GetDepth() >= 1 and did[0].id == 1100 and did[0].creator == 1018571:
                    cyc = bc.GetContainer(c4d.DESC_CYCLE)
                    if isinstance(cyc, c4d.BaseContainer):
                        chosen = None
                        for key, label in cyc:
                            try:
                                if "vertex" in str(label).strip().lower():
                                    chosen = key
                                    break
                            except Exception:
                                continue
                        if chosen is not None:
                            mtx.SetParameter(dist_did, int(chosen), c4d.DESCFLAGS_SET_0)
                    break
    except Exception:
        pass

    mtx.Message(c4d.MSG_UPDATE)
    return mtx

# ------------------------ Scene helpers ------------------------

def ensure_null(doc, name):
    n = c4d.BaseObject(c4d.Onull)
    n.SetName(name)
    doc.InsertObject(n)
    return n

# ------------------------ Constraint setup (B-family IDs + PSR fallback) ------------------------

ID_TRANSFORM_ENABLE = 1000  # enable Transform block
ID_TARGET_LINK_B = 10001
ID_WEIGHT_B      = 10002
ID_P_B           = 10005
ID_R_B           = 10007
ID_S_B           = 10006

def _desc(i):
    return c4d.DescID(c4d.DescLevel(i))

def setup_constraint_follow(dup_cam, src_cam):
    tag = c4d.BaseTag(c4d.Tcaconstraint)
    if not tag:
        raise RuntimeError("Failed to create Character Constraint tag.")
    dup_cam.InsertTag(tag)

    # Transform path (inline/B)
    if tag.SetParameter(_desc(ID_TRANSFORM_ENABLE), True, c4d.DESCFLAGS_SET_0):
        tag.SetParameter(_desc(ID_P_B), True,  c4d.DESCFLAGS_SET_0)
        tag.SetParameter(_desc(ID_R_B), True,  c4d.DESCFLAGS_SET_0)
        tag.SetParameter(_desc(ID_S_B), True,  c4d.DESCFLAGS_SET_0)
        if not tag.SetParameter(_desc(ID_WEIGHT_B), 1.0, c4d.DESCFLAGS_SET_0):
            tag.SetParameter(_desc(ID_WEIGHT_B), 100.0, c4d.DESCFLAGS_SET_0)
        tag.SetParameter(_desc(ID_TARGET_LINK_B), src_cam, c4d.DESCFLAGS_SET_0)
        tag.Message(c4d.MSG_UPDATE)
        dup_cam.Message(c4d.MSG_UPDATE)
        return tag

    # PSR fallback
    bc = tag.GetDataInstance()
    k = getattr
    k_PSR         = k(c4d, "ID_CA_CONSTRAINT_TAG_PSR", None)
    k_PARENT_LINK = k(c4d, "ID_CA_CONSTRAINT_TAG_PARENT_LINK", None)
    k_PSR_P       = k(c4d, "ID_CA_CONSTRAINT_TAG_PSR_P", None)
    k_PSR_R       = k(c4d, "ID_CA_CONSTRAINT_TAG_PSR_R", None)
    k_PSR_S       = k(c4d, "ID_CA_CONSTRAINT_TAG_PSR_S", None)

    if k_PSR is None or k_PARENT_LINK is None:
        raise RuntimeError("Constraint setup failed: Transform and PSR unavailable on this build.")

    bc[k_PSR] = True
    bc[k_PARENT_LINK] = src_cam
    if k_PSR_P is not None: bc[k_PSR_P] = True
    if k_PSR_R is not None: bc[k_PSR_R] = True
    if k_PSR_S is not None: bc[k_PSR_S] = True

    tag.Message(c4d.MSG_UPDATE)
    dup_cam.Message(c4d.MSG_UPDATE)
    return tag

# ------------------------ UI ------------------------

class ImportDialog(gui.GeDialog):
    ID_SCENEFOLDER = 1001
    ID_BTN_BROWSE  = 1002
    ID_SENSOR      = 1003
    ID_FPS         = 1004
    ID_SCALE       = 1005
    ID_POINTS      = 1006

    def CreateLayout(self):
        # Title updated per request
        self.SetTitle("COLMAP Tracking Importer C4D V1.1")
        self.GroupBegin(10, c4d.BFH_SCALEFIT, 3, 1)
        self.AddStaticText(11, c4d.BFH_LEFT, 260, 0, "Scene folder (contains 'sparse'):")
        self.AddEditText(self.ID_SCENEFOLDER, c4d.BFH_SCALEFIT, 520, 0)
        self.AddButton(self.ID_BTN_BROWSE, c4d.BFH_LEFT, 100, 0, "Browse…")
        self.GroupEnd()

        self.GroupBegin(20, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(21, c4d.BFH_LEFT, 220, 0, "Sensor width (mm):")
        self.AddEditNumberArrows(self.ID_SENSOR, c4d.BFH_LEFT)
        self.GroupEnd()

        self.GroupBegin(30, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(31, c4d.BFH_LEFT, 220, 0, "Timeline FPS:")
        self.AddEditNumberArrows(self.ID_FPS, c4d.BFH_LEFT)
        self.GroupEnd()

        self.GroupBegin(40, c4d.BFH_SCALEFIT, 2, 1)
        self.AddStaticText(41, c4d.BFH_LEFT, 220, 0, "Global scale (scene units):")
        self.AddEditNumberArrows(self.ID_SCALE, c4d.BFH_LEFT)
        self.GroupEnd()

        self.AddCheckbox(self.ID_POINTS, c4d.BFH_LEFT, 0, 0, "Import sparse point cloud")

        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.GroupBegin(200, c4d.BFH_RIGHT, 2, 1)
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)
        self.GroupEnd()

        # Footer copyright line (added per request)
        self.AddSeparatorH(0, c4d.BFH_SCALEFIT)
        self.AddStaticText(300, c4d.BFH_CENTER, 0, 0, "Copyright: Elderlan Souza  •  email: elderlan.design@gmail.com")

        fps = doc.GetFps() if doc else 24
        self.SetFloat(self.ID_SENSOR, 36.0, min=1.0, max=100.0, step=0.1)
        self.SetInt32(self.ID_FPS, fps, min=1, max=240, step=1)
        self.SetFloat(self.ID_SCALE, 100.0, min=0.0001, max=100000.0, step=0.1)
        self.SetBool(self.ID_POINTS, True)
        return True

    def Command(self, cid, msg):
        if cid == self.ID_BTN_BROWSE:
            p = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY, title="Select Scene Folder")
            if p: self.SetString(self.ID_SCENEFOLDER, p)
        elif cid == c4d.DLG_OK:
            self.do_import(); self.Close()
        elif cid == c4d.DLG_CANCEL:
            self.Close()
        return True

    def do_import(self):
        scene_folder = self.GetString(self.ID_SCENEFOLDER)
        if not scene_folder or not os.path.isdir(scene_folder):
            gui.MessageDialog("Please select a valid SCENE folder (must contain 'sparse').")
            return

        sparse = find_sparse_txt_folder(scene_folder)
        if not sparse:
            gui.MessageDialog("Could not find a COLMAP TXT model under 'sparse'.")
            return

        sensor_mm = self.GetFloat(self.ID_SENSOR)
        fps       = self.GetInt32(self.ID_FPS)
        scale     = self.GetFloat(self.ID_SCALE)
        do_points = self.GetBool(self.ID_POINTS)

        cams = parse_cameras_txt(os.path.join(sparse, "cameras.txt"))
        imgs = parse_images_txt(os.path.join(sparse, "images.txt"))
        pts  = parse_points3D_txt(os.path.join(sparse, "points3D.txt")) if do_points else []
        if not cams or not imgs:
            gui.MessageDialog("Could not read cameras.txt / images.txt in the sparse model.")
            return

        doc.StartUndo()
        try:
            root = ensure_null(doc, "GLoMap_Import")

            # Timeline
            if fps > 0: doc.SetFps(fps)
            n = len(imgs)
            doc.SetMinTime(c4d.BaseTime(0, fps))
            doc.SetMaxTime(c4d.BaseTime(max(1, n), fps))
            doc.SetTime(c4d.BaseTime(0, fps))
            # Also set the Preview Range to match the full timeline
            doc.SetLoopMinTime(c4d.BaseTime(0, fps))
            doc.SetLoopMaxTime(c4d.BaseTime(max(1, n), fps))

            # Points first (Matrix + reference polygon)
            sparse_obj = None
            if pts:
                pts_scaled = [(x*scale, y*scale, z*scale) for (x,y,z) in pts]
                sparse_obj = import_point_cloud(doc, pts_scaled, parent=root)
                add_matrix_on_sparse_vertices(doc, sparse_obj, parent=None)

            # Build camera keyframes
            keyframes = []
            for i, im in enumerate(imgs):
                cdef = cams.get(im["camera_id"])
                if not cdef: continue
                fl_mm = build_cam_params(cdef, sensor_mm)
                m_c4d = colmap_to_c4d_matrix(
                    im["qw"], im["qx"], im["qy"], im["qz"],
                    im["tx"]*scale, im["ty"]*scale, im["tz"]*scale
                )
                keyframes.append((c4d.BaseTime(i, fps), m_c4d, fl_mm))

            # RS camera
            rs_id = find_rs_camera_object_id()
            if not rs_id:
                gui.MessageDialog("Redshift Camera object plugin not found. No RS camera created.")
                return

            rs_cam = c4d.BaseObject(rs_id)
            rs_cam.SetName("RS Camera [Fixed Flip Y / local Flip Y]")
            rs_cam.InsertUnder(root)
            bake_keys_to_camera(rs_cam, keyframes, sensor_mm)

            # Duplicate + Constraint
            dup_cam = None
            try:
                dup_cam = rs_cam.GetClone()
                dup_cam.SetName("Copy_" + rs_cam.GetName())
                doc.InsertObject(dup_cam)  # at scene root

                setup_constraint_follow(dup_cam, rs_cam)
                dup_cam.Message(c4d.MSG_UPDATE)
            except Exception as e:
                gui.MessageDialog(f"Camera duplication/constraint failed: {e}")

            # ---------- Render Output (resolution, preview range, film aspect custom) ----------
            res_w = res_h = None
            try:
                if imgs:
                    c0 = cams.get(imgs[0]["camera_id"])
                    if c0:
                        res_w = int(c0["width"])
                        res_h = int(c0["height"])
            except Exception:
                pass

            try:
                rd = doc.GetActiveRenderData()
                if rd:
                    if res_w and res_h:
                        rd[c4d.RDATA_XRES] = res_w
                        rd[c4d.RDATA_YRES] = res_h
                    try:
                        rd[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_PREVIEWRANGE
                    except Exception:
                        loop_min = doc.GetLoopMinTime()
                        loop_max = doc.GetLoopMaxTime()
                        rd[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_MANUAL
                        rd[c4d.RDATA_FRAMEFROM] = loop_min
                        rd[c4d.RDATA_FRAMETO]   = loop_max
                    try:
                        rd[c4d.RDATA_FILMASPECT] = c4d.RDATA_FILMASPECT_CUSTOM
                    except Exception:
                        pass
                    try:
                        rd[c4d.RDATA_PIXELASPECT] = 1.0
                    except Exception:
                        pass
            except Exception:
                pass

            c4d.EventAdd()
        finally:
            doc.EndUndo()

        # ------- Final concise message -------
        res_text = "Unknown"
        try:
            c0 = cams.get(imgs[0]["camera_id"])
            if c0:
                res_text = f"{int(c0['width'])} x {int(c0['height'])}"
        except Exception:
            pass

        gui.MessageDialog(
            "Scene import successful\n"
            f"Resolution: {res_text}\n"
            f"Duration: {n} frames\n"
            "To visualise the point cloud, select the Matrix object and change the Distribution to Vertex."
        )

# ------------------------ Main ------------------------

def main():
    ImportDialog().Open(c4d.DLG_TYPE_MODAL, defaultw=860, defaulth=0)

if __name__ == "__main__":
    main()