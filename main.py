# coding: shift-jis

from hwx import simlab, gui
import os, sys
import tkinter as tk
import importlib

## global variable
SRC_DIR = (os.path.dirname(os.path.realpath(__file__)))
IMAGE_DIR = (os.path.join(SRC_DIR, 'images'))
ROOT = None

gui.addResourcePath(SRC_DIR)
if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)
os.chdir(SRC_DIR)

## local import
import maintool

## menu functions
def LaunchMainTool():
    global ROOT
    if Exists(ROOT):
        ROOT.deiconify()
        return

    importlib.reload(maintool)

    ROOT = tk.Tk()
    app = maintool.MainTool(ROOT)
    app.mainloop()

def Exists(win):
    try:
        if ROOT == None:
            return False
        return ROOT.winfo_exists()
    except:
        return False

LaunchMainTool()
# ## adds menus to SimLab
# page = gui.RibbonPage (text="Automation", name='demopage'+'99999', after='Scripting')
# group1 = gui.SpriteActionGroup (page, text="Welder")
# gui.SpriteAction(group1, tooltip="Automation", icon=(os.path.join(IMAGE_DIR, 'icon.png')), command=LaunchMainTool)