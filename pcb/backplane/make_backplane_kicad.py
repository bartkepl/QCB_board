#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator template'u backplane 3U (4 x 5TE) do KiCAD - pcbnew API (KiCad 7/8).

Klade 4 zlacza DIN 41612 typ C a+c (HARTING 09032646824) we wlasciwych pozycjach
wg IEEE 1101.1 Rys.24, dodaje otwory mocujace backplane->subrack i obrys plytki.

JAK URUCHOMIC:
  1) Otworz KiCAD -> nowy projekt -> otworz PCB Editor (pusty board).
  2) Tools -> Scripting Console.
  3) W konsoli:  exec(open(r"/sciezka/do/make_backplane_kicad.py").read())
  4) Zapisz plytke (Ctrl+S).  Refresh: View -> Refresh jesli trzeba.

Footprint jest WBUDOWANY w skrypt (zapisywany do temp .pretty), wiec nie zalezy
od sciezek bibliotek. Mozesz tez po prostu uzyc gotowego footprintu z biblioteki
KiCAD: Connector_DIN -> DIN41612_C_2x32_Female_Vertical_THT (te same wymiary).
"""
import pcbnew, os, tempfile

# ---- PARAMETRY (IEEE 1101.1 Rys.24) ----
SLOTS_X   = [7.47, 32.87, 58.27, 83.67]   # srodki zlaczy (row b / os) od lewej [mm]
Y_CONN_C  = 64.35      # pionowy srodek zlacza (= srodek plytki 128.7)
PIN_A1_DX = -2.54      # row a wzgledem osi slotu (anchor footprintu = pin a1 = row a)
PIN_FIELD_HALF = 39.37 # pol pola pinow (78.74/2)
BOARD_W, BOARD_H = 101.6, 128.7
MNT_Y     = [3.10, 125.60]   # otwory mocujace backplane (F1=122.5) od gory [mm]
MNT_DRILL = 2.70             # M2.5 clearance

FP_NAME = "DIN41612_C_2x32_Female_Vertical_THT"
FP_TEXT = r"""(module DIN41612_C_2x32_Female_Vertical_THT (layer F.Cu) (tedit 5EAFCB7F)
  (descr "DIN41612 connector, type C, Vertical, 3 rows 32 pins wide, https://www.erni-x-press.com/de/downloads/kataloge/englische_kataloge/erni-din41612-iec60603-2-e.pdf")
  (tags "DIN 41612 IEC 60603 C")
  (fp_text reference REF** (at 2.54 -9.13) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value DIN41612_C_2x32_Female_Vertical_THT (at 2.54 87.87) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_line (start -1.71 -3.13) (end 3.79 -3.13) (layer F.Fab) (width 0.1))
  (fp_line (start 3.79 -3.13) (end 3.79 -2.13) (layer F.Fab) (width 0.1))
  (fp_line (start 3.79 -2.13) (end 6.79 -2.13) (layer F.Fab) (width 0.1))
  (fp_line (start 6.79 -2.13) (end 6.79 80.87) (layer F.Fab) (width 0.1))
  (fp_line (start 6.79 80.87) (end 3.79 80.87) (layer F.Fab) (width 0.1))
  (fp_line (start 3.79 80.87) (end 3.79 81.87) (layer F.Fab) (width 0.1))
  (fp_line (start 3.79 81.87) (end -1.71 81.87) (layer F.Fab) (width 0.1))
  (fp_line (start -1.71 81.87) (end -1.71 -3.13) (layer F.Fab) (width 0.1))
  (fp_line (start -2.76 -8.13) (end 7.84 -8.13) (layer F.Fab) (width 0.1))
  (fp_line (start 7.84 -8.13) (end 7.84 86.87) (layer F.Fab) (width 0.1))
  (fp_line (start 7.84 86.87) (end -2.76 86.87) (layer F.Fab) (width 0.1))
  (fp_line (start -2.76 86.87) (end -2.76 -8.13) (layer F.Fab) (width 0.1))
  (fp_line (start -2.87 -8.24) (end 7.95 -8.24) (layer F.SilkS) (width 0.12))
  (fp_line (start 7.95 -8.24) (end 7.95 86.98) (layer F.SilkS) (width 0.12))
  (fp_line (start 7.95 86.98) (end -2.87 86.98) (layer F.SilkS) (width 0.12))
  (fp_line (start -2.87 86.98) (end -2.87 -8.24) (layer F.SilkS) (width 0.12))
  (fp_line (start -3.26 -8.63) (end 8.34 -8.63) (layer F.CrtYd) (width 0.05))
  (fp_line (start 8.34 -8.63) (end 8.34 87.37) (layer F.CrtYd) (width 0.05))
  (fp_line (start 8.34 87.37) (end -3.26 87.37) (layer F.CrtYd) (width 0.05))
  (fp_line (start -3.26 87.37) (end -3.26 -8.63) (layer F.CrtYd) (width 0.05))
  (fp_line (start -3.06 0) (end -3.74 -0.3) (layer F.SilkS) (width 0.12))
  (fp_line (start -3.74 -0.3) (end -3.74 0.3) (layer F.SilkS) (width 0.12))
  (fp_line (start -3.74 0.3) (end -3.06 0) (layer F.SilkS) (width 0.12))
  (fp_line (start -2.76 -0.5) (end -2.06 0) (layer F.Fab) (width 0.1))
  (fp_line (start -2.06 0) (end -2.76 0.5) (layer F.Fab) (width 0.1))
  (fp_line (start -1.71 -3.131) (end 3.79 -3.131) (layer F.SilkS) (width 0.12))
  (fp_line (start 3.79 -3.131) (end 3.79 -2.131) (layer F.SilkS) (width 0.12))
  (fp_line (start 3.79 -2.131) (end 6.79 -2.131) (layer F.SilkS) (width 0.12))
  (fp_line (start 6.79 -2.131) (end 6.79 80.87) (layer F.SilkS) (width 0.12))
  (fp_line (start 6.79 80.87) (end 3.79 80.87) (layer F.SilkS) (width 0.12))
  (fp_line (start 3.79 80.87) (end 3.79 81.87) (layer F.SilkS) (width 0.12))
  (fp_line (start 3.79 81.87) (end -1.71 81.87) (layer F.SilkS) (width 0.12))
  (fp_line (start -1.71 81.87) (end -1.71 -3.131) (layer F.SilkS) (width 0.12))
  (pad a1 thru_hole roundrect (at 0 0) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask) (roundrect_rratio 0.16129))
  (pad a2 thru_hole circle (at 0 2.54) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a3 thru_hole circle (at 0 5.08) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a4 thru_hole circle (at 0 7.62) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a5 thru_hole circle (at 0 10.16) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a6 thru_hole circle (at 0 12.7) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a7 thru_hole circle (at 0 15.24) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a8 thru_hole circle (at 0 17.78) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a9 thru_hole circle (at 0 20.32) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a10 thru_hole circle (at 0 22.86) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a11 thru_hole circle (at 0 25.4) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a12 thru_hole circle (at 0 27.94) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a13 thru_hole circle (at 0 30.48) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a14 thru_hole circle (at 0 33.02) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a15 thru_hole circle (at 0 35.56) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a16 thru_hole circle (at 0 38.1) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a17 thru_hole circle (at 0 40.64) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a18 thru_hole circle (at 0 43.18) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a19 thru_hole circle (at 0 45.72) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a20 thru_hole circle (at 0 48.26) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a21 thru_hole circle (at 0 50.8) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a22 thru_hole circle (at 0 53.34) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a23 thru_hole circle (at 0 55.88) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a24 thru_hole circle (at 0 58.42) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a25 thru_hole circle (at 0 60.96) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a26 thru_hole circle (at 0 63.5) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a27 thru_hole circle (at 0 66.04) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a28 thru_hole circle (at 0 68.58) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a29 thru_hole circle (at 0 71.12) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a30 thru_hole circle (at 0 73.66) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a31 thru_hole circle (at 0 76.2) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad a32 thru_hole circle (at 0 78.74) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c1 thru_hole circle (at 5.08 0) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c2 thru_hole circle (at 5.08 2.54) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c3 thru_hole circle (at 5.08 5.08) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c4 thru_hole circle (at 5.08 7.62) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c5 thru_hole circle (at 5.08 10.16) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c6 thru_hole circle (at 5.08 12.7) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c7 thru_hole circle (at 5.08 15.24) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c8 thru_hole circle (at 5.08 17.78) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c9 thru_hole circle (at 5.08 20.32) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c10 thru_hole circle (at 5.08 22.86) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c11 thru_hole circle (at 5.08 25.4) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c12 thru_hole circle (at 5.08 27.94) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c13 thru_hole circle (at 5.08 30.48) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c14 thru_hole circle (at 5.08 33.02) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c15 thru_hole circle (at 5.08 35.56) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c16 thru_hole circle (at 5.08 38.1) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c17 thru_hole circle (at 5.08 40.64) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c18 thru_hole circle (at 5.08 43.18) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c19 thru_hole circle (at 5.08 45.72) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c20 thru_hole circle (at 5.08 48.26) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c21 thru_hole circle (at 5.08 50.8) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c22 thru_hole circle (at 5.08 53.34) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c23 thru_hole circle (at 5.08 55.88) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c24 thru_hole circle (at 5.08 58.42) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c25 thru_hole circle (at 5.08 60.96) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c26 thru_hole circle (at 5.08 63.5) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c27 thru_hole circle (at 5.08 66.04) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c28 thru_hole circle (at 5.08 68.58) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c29 thru_hole circle (at 5.08 71.12) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c30 thru_hole circle (at 5.08 73.66) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c31 thru_hole circle (at 5.08 76.2) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad c32 thru_hole circle (at 5.08 78.74) (size 1.55 1.55) (drill 1) (layers *.Cu *.Mask))
  (pad "" np_thru_hole circle (at 2.24 -5.63) (size 2.85 2.85) (drill 2.85) (layers *.Cu *.Mask))
  (pad "" np_thru_hole circle (at 2.24 84.37) (size 2.85 2.85) (drill 2.85) (layers *.Cu *.Mask))
  (fp_text user %R (at 2.54 39.37) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (model ${KISYS3DMOD}/Connector_DIN.3dshapes/DIN41612_C_2x32_Female_Vertical_THT.wrl
    (at (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)"""

def mm(v): return pcbnew.FromMM(float(v))
def vec(x,y):
    try:    return pcbnew.VECTOR2I(mm(x), mm(y))
    except Exception: return pcbnew.wxPoint(mm(x), mm(y))

board = pcbnew.GetBoard()

# zapis footprintu do temp .pretty i zaladowanie
libdir = tempfile.mkdtemp(suffix=".pretty")
with open(os.path.join(libdir, FP_NAME + ".kicad_mod"), "w", encoding="utf-8") as f:
    f.write(FP_TEXT)

def add_connectors():
    for i, sx in enumerate(SLOTS_X):
        fp = pcbnew.FootprintLoad(libdir, FP_NAME)
        if fp is None:
            print("BLAD: nie zaladowano footprintu"); return
        fp.SetReference("J%d" % (i+1))
        # anchor (pin a1 = row a, gora pola pinow) -> (sx + PIN_A1_DX, Y_CONN_C - PIN_FIELD_HALF)
        fp.SetPosition(vec(sx + PIN_A1_DX, Y_CONN_C - PIN_FIELD_HALF))
        fp.SetOrientationDegrees(0)   # pole pinow pionowo, rzedy a|c poziomo
        board.Add(fp)
        print("  J%d @ slot X=%.2f (pin a1 @ %.2f, %.2f)" % (i+1, sx, sx+PIN_A1_DX, Y_CONN_C-PIN_FIELD_HALF))

def add_mounting_holes():
    for sx in SLOTS_X:
        for my in MNT_Y:
            fp = pcbnew.FOOTPRINT(board)
            fp.SetPosition(vec(sx, my))
            pad = pcbnew.PAD(fp)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(vec(MNT_DRILL, MNT_DRILL))
            pad.SetDrillSize(vec(MNT_DRILL, MNT_DRILL))
            try:    pad.SetLayerSet(pad.UnplatedHoleMask())
            except Exception: pass
            fp.Add(pad); board.Add(fp)

def add_outline():
    pts = [(0,0),(BOARD_W,0),(BOARD_W,BOARD_H),(0,BOARD_H),(0,0)]
    for (x0,y0),(x1,y1) in zip(pts, pts[1:]):
        s = pcbnew.PCB_SHAPE(board)
        try:    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        except Exception: pass
        s.SetStart(vec(x0,y0)); s.SetEnd(vec(x1,y1))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
        board.Add(s)

print("Backplane 3U 4x5TE -> KiCAD")
add_outline()
add_connectors()
add_mounting_holes()
try: pcbnew.Refresh()
except Exception: pass
print("Gotowe. Zapisz plytke (Ctrl+S). Uwaga: w razie potrzeby przerzuc footprinty na wlasciwa warstwe (F/B.Cu).")
