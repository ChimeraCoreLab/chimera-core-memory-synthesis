import os,wave;from pathlib import Path
b=Path(__file__).parent
n=[".","ChimeraEngine_V1_Genesis","ChimeraEngine_V2_Ultimate","ChimeraEngine_V3_Atomic_Cessation"]
m="\n".join([f"[{i}] {x}" for i,x in enumerate(n)])
s=int(input(f"{m}\n>> "))
p=b/n[s];t=0
if not p.exists():print(f"ERR:{p.name}_NOT_FOUND");exit()
fs=sorted([f for f in os.listdir(p) if f.endswith(".wav")])
print(f"'{p.absolute()}'")
for f in fs:
 try:
  with wave.open(str(p/f),'r') as w:
   d=w.getnframes()/w.getframerate()
   print(f"{f}:{d:.3f}s");t+=d
 except:print(f"{f}|ERR")
print(f"{len(fs)}F:{t:.3f}s")