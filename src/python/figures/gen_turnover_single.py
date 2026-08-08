#!/usr/bin/env python3
"""
Generate single-column turnover figure (Fig 4) — clean, no internal legend.
"""
import warnings; from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt; import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIGURES_DIR = PROJECT_ROOT / "paper" / "clei2026" / "figures"
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"
BLUE, ORANGE, GRAY = "#1f77b4", "#ff7f0e", "#7f7f7f"
DPI = 300

plt.rcParams.update({"font.family":"serif","font.size":8,"axes.labelsize":9,
    "axes.titlesize":9,"xtick.labelsize":7,"ytick.labelsize":7,
    "legend.fontsize":7,"figure.dpi":100,"savefig.dpi":DPI,
    "savefig.bbox":"tight","figure.facecolor":"white","axes.facecolor":"white",
    "savefig.facecolor":"white","axes.spines.top":False,"axes.spines.right":False})

def load_mat_generations(p):
    from pymatreader import read_mat
    d=read_mat(str(p)); g=d.get("trace_generations",[])
    if isinstance(g,dict): g=[g]
    elif isinstance(g,np.ndarray): g=list(g)
    return g
def extract_trajectory(gens,key):
    v=[]; 
    for g in gens:
        if isinstance(g,dict) and key in g:
            x=g[key]
            if isinstance(x,(int,float,np.integer,np.floating)): v.append(float(x))
            else: v.append(np.nan)
        else: v.append(np.nan)
    return np.array(v)
def load_case(cid,algo):
    r=DATA_RAW/algo/cid
    if not r.exists(): return []
    pfx="IVF_" if algo=="ivf" else "SPEA2_"
    return [load_mat_generations(f) for f in sorted(r.glob(f"{pfx}*.mat")) if len(load_mat_generations(f))>5]

def main():
    FIGURES_DIR.mkdir(parents=True,exist_ok=True)
    cases=[("strong_pos_dtlz3_m2","DTLZ3 helpful",BLUE),
           ("neutral_wfg8_m2","WFG8 neutral",GRAY),
           ("hurts_wfg2_m3","WFG2 harmful",ORANGE)]
    fig,ax=plt.subplots(figsize=(3.4,2.0)); any_data=False
    for cid,label,color in cases:
        try:
            ivf=load_case(cid,"ivf"); spea2=load_case(cid,"spea2")
        except: continue
        if not ivf: continue
        any_data=True
        ng=min(len(t) for t in ivf)
        if spea2: ng=min(ng,min(len(t) for t in spea2))
        # IVF turnover only (solid). SPEA2 ratio ≈ 1.0, not needed.
        all_t=np.array([extract_trajectory(t,"turnover")[:ng] for t in ivf])
        mean_t=np.nanmean(all_t,axis=0)
        ax.plot(np.linspace(0,1,len(mean_t)),mean_t,color=color,lw=2.0,label=label)
    ax.axvline(x=0.2,color="black",ls="--",lw=1.0,alpha=0.75)
    ax.annotate("20%",xy=(0.2,0.98),xycoords=("data","axes fraction"),
                fontsize=7,ha="center",va="top",color="black",alpha=0.85)
    ax.axhline(y=0.216,color="black",ls=":",lw=1.0,alpha=0.75)
    ax.annotate(r"$\theta\approx 0.216$",xy=(1.0,0.216),
                xycoords=("axes fraction","data"),fontsize=7,ha="right",
                va="bottom",color="black",alpha=0.85)
    ax.set_xlabel("Fraction of total generations")
    ax.set_ylabel("Mean archive turnover")
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(True,alpha=0.25,lw=0.4)
    ax.legend(frameon=True,framealpha=0.85,edgecolor="lightgray",fontsize=7,
              loc="upper right",handlelength=1.2,handletextpad=0.5,
              borderpad=0.3,labelspacing=0.2)
    if any_data:
        fig.tight_layout(pad=0.5)
        for ext in ["pdf","png"]:
            p=FIGURES_DIR/f"fig4_turnover.{ext}"
            fig.savefig(p,format=ext,bbox_inches="tight",dpi=DPI if ext=="png" else None)
            print(f"Saved: {p}")
    else: print("WARNING: No data.")
    plt.close(fig)
if __name__=="__main__":
    warnings.filterwarnings("ignore",category=RuntimeWarning); main()
