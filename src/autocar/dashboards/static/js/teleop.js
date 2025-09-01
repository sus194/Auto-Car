const socket = io();
const dWS = document.getElementById('wsdot');

socket.on('connect', () => dWS.classList.add('on'));
socket.on('disconnect', () => dWS.classList.remove('on'));

const state = {
    turbo: false,
    kbd: { w: 0, a: 0, s: 0, d: 0, q: 0, e: 0 },
    auton: false,
    speed: 1.0
};

function computeAxes() {
    let ax = (state.kbd.d - state.kbd.a);
    let ay = (state.kbd.s - state.kbd.w);
    let rot = (state.kbd.e - state.kbd.q);
    const m = Math.max(1, Math.abs(ax) + Math.abs(ay));
    return { ax: ax / m, ay: ay / m, rot: rot, turbo: state.turbo };
}

function sendAxes() {
    if (state.auton) return;
    const { ax, ay, rot, turbo } = computeAxes();
    socket.emit('axes', { ax, ay, rot, turbo, speed: parseFloat(document.getElementById('spd').value) });
}

window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (k in state.kbd) { state.kbd[k] = 1; e.preventDefault(); sendAxes(); }
    if (k === 'shift') { state.turbo = true; e.preventDefault(); sendAxes(); }
});

window.addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (k in state.kbd) { state.kbd[k] = 0; sendAxes(); }
    if (k === 'shift') { state.turbo = false; sendAxes(); }
});

document.getElementById('stop').onclick = () => socket.emit('brake', {});
document.getElementById('auton').onclick = () => {
    state.auton = !state.auton;
    document.getElementById('auton_state').textContent = state.auton ? 'ON' : 'OFF';
    socket.emit('auton', { enabled: state.auton });
};

document.getElementById('apply').onclick = () => {
    const kp = parseFloat(document.getElementById('kp').value);
    const ki = parseFloat(document.getElementById('ki').value);
    const kd = parseFloat(document.getElementById('kd').value);
    socket.emit('pid', { kp, ki, kd });
};

document.getElementById('ota').onclick = () => socket.emit('ota', {});
document.getElementById('reboot').onclick = () => alert("Demo: wire this to a privileged endpoint on the Pi");
document.getElementById('spd').addEventListener('input', sendAxes);

// Mini map grid
const grid = document.getElementById('grid');
const W = 16, H = 10;
for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.onclick = () => {
            document.querySelectorAll('.cell.goal').forEach(el => el.classList.remove('goal'));
            cell.classList.add('goal');
            socket.emit('goal', { x: Math.floor(x * 2.5), y: Math.floor(y * 3.0) });
        };
        grid.appendChild(cell);
    }
}

document.getElementById('clear').onclick = () => {
    document.querySelectorAll('.cell.goal').forEach(el => el.classList.remove('goal'));
    socket.emit('goal', { x: -1, y: -1 });
};

// Gamepad polling
function pollGamepad() {
    const gp = navigator.getGamepads()[0];
    if (!gp || state.auton) return;
    const ax = gp.axes[0];
    const ay = gp.axes[1];
    const rot = gp.axes[2];
    const turbo = gp.buttons[0]?.pressed || false;
    if (Math.hypot(ax, ay, rot) > 0.1) {
        socket.emit('axes', { ax, ay, rot, turbo, speed: parseFloat(document.getElementById('spd').value) });
    } else {
        socket.emit('axes', { ax:0, ay:0, rot:0, turbo:false, speed:1.0 });
    }
}
setInterval(pollGamepad, 50);
