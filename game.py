
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="4K 3D Car Racing",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    iframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #050505;
    font-family: Arial, sans-serif;
}

#game {
    width: 100vw;
    height: 100vh;
    display: block;
}

#hud {
    position: fixed;
    top: 20px;
    left: 20px;
    color: white;
    z-index: 10;
    background: rgba(0,0,0,.45);
    backdrop-filter: blur(8px);
    padding: 15px 20px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,.2);
}

.speed {
    font-size: 32px;
    font-weight: bold;
}

.info {
    font-size: 14px;
    opacity: .8;
    margin-top: 5px;
}

#startScreen {
    position: fixed;
    inset: 0;
    z-index: 20;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    background:
        radial-gradient(circle at center, rgba(20,80,120,.35), #020305 70%);
}

#startScreen h1 {
    font-size: clamp(45px, 7vw, 100px);
    letter-spacing: 8px;
    text-shadow: 0 0 30px #00bfff;
}

#startScreen p {
    margin: 15px;
    font-size: 18px;
    opacity: .8;
}

button {
    margin-top: 20px;
    padding: 16px 45px;
    font-size: 20px;
    font-weight: bold;
    color: white;
    background: linear-gradient(135deg,#008cff,#00d4ff);
    border: none;
    border-radius: 40px;
    cursor: pointer;
    box-shadow: 0 0 30px rgba(0,180,255,.5);
}

button:hover {
    transform: scale(1.05);
}

#gameOver {
    position: fixed;
    inset: 0;
    z-index: 30;
    display: none;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background: rgba(0,0,0,.72);
    color: white;
}

#gameOver h2 {
    font-size: 65px;
    color: #ff3030;
}
</style>
</head>

<body>

<div id="hud">
    <div class="speed">
        <span id="speed">0</span> KM/H
    </div>
    <div class="info">
        Distance: <span id="distance">0</span> m
    </div>
    <div class="info">
        Controls: W/A/S/D or Arrow Keys
    </div>
</div>

<div id="startScreen">
    <h1>ROAD RUSH</h1>
    <p>Ultra 3D Racing Experience</p>
    <button onclick="startGame()">START RACE</button>
</div>

<div id="gameOver">
    <h2>CRASH!</h2>
    <p id="finalScore">Distance: 0m</p>
    <button onclick="location.reload()">RESTART</button>
</div>

<canvas id="game"></canvas>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>

<script>

let scene, camera, renderer;
let car;
let road;
let trees = [];
let buildings = [];
let traffic = [];

let running = false;
let speed = 0;
let distance = 0;

let keys = {};

let carX = 0;
let targetX = 0;

const ROAD_WIDTH = 12;

document.addEventListener("keydown", e => {
    keys[e.key.toLowerCase()] = true;

    if (
        ["arrowup","arrowdown","arrowleft","arrowright"," "]
        .includes(e.key.toLowerCase())
    ) {
        e.preventDefault();
    }
});

document.addEventListener("keyup", e => {
    keys[e.key.toLowerCase()] = false;
});


function createCar() {

    const group = new THREE.Group();

    // Body
    const bodyGeo = new THREE.BoxGeometry(2.2, .55, 4.2);

    const bodyMat = new THREE.MeshStandardMaterial({
        color: 0x006cff,
        metalness: .85,
        roughness: .18
    });

    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = .7;
    group.add(body);


    // Hood
    const hoodGeo = new THREE.BoxGeometry(2.0,.25,1.4);

    const hood = new THREE.Mesh(
        hoodGeo,
        new THREE.MeshStandardMaterial({
            color: 0x0050d0,
            metalness: .8,
            roughness: .15
        })
    );

    hood.position.set(0,1.02,-1.15);
    group.add(hood);


    // Cabin
    const cabinGeo = new THREE.BoxGeometry(1.65,.7,1.7);

    const cabinMat = new THREE.MeshStandardMaterial({
        color: 0x07101c,
        metalness: .3,
        roughness: .1
    });

    const cabin = new THREE.Mesh(cabinGeo,cabinMat);
    cabin.position.set(0,1.12,.35);
    group.add(cabin);


    // Spoiler
    const spoiler = new THREE.Mesh(
        new THREE.BoxGeometry(2.1,.12,.45),
        new THREE.MeshStandardMaterial({
            color: 0x111111,
            metalness: .8
        })
    );

    spoiler.position.set(0,1.2,1.95);
    group.add(spoiler);


    // Wheels
    const wheelGeo = new THREE.CylinderGeometry(
        .48,.48,.35,32
    );

    const wheelMat = new THREE.MeshStandardMaterial({
        color: 0x080808,
        roughness: .5
    });

    const positions = [
        [-1.08,.48,-1.35],
        [1.08,.48,-1.35],
        [-1.08,.48,1.35],
        [1.08,.48,1.35]
    ];

    positions.forEach(p => {

        const wheel = new THREE.Mesh(
            wheelGeo,
            wheelMat
        );

        wheel.rotation.z = Math.PI/2;

        wheel.position.set(
            p[0],
            p[1],
            p[2]
        );

        group.add(wheel);
    });


    // Headlights
    const lightGeo = new THREE.BoxGeometry(.38,.18,.1);

    const lightMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0xffffff,
        emissiveIntensity: 5
    });

    [-.65,.65].forEach(x => {

        const light = new THREE.Mesh(
            lightGeo,
            lightMat
        );

        light.position.set(x,.82,-2.13);
        group.add(light);

    });


    group.position.y = 0;
    scene.add(group);

    return group;
}


function createRoad() {

    const roadGeo = new THREE.PlaneGeometry(
        ROAD_WIDTH,
        3000
    );

    const roadMat = new THREE.MeshStandardMaterial({
        color: 0x292929,
        roughness: .95
    });

    road = new THREE.Mesh(
        roadGeo,
        roadMat
    );

    road.rotation.x = -Math.PI/2;
    road.position.z = -1000;

    scene.add(road);


    // Road borders
    const borderMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: .6
    });

    [-6.2,6.2].forEach(x => {

        const border = new THREE.Mesh(
            new THREE.BoxGeometry(.25,.03,3000),
            borderMat
        );

        border.position.set(x,.03,-1000);

        scene.add(border);
    });


    // Center dashed line
    for(let i=0;i<150;i++){

        const line = new THREE.Mesh(
            new THREE.BoxGeometry(.18,.035,8),
            new THREE.MeshStandardMaterial({
                color: 0xffffcc
            })
        );

        line.position.set(
            0,
            .04,
            -i*20
        );

        scene.add(line);
    }
}


function createTree(x,z) {

    const group = new THREE.Group();

    const trunk = new THREE.Mesh(
        new THREE.CylinderGeometry(.18,.25,2,12),
        new THREE.MeshStandardMaterial({
            color: 0x6b3b20
        })
    );

    trunk.position.y = 1;

    group.add(trunk);


    const leaves = new THREE.Mesh(
        new THREE.SphereGeometry(
            1.2,
            16,
            16
        ),
        new THREE.MeshStandardMaterial({
            color: 0x075d26,
            roughness: .9
        })
    );

    leaves.position.y = 2.3;

    group.add(leaves);

    group.position.set(x,0,z);

    scene.add(group);

    trees.push(group);
}


function createBuilding(x,z) {

    const h = 4 + Math.random()*12;

    const building = new THREE.Mesh(
        new THREE.BoxGeometry(
            3 + Math.random()*4,
            h,
            3 + Math.random()*4
        ),
        new THREE.MeshStandardMaterial({
            color: 0x263342,
            roughness: .8
        })
    );

    building.position.set(
        x,
        h/2,
        z
    );

    scene.add(building);

    buildings.push(building);
}


function createTrafficCar(z) {

    const group = new THREE.Group();

    const body = new THREE.Mesh(
        new THREE.BoxGeometry(1.8,.6,3.5),
        new THREE.MeshStandardMaterial({
            color: Math.random()*0xffffff,
            metalness:.7,
            roughness:.25
        })
    );

    body.position.y = .65;

    group.add(body);


    const cabin = new THREE.Mesh(
        new THREE.BoxGeometry(1.4,.6,1.5),
        new THREE.MeshStandardMaterial({
            color:0x111822,
            roughness:.1
        })
    );

    cabin.position.set(0,1.05,.25);

    group.add(cabin);


    group.position.set(
        [-4,-2,2,4][Math.floor(Math.random()*4)],
        0,
        z
    );

    scene.add(group);

    traffic.push(group);
}


function createEnvironment() {

    for(let i=0;i<80;i++){

        let z = -i*40 - 20;

        createTree(
            -9 - Math.random()*5,
            z
        );

        createTree(
            9 + Math.random()*5,
            z
        );

        if(i % 3 === 0){

            createBuilding(
                -16 - Math.random()*8,
                z
            );

            createBuilding(
                16 + Math.random()*8,
                z-15
            );
        }
    }


    for(let i=0;i<12;i++){
        createTrafficCar(
            -80 - i*100
        );
    }
}


function setup() {

    scene = new THREE.Scene();

    scene.background = new THREE.Color(0x8bc7ff);

    scene.fog = new THREE.Fog(
        0x8bc7ff,
        80,
        500
    );


    camera = new THREE.PerspectiveCamera(
        65,
        window.innerWidth/window.innerHeight,
        .1,
        1000
    );

    camera.position.set(
        0,
        4.2,
        8
    );


    renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById("game"),
        antialias: true,
        powerPreference: "high-performance"
    });

    renderer.setPixelRatio(
        Math.min(window.devicePixelRatio,2)
    );

    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    );

    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type =
        THREE.PCFSoftShadowMap;


    // Sun
    const sun = new THREE.DirectionalLight(
        0xffffff,
        3
    );

    sun.position.set(
        -50,
        100,
        50
    );

    sun.castShadow = true;

    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;

    scene.add(sun);


    // Ambient
    const ambient = new THREE.HemisphereLight(
        0xbfe7ff,
        0x203020,
        1.5
    );

    scene.add(ambient);


    createRoad();

    car = createCar();

    createEnvironment();

    window.addEventListener(
        "resize",
        resize
    );

    animate();
}


function startGame() {

    document.getElementById(
        "startScreen"
    ).style.display = "none";

    running = true;

    speed = 80;
}


function crash() {

    running = false;

    document.getElementById(
        "gameOver"
    ).style.display = "flex";

    document.getElementById(
        "finalScore"
    ).innerText =
        "Distance: " +
        Math.floor(distance) +
        " meters";
}


function updateGame() {

    if(!running) return;


    // Acceleration
    if(keys["w"] || keys["arrowup"]){
        speed += .8;
    }
    else{
        speed -= .25;
    }


    if(keys["s"] || keys["arrowdown"]){
        speed -= 1;
    }


    speed = Math.max(
        30,
        Math.min(speed,260)
    );


    // Steering
    if(keys["a"] || keys["arrowleft"]){
        targetX -= .18;
    }

    if(keys["d"] || keys["arrowright"]){
        targetX += .18;
    }


    targetX = Math.max(
        -4.5,
        Math.min(targetX,4.5)
    );


    carX +=
        (targetX-carX)*.15;

    car.position.x = carX;


    // Camera follows car
    camera.position.x =
        carX * .25;

    camera.lookAt(
        carX*.2,
        1,
        -25
    );


    // Move world
    const movement =
        speed * .025;

    distance += movement;


    trees.forEach(obj => {

        obj.position.z += movement;

        if(obj.position.z > 20){
            obj.position.z -= 3200;
        }
    });


    buildings.forEach(obj => {

        obj.position.z += movement;

        if(obj.position.z > 30){
            obj.position.z -= 3200;
        }
    });


    traffic.forEach(obj => {

        obj.position.z += movement * 1.15;

        if(obj.position.z > 30){

            obj.position.z =
                -700 - Math.random()*600;

            obj.position.x =
                [-4,-2,2,4][
                    Math.floor(Math.random()*4)
                ];
        }


        // Collision
        const dx =
            Math.abs(obj.position.x-car.position.x);

        const dz =
            Math.abs(obj.position.z-car.position.z);

        if(dx < 1.5 && dz < 2.5){
            crash();
        }
    });


    document.getElementById(
        "speed"
    ).innerText = Math.floor(speed);

    document.getElementById(
        "distance"
    ).innerText = Math.floor(distance);
}


function animate() {

    requestAnimationFrame(animate);

    updateGame();

    renderer.render(
        scene,
        camera
    );
}


function resize() {

    camera.aspect =
        window.innerWidth/window.innerHeight;

    camera.updateProjectionMatrix();

    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    );
}


setup();

</script>
</body>
</html>
"""


components.html(
    game_html,
    height=900,
    scrolling=False
)
"""

st.components.v1.html(game_html, height=900, scrolling=False)
"""

# NOTE:
# The game is rendered inside the browser using Three.js.
# Streamlit handles the application shell while JavaScript
# handles the actual 3D game.


import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Car Racing", layout="wide")

components.html("""
<!DOCTYPE html>
<html>
<body style="margin:0;overflow:hidden">

<div id="hud" style="position:fixed;z-index:2;color:white;
font:25px Arial;padding:15px">
🏎️ Speed: <span id="s">0</span> |
🏁 Score: <span id="p">0</span>
</div>

<canvas id="c"></canvas>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>

<script>
const S=new THREE.Scene(), C=new THREE.PerspectiveCamera(
60,innerWidth/innerHeight,.1,1000);
const R=new THREE.WebGLRenderer({canvas:c,antialias:true});
R.setSize(innerWidth,innerHeight);
R.shadowMap.enabled=true;
S.background=new THREE.Color(0x87ceeb);

C.position.set(0,4,8);

S.add(new THREE.HemisphereLight(0xffffff,0x555555,2));

let sun=new THREE.DirectionalLight(0xffffff,3);
sun.position.set(-10,20,10);
S.add(sun);

// Road
let road=new THREE.Mesh(
new THREE.PlaneGeometry(12,1000),
new THREE.MeshStandardMaterial({color:0x292929}));
road.rotation.x=-Math.PI/2;
road.position.z=-450;
S.add(road);

// Car
let car=new THREE.Mesh(
new THREE.BoxGeometry(2,1,4),
new THREE.MeshStandardMaterial({
color:0x0066ff,metalness:.7,roughness:.2}));
car.position.y=.7;
S.add(car);

// Roof
let roof=new THREE.Mesh(
new THREE.BoxGeometry(1.5,.6,1.8),
new THREE.MeshStandardMaterial({color:0x111111}));
roof.position.y=1.4;
S.add(roof);

// Trees
let trees=[];
for(let i=0;i<50;i++){
 let t=new THREE.Group();
 let trunk=new THREE.Mesh(
  new THREE.CylinderGeometry(.15,.2,2),
  new THREE.MeshStandardMaterial({color:0x704020}));
 let leaf=new THREE.Mesh(
  new THREE.SphereGeometry(1.2),
  new THREE.MeshStandardMaterial({color:0x087522}));
 trunk.position.y=1;
 leaf.position.y=2.3;
 t.add(trunk,leaf);
 t.position.set(
  Math.random()>0.5?8:-8,0,-i*25);
 S.add(t); trees.push(t);
}

// Traffic
let cars=[];
for(let i=0;i<8;i++){
 let x=[-4,-2,2,4][Math.floor(Math.random()*4)];
 let a=new THREE.Mesh(
  new THREE.BoxGeometry(1.7,1,3),
  new THREE.MeshStandardMaterial({
   color:Math.random()*0xffffff}));
 a.position.set(x,.7,-50-i*80);
 S.add(a); cars.push(a);
}

let x=0,score=0,speed=1;
let keys={};

onkeydown=e=>keys[e.key.toLowerCase()]=1;
onkeyup=e=>keys[e.key.toLowerCase()]=0;

function game(){
 requestAnimationFrame(game);

 if(keys.a||keys.arrowleft)x-=.12;
 if(keys.d||keys.arrowright)x+=.12;

 x=Math.max(-4.5,Math.min(4.5,x));
 car.position.x=x;
 roof.position.x=x;

 let move=.8;

 trees.forEach(t=>{
  t.position.z+=move;
  if(t.position.z>10)t.position.z-=1250;
 });

 cars.forEach(a=>{
  a.position.z+=move*1.4;

  if(a.position.z>10){
   a.position.z=-600-Math.random()*400;
   a.position.x=[-4,-2,2,4][
    Math.floor(Math.random()*4)];
   score+=10;
  }

  if(Math.abs(a.position.x-x)<1.5 &&
     Math.abs(a.position.z)<3){
   score=0;
   alert("CRASH! Score: "+score);
   a.position.z=-500;
  }
 });

 document.getElementById("s").innerText=
  Math.floor(speed*100);
 document.getElementById("p").innerText=score;

 C.position.x=x*.25;
 C.lookAt(x*.2,1,-30);

 R.render(S,C);
}
game();
</script>

<p style="position:fixed;bottom:15px;left:20px;
color:white;font:16px Arial">
A/D or ←/→ = Steering
</p>

</body>
</html>
""",height=800)
