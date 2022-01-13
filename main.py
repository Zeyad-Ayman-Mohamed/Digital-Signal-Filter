# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and setti

from math import pi
import cmath
import json
from flask import Flask,jsonify, make_response, render_template, request
from flask import Flask, render_template
from flask_sock import Sock
from scipy.signal import butter, freqz
import matplotlib.pyplot as plt
from math import pi
import numpy as np
from scipy import signal
import cmath
import json
import pandas as pd

app = Flask(__name__)
sock = Sock(app)
def PolesAndZerosAdujesment(poles,zeros):
    Poles=[]
    Zeros=[]
    for i in range(0,len(poles)):
        Poles.append(complex(poles[i][0],poles[i][1]))
    for i in range(0,len(zeros)):
        Zeros.append(complex(zeros[i][0],zeros[i][1]))
    return Poles,Zeros
datatosite={
            "w": [],
            "H_dB": [],
            "phi":[],
            "w_allpass":[],
            "H_dB_allpass":[],
            "phi_allpass":[],
            "RealFiltered":[],
            "ImagineryFiltered":[],
            "RealFilteredAllPass":[],
            "ImaginaryFilteredAllPass" :[],
            "Time":[],
             "InputSignal":[]




        }
x = datatosite
loaded_data = pd.read_csv("ECG.csv")

InputSignal = loaded_data["filtered_ECG_mV"]
global start
start=0
FilteredSignal=[]
PointsNumber=10
wf =0.5
time = np.linspace(0,len(InputSignal),len(InputSignal))
time=time.tolist()
global EnteredSignal
global EnteredTime
EnteredSignal=InputSignal[start:start+PointsNumber]
EnteredTime=time[start:start+PointsNumber]
@app.route('/')
def index():
    return render_template('T5WebPage.html')


@sock.route('/echo')
def echo(sock):

    while True:

        data = sock.receive()
        data = json.loads(data)
        global start
        global EnteredSignal
        global EnteredTime

        zerosfromsite=data["value"]
        polesfromsite=data["value2"]
        wf=data["value5"]
        PointsNumber=data["value6"]
        print(wf)
        #print("poles",polesfromsite)
        f_s=360
        #AllPass Addition code
        AllPassSys = signal.TransferFunction([-wf, 1.0], [1.0, -wf])
        AllPassZeros = AllPassSys.zeros
        AllPassPoles = AllPassSys.poles
        ##########
        poles, zeros=PolesAndZerosAdujesment(polesfromsite, zerosfromsite)
        poles=poles+AllPassPoles
        zeros=zeros+AllPassZeros
        system = signal.ZerosPolesGain(zeros, poles, 1)
        system = system.to_tf()
        a = system.den
        b = system.num
        w, H = freqz(b, a, 4096)  # Calculate the frequency response
        w *= f_s / (2 * pi)  # Convert from rad/sample to Hz
        H_dB = 20 * np.log10(abs(H))
        phi = np.angle(H)  # Argument of H
        phi = np.unwrap(phi)  # Remove discontinuities
        phi *= 180 / pi
        #warp_factors=np.linspace(-0.99, 0.99, 5)
        #for i, wf in enumerate(warp_factors):
        WofAllPass, HofAllPass = signal.freqz([-wf, 1.0], [1.0, -wf])
        HofAllPassdB=20 * np.log10(abs(HofAllPass))
        AnglesofAllPass = np.unwrap(np.angle(HofAllPass))
        AllPassSys=signal.TransferFunction([-wf, 1.0], [1.0, -wf])
        AllPassZeros=AllPassSys.zeros
        AllPassPoles=AllPassSys.poles
        print(AllPassZeros)
        print(AllPassPoles)
        #dividenumber=len(InputSignal)/PointsNumber
        #InputSignalDivided = np.array_split(InputSignal, dividenumber)
        #TimeDivided= np.array_split(time, dividenumber)
        #for i in range(0, len(InputSignalDivided))  :
         #   for j in range(0, PointsNumber):
          #      FilteredSignal = signal.lfilter(b, a, InputSignal[i][j])
        flag=data["value4"]
        if(flag==1):
            EnteredSignal=InputSignal[start:start+PointsNumber]
            EnteredTime=time[start:start+PointsNumber]
            start = start + PointsNumber
        #print(EnteredSignal)
        FilteredSignal = signal.lfilter(b, a, EnteredSignal)

        FilteredSignalAllPass  = signal.lfilter([-wf, 1.0], [1.0, -wf], phi)
        for i in range(0,len(FilteredSignal)):
            x["RealFiltered"].append(FilteredSignal[i].real)
            x["ImagineryFiltered"].append(FilteredSignal[i].imag)
        for i in range(0,len(FilteredSignalAllPass)):
            x["RealFilteredAllPass"].append(FilteredSignalAllPass[i].real)
            x["ImaginaryFilteredAllPass"].append(FilteredSignalAllPass[i].imag)







        #we need to draw w with hdb, w with phi so we will put them in a dic send them
        #we need to draw w of all pass with hdb all pass and angle of all pass , put them in dic to send them
        #print("high")
        x["w"]=w.tolist()
        x["H_dB"]=H_dB.tolist()
        x["phi"]=phi.tolist()
        x["w_allpass"] = WofAllPass.tolist()
        x["H_dB_allpass"] = HofAllPassdB.tolist()
        x["phi_allpass"] = AnglesofAllPass.tolist()
        x["Time"]=EnteredTime
        x["InputSignal"]=EnteredSignal.tolist()
        #x["FilterdSignal"] =FilteredSignal.tolist()
        #x["FilteredSignalAllPass"] =FilteredSignalAllPass.tolist()
        #x["Time"] =TimeDivided.tolist()

        #print(x)
        #try:
        datasenttosite = json.dumps(x,indent = 12)
            #print("data",x)

        sock.send(datasenttosite)
        #except:
            #print("error")

