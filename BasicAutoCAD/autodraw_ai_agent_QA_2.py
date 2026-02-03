# ============================================================
# AutoDraw AI Agent - AutoCAD Drawing Automation (STABLE)
# ============================================================

import win32com.client
import json
import os
import logging
import threading
import pythoncom
import traceback
import time
from typing import Dict, List, Optional
from datetime import datetime

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoDrawAIAgent:
    """
    AutoCAD Automation Agent using AutoLISP APIs
    """

    # =========================================================
    # INIT / CONNECTION
    # =========================================================

    def __init__(self, initialize_autocad: bool = True):
        self.lisp_base_path = r"C:\Users\coronetastera\Documents\Lisp and Dialogue files\Lisp"
        self._thread_local = threading.local()
        self._loaded_lisp = set()
        self._initialized_drawings = set()

        self._setup_lisp_files()

        if initialize_autocad:
            self._initialize_autocad_connection()

    def _initialize_autocad_connection(self):
        pythoncom.CoInitialize()

        try:
            try:
                self._thread_local.autocad = win32com.client.GetActiveObject("AutoCAD.Application")
                logger.info("Connected to existing AutoCAD")
            except Exception:
                self._thread_local.autocad = win32com.client.Dispatch("AutoCAD.Application")
                logger.info("Started new AutoCAD")

            time.sleep(1)

            doc = self._thread_local.autocad.ActiveDocument
            self._thread_local.doc = doc
            self._thread_local.modelspace = doc.ModelSpace

        except Exception:
            pythoncom.CoUninitialize()
            raise

    def _get_autocad_objects(self):
        if not hasattr(self._thread_local, "autocad"):
            self._initialize_autocad_connection()
        return (
            self._thread_local.autocad,
            self._thread_local.doc,
            self._thread_local.modelspace
        )

    # =========================================================
    # LISP SETUP
    # =========================================================

    def _setup_lisp_files(self):
        self.lisp_files = {
            "universal": os.path.join(self.lisp_base_path, "Autodraw_UnivFunctions.lsp"),
            "PG": os.path.join(self.lisp_base_path, "PG_AutoDraw_API.lsp"),
            "MagTrk": os.path.join(self.lisp_base_path, "Mag-Trk_AutoDraw_API.lsp"),
        }

        self.fixture_api_map = {
            "PG": "c:PGAutoAPI",
            "MagTrk": "c:MagTrkAutoAPI",
        }

        self.finish_map = {
            "WH": "White", "WHITE": "White",
            "BK": "Black", "BLACK": "Black",
            "SL": "Silver", "SILVER": "Silver",
            "CC": "CC",
        }

    # =========================================================
    # CORE SEND / WAIT (CRITICAL)
    # =========================================================

    def _wait_for_autocad(self, doc, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                if doc.GetVariable("CMDACTIVE") == 0:
                    time.sleep(0.2)
                    return True
            except Exception:
                pass
            time.sleep(0.2)

        logger.warning("AutoCAD command may not have completed within timeout")
        return False

    def _send_lisp_command(self, doc, cmd: str) -> bool:
        """
        SINGLE SAFE ENTRY POINT FOR COMMANDS
        """
        try:
            logger.info("Sending LISP command")
            doc.SendCommand(cmd.rstrip() + "\n")
            return self._wait_for_autocad(doc)
        except Exception as e:
            logger.error(f"SendCommand failed: {e}")
            return False

    # =========================================================
    # DRAWING INITIALIZATION (ONCE)
    # =========================================================

    def _initialize_drawing_for_fixtures(self, doc, fixture_type=None):
        name = doc.Name
        if name in self._initialized_drawings:
            return True

        logger.info(f"Initializing drawing: {name}")

        uni = self.lisp_files["universal"].replace("\\", "/")
        self._send_lisp_command(doc, f'(load "{uni}")')

        self._send_lisp_command(
            doc,
            '(command "_.insert" "LSAD_Styles" (list 0 0 0) "" "" "")'
        )

        self._send_lisp_command(doc, '(setq ApiMode T)')

        if fixture_type in self.lisp_files:
            fx = self.lisp_files[fixture_type].replace("\\", "/")
            self._send_lisp_command(doc, f'(load "{fx}")')

        self._initialized_drawings.add(name)
        return True

    # =========================================================
    # PG FIXTURE
    # =========================================================

    def draw_fixture(self, fixture_type: str, specs: Dict) -> Dict:
        try:
            if fixture_type == "PG":
                return self._draw_pg_fixture(specs)
            if fixture_type == "MagTrk":
                return self._draw_magtrk_fixture(specs)

            return {"success": False, "error": "Unsupported fixture"}

        except Exception as e:
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def _map_finish(self, f):
        return self.finish_map.get(str(f).upper(), "White")

    def _draw_pg_fixture(self, specs: Dict) -> Dict:
        autocad, doc, _ = self._get_autocad_objects()
        self._initialize_drawing_for_fixtures(doc, "PG")

        cmd = (
            f'(c:PGAutoAPI "{specs["series"]}" "{specs["mounting"]}" '
            f'"{specs["output"]}" {int(specs["regress"])} '
            f'{float(specs["length_ft"])} {float(specs.get("length_in", 0))} '
            f'0 0 nil "{self._map_finish(specs.get("finish"))}" '
            f'"Exact" "EqualLength" 0 nil "F1" 1 "" "" 0 0)'
        )

        ok = self._send_lisp_command(doc, cmd)
        return {"success": ok}

    # =========================================================
    # MAGTRK FIXTURE
    # =========================================================

    def _draw_magtrk_fixture(self, specs: Dict) -> Dict:
        autocad, doc, _ = self._get_autocad_objects()
        self._initialize_drawing_for_fixtures(doc, "MagTrk")

        cmd = (
            f'(c:MagTrkAutoAPI "{specs["series"]}" "{specs["mounting"]}" '
            f'0 nil nil "{self._map_finish(specs.get("finish"))}" '
            f'"Nom" "EqualLength" 0 nil '
            f'{float(specs["length_ft"])} {float(specs.get("length_in", 0))} '
            f'"F1" 1 "" "" 0 0)'
        )

        ok = self._send_lisp_command(doc, cmd)
        return {"success": ok}
