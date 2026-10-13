(()=>{'use strict';
const root=document.documentElement;
const read=(key,fallback,allowed)=>{try{const value=localStorage.getItem(key);return allowed.includes(value)?value:fallback}catch{return fallback}};
const save=(key,value)=>{try{localStorage.setItem(key,value)}catch{}};
root.dataset.theme=read('census-appearance','dark',['dark','light']);
root.dataset.vibe=read('census-vibe','pixel',['cartoon','calm','pixel','lab']);
document.addEventListener('DOMContentLoaded',()=>{
  for(const [id,key,values] of [['appearance','census-appearance',['dark','light']],['vibe','census-vibe',['cartoon','calm','pixel','lab']]]){
    const control=document.getElementById(id);control.value=root.dataset[id==='appearance'?'theme':id];
    control.addEventListener('change',()=>{if(values.includes(control.value)){root.dataset[id==='appearance'?'theme':id]=control.value;save(key,control.value);start()}});
  }
  const filter=document.getElementById('status-filter');
  if(filter)filter.addEventListener('change',()=>{let shown=0;const rows=document.querySelectorAll('#trial-table tbody tr');for(const row of rows){row.hidden=filter.value!=='all'&&row.dataset.status!==filter.value;if(!row.hidden)shown++}document.getElementById('filter-status').textContent=`${shown} of ${rows.length} planned trials shown. The denominator is unchanged.`});
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let paused=true,visible=true,worker=null,attempted=false;
  const canvas=document.getElementById('field');canvas.dataset.gpu='static';
  function fieldWorker(){
    let gl=null,program=null,frame=0,running=false,canvas=null;
    function stop(){if(frame)cancelAnimationFrame(frame);frame=0}
    function draw(now){if(!running||!gl)return;gl.uniform1f(gl.getUniformLocation(program,'time'),now/1000);gl.uniform2f(gl.getUniformLocation(program,'size'),canvas.width,canvas.height);gl.drawArrays(gl.TRIANGLES,0,6);frame=requestAnimationFrame(draw)}
    self.onmessage=event=>{
      if(event.data.canvas){
        canvas=event.data.canvas;
        try{
          gl=canvas.getContext('webgl2',{alpha:true,antialias:false});if(!gl)throw Error('WebGL2 unavailable');
          const shader=(type,source)=>{const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error('shader');return shader};
          program=gl.createProgram();
          gl.attachShader(program,shader(gl.VERTEX_SHADER,'#version 300 es\nin vec2 position;void main(){gl_Position=vec4(position,0.,1.);}'));
          gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'#version 300 es\nprecision mediump float;uniform float time;uniform vec2 size;out vec4 color;void main(){vec2 uv=gl_FragCoord.xy/size;vec2 grid=abs(fract(uv*vec2(64.,8.)+vec2(time*.025,0.))-.5);float dot=1.-smoothstep(.12,.18,length(grid));color=vec4(.55,.44,.72,dot*.65);}'));
          gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('program');gl.useProgram(program);
          const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
          const attr=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,2,gl.FLOAT,false,0,0);gl.viewport(0,0,canvas.width,canvas.height);
          self.postMessage('webgl2');
          canvas.addEventListener('webglcontextlost',()=>{running=false;stop();self.postMessage('static')});
        }catch{gl=null;self.postMessage('static')}
      }
      running=event.data.running;stop();if(running&&gl)frame=requestAnimationFrame(draw);
    };
  }
  function start(){
    const running=!paused&&!document.hidden&&!reduced.matches&&visible;
    if(running&&!worker&&!attempted&&canvas.transferControlToOffscreen&&typeof Worker==='function'){
      try{
        attempted=true;const url=URL.createObjectURL(new Blob(['('+fieldWorker.toString()+')()'],{type:'text/javascript'}));
        worker=new Worker(url);URL.revokeObjectURL(url);
        worker.onmessage=event=>{canvas.dataset.gpu=event.data;if(event.data==='static'){worker.terminate();worker=null}};
        worker.onerror=()=>{canvas.dataset.gpu='static';worker.terminate();worker=null};
        const offscreen=canvas.transferControlToOffscreen();worker.postMessage({canvas:offscreen,running},[offscreen]);
      }catch{if(worker)worker.terminate();worker=null;canvas.dataset.gpu='static'}
    }else if(worker)worker.postMessage({running});
  }
  document.getElementById('motion').addEventListener('click',event=>{paused=!paused;root.dataset.paused=String(paused);event.currentTarget.setAttribute('aria-pressed',String(paused));event.currentTarget.textContent=paused?'Resume motion':'Pause motion';start()});
  document.addEventListener('visibilitychange',()=>{root.dataset.paused=String(paused||document.hidden);start()});reduced.addEventListener('change',start);
  if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;start()}).observe(canvas);
  window.addEventListener('pagehide',()=>{if(worker)worker.terminate();worker=null});start();
});})();
