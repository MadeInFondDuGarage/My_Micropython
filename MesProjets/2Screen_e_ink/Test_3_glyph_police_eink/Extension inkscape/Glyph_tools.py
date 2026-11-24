#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inkex
from make_svg_model import GlyphGridEffect
from auto_metrics import AutoMetrics
from convert_svg_to_svg_font import ExportSVGFont

class GlyphsToolkit(inkex.Effect):

    def add_arguments(self, pars):
        # Onglet actif
        pars.add_argument("--active-tab", type=str, dest="active_tab", default="tab_grid")

        # Paramètres - Onglet 1 (Glyph Grid Model)
        pars.add_argument("--font-family", type=str, dest="font_family", default="Arial")

        # Paramètres - Onglet 2 (Auto Metrics)
        pars.add_argument("--padding", type=float, dest="padding", default=0.5)

        # Paramètres - Onglet 3 (Export SVG Font)
        #pars.add_argument("--font-name",    type=str, dest="font_name",    default="My_HersheyCustom")
        pars.add_argument("--output-file",  type=str, dest="output_path",  default="./")
        pars.add_argument("--units-per-em", type=int, dest="units_per_em", default=1000)
        pars.add_argument("--ascent",       type=int, dest="ascent",       default=800)
        pars.add_argument("--horiz-adv-x",  type=int, dest="horiz_adv_x",  default=500)
        pars.add_argument("--descent",      type=int, dest="descent",      default=-200)

    def effect(self):
        tab = self.options.active_tab
        self.options.font_name= f'Hershley{self.options.font_family}'
        if tab == "tab_grid":
            sub_effect = GlyphGridEffect()
        elif tab == "tab_metrics":
            sub_effect = AutoMetrics()
        elif tab == "tab_export":
            sub_effect = ExportSVGFont()
        else:
            return

        # Transmission du document et des options au sous-effet
        sub_effect.document = self.document
        sub_effect.options = self.options
        sub_effect.effect()

if __name__ == "__main__":
    GlyphsToolkit().run()
