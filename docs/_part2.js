/* ============================================================
   Casos de Uso & UML — ISFT 189
   ============================================================ */
const $  = (s,r=document)=>r.querySelector(s);
const $$ = (s,r=document)=>[...r.querySelectorAll(s)];
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- pestañas ---------- */
$$('#tabs button').forEach(b=>b.onclick=()=>{
  $$('#tabs button').forEach(x=>x.classList.remove('on'));
  $$('section.tab').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');
  $('#tab-'+b.dataset.tab).classList.add('on');
  /* al mostrar una pestaña con visor, re-ajustar (estaba oculta y fit() medía 0) */
  const t=b.dataset.tab;
  requestAnimationFrame(()=>{
    try{
      if(t==='umlcu'  && !vCU.userMoved) vCU.fit();
      if(t==='umlcl'  && !vCL.userMoved) vCL.fit();
      if(t==='fichas') FICHAS.forEach(f=>{ const v=FLOWVIEWS[f.id]; if(v && !v.userMoved) v.fit(); });
    }catch(e){}
  });
});

/* ============================================================
   CATÁLOGO DE CASOS DE USO
   ============================================================ */
const PKGCODE = {'01':'PK-SEC','02':'PK-CUR','03':'PK-ALU','04':'PK-DOC',
                 '05':'PK-CURS','06':'PK-EXAM','07':'PK-DOCUM','08':'PK-CHAT'};
const PKGPILL = {'PK-SEC':'p1','PK-CUR':'p2','PK-ALU':'p3','PK-DOC':'p4',
                 'PK-CURS':'p5','PK-EXAM':'p6','PK-DOCUM':'p7','PK-CHAT':'p8'};
const RF = {
 'CU-01':'RF-041','CU-02':'RF-042','CU-03':'RF-043','CU-04':'RF-044',
 'CU-05':'RF-005','CU-06':'RF-006','CU-07':'RF-007','CU-08':'RF-008','CU-09':'RF-009','CU-10':'RF-010',
 'CU-11':'RF-001','CU-12':'RF-002','CU-13':'RF-003','CU-14':'RF-004','CU-15':'RF-018','CU-16':'RF-038',
 'CU-17':'RF-011','CU-18':'RF-012','CU-19':'RF-013','CU-20':'RF-014','CU-21':'RF-015','CU-22':'RF-016','CU-23':'RF-017',
 'CU-24':'RF-019, RF-021','CU-25':'RF-020, RF-021','CU-26':'RF-021','CU-27':'RF-022','CU-28':'RF-028',
 'CU-29':'RF-029','CU-30':'RF-030','CU-31':'RF-031','CU-32':'RF-032','CU-33':'RF-033','CU-34':'RF-037',
 'CU-35':'RF-023','CU-36':'RF-024, RF-026','CU-37':'RF-025, RF-026','CU-38':'RF-026','CU-39':'RF-027',
 'CU-40':'RF-034','CU-41':'RF-035','CU-42':'RF-036',
 'CU-43':'RF-039','CU-44':'RF-040',
 'CU-45':'RF-045','CU-46':'RF-046','CU-47':'RF-047','CU-48':'RF-047, RF-009, RF-021','CU-49':'RF-048'
};
const FICHA_IDS = ['CU-01','CU-11','CU-24','CU-35','CU-45'];

/* Construye el catálogo unificado desde los .puml parseados */
const CATALOG = (()=>{
  const byCode = new Map();
  DATA.cu.forEach(d=>{
    const prefix = d.file.slice(0,2);
    const pkg = PKGCODE[prefix] || 'PK-?';
    const pkgName = d.title || d.file;
    const alias2name = {}; d.actors.forEach(a=>alias2name[a.id]=a.name);
    const actorOf = {};
    d.actor_links.forEach(l=>{ if(!actorOf[l.to]) actorOf[l.to]=alias2name[l.from]||l.from; });
    d.usecases.forEach(u=>{
      if(!u.code) return;
      if(byCode.has(u.code)) return;           // evita el duplicado CU-38
      byCode.set(u.code,{
        code:u.code, name:u.name, pkg, pkgName,
        actor: actorOf[u.id] || 'Inclusión',
        rf: RF[u.code]||'—', file:d.file,
        ficha: FICHA_IDS.includes(u.code)
      });
    });
  });
  return [...byCode.values()].sort((a,b)=>parseInt(a.code.slice(3))-parseInt(b.code.slice(3)));
})();

/* ---------- tabla de paquetes (resumen) ---------- */
(()=>{
  const groups = new Map();
  CATALOG.forEach(c=>{ if(!groups.has(c.pkg)) groups.set(c.pkg,{name:c.pkgName,n:0}); groups.get(c.pkg).n++; });
  $('#pkgRows').innerHTML = [...groups].map(([code,g])=>
    `<tr><td><span class="pill ${PKGPILL[code]||'p1'}">${code}</span></td><td>${esc(g.name)}</td><td><b>${g.n}</b></td></tr>`).join('');
})();

/* ---------- filtros de la tabla ---------- */
(()=>{
  const q=$('#cuQ'), pk=$('#cuPkg'), ac=$('#cuActor'), of=$('#cuOnlyFicha'), cnt=$('#cuCount');
  const pkgs=[...new Set(CATALOG.map(c=>c.pkg))].sort();
  const pkgNames={}; CATALOG.forEach(c=>pkgNames[c.pkg]=c.pkgName);
  pk.innerHTML = '<option value="">Todos los paquetes</option>' +
    pkgs.map(p=>`<option value="${p}">${p} — ${esc(pkgNames[p])}</option>`).join('');
  const actors=[...new Set(CATALOG.map(c=>c.actor))].sort();
  ac.innerHTML = '<option value="">Todos los actores</option>' +
    actors.map(a=>`<option value="${esc(a)}">${esc(a)}</option>`).join('');

  function render(){
    const t=(q.value||'').toLowerCase().trim();
    const rows = CATALOG.filter(c=>{
      if(pk.value && c.pkg!==pk.value) return false;
      if(ac.value && c.actor!==ac.value) return false;
      if(of.checked && !c.ficha) return false;
      if(t && !(c.code.toLowerCase().includes(t) || c.name.toLowerCase().includes(t) ||
                c.rf.toLowerCase().includes(t) || c.actor.toLowerCase().includes(t))) return false;
      return true;
    });
    $('#cuRows').innerHTML = rows.map(c=>`<tr>
      <td class="ccode">${c.code}</td>
      <td>${esc(c.name)}</td>
      <td><span class="pill ${PKGPILL[c.pkg]||'p1'}">${c.pkg}</span> <span class="muted" style="font-size:11px">${esc(c.pkgName)}</span></td>
      <td>${esc(c.actor)}</td>
      <td class="rf">${esc(c.rf)}</td>
      <td>${c.ficha?'<span class="pill p5">sí</span>':'<span class="muted">—</span>'}</td>
    </tr>`).join('') || '<tr><td colspan="6" class="muted" style="text-align:center;padding:22px">Sin resultados</td></tr>';
    cnt.textContent = `${rows.length} de ${CATALOG.length} casos de uso`;
  }
  [q,pk,ac,of].forEach(el=>el.addEventListener('input',render));
  $('#cuReset').onclick=()=>{q.value='';pk.value='';ac.value='';of.checked=false;render();};
  render();
})();

/* ============================================================
   FICHAS + DIAGRAMAS DE FLUJO
   ============================================================ */
const FICHAS = [
{
 id:'CU-01', title:'Iniciar sesión', pkg:'PK-SEC', pkgName:'Seguridad y Acceso',
 actor:'Usuario', sec:'—', rf:'RF-041', inc:'—', ext:'—',
 desc:`Permite a cualquier persona con cuenta institucional autenticarse en la plataforma mediante su correo
 institucional y contraseña. Es el punto de entrada obligatorio a todas las funcionalidades del sistema y
 la base del esquema de control de acceso por roles (RNF-007): el rol determina qué menús y qué información
 quedan disponibles una vez dentro.`,
 pre:['Existe una cuenta registrada en la tabla <code>usuario</code> con estado <code>activo = true</code>.',
      'El usuario conoce su correo institucional y su contraseña.',
      'No hay una sesión abierta para ese usuario en el mismo navegador.'],
 post:['Se emite un <b>token JWT</b> firmado con el rol del usuario y una vigencia de 120 minutos.',
       'La sesión queda registrada con usuario, fecha y hora para auditoría (RNF-009).',
       'El usuario es redirigido al panel propio de su rol.'],
 steps:[
  {t:'start',text:'Inicio',next:1},
  {t:'proc',text:'El usuario accede al sistema y selecciona "Iniciar sesión"',next:2},
  {t:'proc',text:'Ingresa su correo institucional y su contraseña',next:3},
  {t:'proc',text:'Envía las credenciales al servidor',next:4},
  {t:'dec',text:'¿Credenciales válidas?',next:6,no:5},
  {t:'err',text:'Mostrar "Correo o contraseña incorrectos" y permanecer en la pantalla de acceso'},
  {t:'dec',text:'¿Cuenta activa?',next:8,no:7},
  {t:'err',text:'Mostrar "Cuenta inactiva" y derivar al Administrador/a'},
  {t:'proc',text:'Generar token JWT con identificador, rol y vigencia',next:9},
  {t:'proc',text:'Registrar el evento de acceso (auditoría)',next:10},
  {t:'end',text:'Sesión iniciada · Acceso al panel del rol'}
 ],
 alt:`Si el usuario olvidó su contraseña, desde la misma pantalla puede invocar el <b>CU-02: Recuperar contraseña</b>,
 que reemplaza el paso de validación por un flujo de verificación por correo electrónico.`,
 exc:`Tras 5 intentos fallidos consecutivos, el sistema bloquea temporalmente la cuenta y notifica al
 Administrador/a para evitar ataques de fuerza bruta.`,
 seq:{
  lifelines:[
   {id:'user',label:'Usuario',kind:'actor'},
   {id:'ui',label:'Interfaz web',stereo:'«boundary»'},
   {id:'api',label:'Servidor / API',stereo:'«control»'},
   {id:'db',label:'Base de datos',stereo:'«entity»'}
  ],
  msgs:[
   {k:'msg',from:'user',to:'ui',label:'Abrir "Iniciar sesión"',type:'sync'},
   {k:'msg',from:'user',to:'ui',label:'Ingresar correo y contraseña',type:'sync'},
   {k:'msg',from:'ui',to:'api',label:'POST /api/v1/auth/login',type:'sync'},
   {k:'msg',from:'api',to:'db',label:'Buscar usuario por correo',type:'sync'},
   {k:'alt',cond:'¿Credenciales válidas?',then:[
     {k:'alt',cond:'¿Cuenta activa?',then:[
       {k:'msg',from:'api',to:'api',label:'Generar token JWT firmado',type:'self'},
       {k:'msg',from:'api',to:'db',label:'Registrar acceso (auditoría)',type:'sync'},
       {k:'msg',from:'api',to:'ui',label:'200 · token JWT + rol',type:'reply'},
       {k:'msg',from:'ui',to:'user',label:'Redirigir al panel del rol',type:'reply'}
     ],else:[
       {k:'msg',from:'api',to:'ui',label:'403 · "Cuenta inactiva"',type:'reply'},
       {k:'msg',from:'ui',to:'user',label:'Derivar al Administrador/a',type:'reply'}
     ]}
   ],else:[
     {k:'msg',from:'api',to:'ui',label:'401 · "Correo o contraseña incorrectos"',type:'reply'},
     {k:'msg',from:'ui',to:'user',label:'Permanecer en la pantalla de acceso',type:'reply'}
   ]}
  ]
 }
},
{
 id:'CU-11', title:'Registrar alumno/a', pkg:'PK-ALU', pkgName:'Gestión de Alumnos y Legajos',
 actor:'Preceptor/a', sec:'—', rf:'RF-001', inc:'—', ext:'—',
 desc:`Permite al/a la preceptor/a dar de alta a un/a nuevo/a alumno/a en la institución, cargando su legajo,
 datos personales, datos de contacto y estado. El alta genera a su vez la cuenta de usuario asociada y
 habilita las posteriores inscripciones a carrera y a cursadas (CU-15, CU-24).`,
 pre:['El/a Preceptor/a tiene una sesión activa.',
      'No existe otro/a alumno/a con el mismo DNI ni con el mismo legajo.',
      'El ciclo lectivo correspondiente está abierto.'],
 post:['El registro queda persistido en la tabla <code>alumno</code> con estado <code>ACTIVO</code>.',
       'Se genera la cuenta de usuario vinculada con hash bcrypt de la contraseña provisoria.',
       'Se registra la fecha de alta para auditoría.'],
 steps:[
  {t:'start',text:'Inicio',next:1},
  {t:'proc',text:'El/a Preceptor/a ingresa al módulo de legajos de alumnos/as',next:2},
  {t:'proc',text:'Selecciona "Registrar alumno/a"',next:3},
  {t:'proc',text:'Completa DNI, apellido y nombre, fecha de nacimiento, email, teléfono y domicilio',next:4},
  {t:'dec',text:'¿Datos completos y válidos?',next:6,no:5},
  {t:'err',text:'Resaltar los campos con error y volver a solicitar la carga'},
  {t:'dec',text:'¿DNI ya registrado?',next:8,no:7},
  {t:'err',text:'Mostrar "Ya existe un legajo con ese DNI" y ofrecer abrir el existente'},
  {t:'proc',text:'Asignar legajo único y generar la cuenta de usuario con contraseña provisoria',next:9},
  {t:'proc',text:'Guardar en la tabla alumno con estado ACTIVO',next:10},
  {t:'end',text:'Alumno/a registrado · Legajo asignado correctamente'}
 ],
 alt:`Si el/a alumno/a ya figura en otra institución con documentación traspasada, el/a Preceptor/a registra
 el alta marcando el origen de la documentación en el campo de observaciones, sin alterar el flujo principal.`,
 exc:`Si el DNI ya existe, el sistema no duplica el registro: muestra el legajo existente y sugiere usar el
 <b>CU-12: Modificar datos de alumno/a</b> para actualizar la información.`,
 seq:{
  lifelines:[
   {id:'pre',label:'Preceptor/a',kind:'actor'},
   {id:'ui',label:'Interfaz web',stereo:'«boundary»'},
   {id:'api',label:'Servidor / API',stereo:'«control»'},
   {id:'db',label:'Base de datos',stereo:'«entity»'}
  ],
  msgs:[
   {k:'msg',from:'pre',to:'ui',label:'Abrir módulo de legajos',type:'sync'},
   {k:'msg',from:'pre',to:'ui',label:'Elegir «Registrar alumno/a»',type:'sync'},
   {k:'msg',from:'pre',to:'ui',label:'Cargar DNI, nombre y contacto',type:'sync'},
   {k:'alt',cond:'¿Datos completos y válidos?',then:[
     {k:'msg',from:'ui',to:'api',label:'POST /alumnos',type:'sync'},
     {k:'msg',from:'api',to:'db',label:'SELECT DNI en legajos',type:'sync'},
     {k:'alt',cond:'¿DNI disponible?',then:[
       {k:'msg',from:'api',to:'api',label:'Asignar legajo único',type:'self'},
       {k:'msg',from:'api',to:'db',label:'INSERT alumno (ACTIVO)',type:'sync'},
       {k:'msg',from:'api',to:'db',label:'INSERT usuario (bcrypt)',type:'sync'},
       {k:'msg',from:'api',to:'ui',label:'200 · legajo asignado',type:'reply'},
       {k:'msg',from:'ui',to:'pre',label:'Mostrar alta confirmada',type:'reply'}
     ],else:[
       {k:'msg',from:'api',to:'ui',label:'409 · "DNI ya registrado"',type:'reply'},
       {k:'msg',from:'ui',to:'pre',label:'Ofrecer abrir legajo existente',type:'reply'}
     ]}
   ],else:[
     {k:'msg',from:'ui',to:'pre',label:'Resaltar campos con error',type:'reply'}
   ]}
  ]
 },
},
{
 id:'CU-24', title:'Inscribirse a cursada de materia', pkg:'PK-CURS', pkgName:'Cursadas, Asistencias y Calificaciones',
 actor:'Alumno/a', sec:'—', rf:'RF-019, RF-021', inc:'CU-26', ext:'—',
 desc:`Permite al/a alumno/a inscribirse a la cursada de una materia dentro de los plazos habilitados por el
 período de inscripción. Antes de confirmar, el sistema ejecuta obligatoriamente la <b>inclusión CU-26</b>
 que valida las correlatividades exigidas por el plan de estudios (RF-021).`,
 pre:['El/a alumno/a tiene una carrera inscripta y activa.',
      'Existe un ciclo lectivo abierto con un período de inscripción a cursadas vigente.',
      'El/a alumno/a no tiene una inscripción activa a esa misma materia en ese ciclo.'],
 post:['Queda registrada la inscripción con condición <code>CURSANDO</code>.',
       'Se registra si la inscripción fue dentro o fuera de término.',
       'El/a alumno/a aparece en la nómina de la cátedra correspondiente (CU-21).'],
 steps:[
  {t:'start',text:'Inicio',next:1},
  {t:'proc',text:'El/a alumno/a consulta las materias disponibles en su plan de estudios',next:2},
  {t:'proc',text:'Selecciona la materia y confirma la inscripción',next:3},
  {t:'dec',text:'¿Período de inscripción vigente?',next:5,no:4},
  {t:'err',text:'Mostrar "Período cerrado" y derivar al/a Preceptor/a (CU-25 fuera de término)'},
  {t:'proc',text:'Invocar CU-26: validar correlatividades de cursada',next:6},
  {t:'dec',text:'¿Cumple todas las correlativas?',next:8,no:7},
  {t:'err',text:'Listar las materias faltantes con su tipo (para cursar / para rendir) y no inscribir'},
  {t:'proc',text:'Registrar la inscripción con condición CURSANDO',next:9},
  {t:'proc',text:'Actualizar la nómina y el porcentaje de la cátedra',next:10},
  {t:'end',text:'Inscripción a cursada confirmada'}
 ],
 alt:`El/a Preceptor/a puede registrar una inscripción <b>fuera de término</b> mediante el <b>CU-25</b>,
 que saltea la restricción de período pero conserva la validación de correlatividades.`,
 exc:`Si la materia ya está aprobada o tiene una inscripción activa, el sistema bloquea la nueva inscripción
 y muestra la condición actual del/a alumno/a en esa unidad curricular.`,
 seq:{
  lifelines:[
   {id:'alu',label:'Alumno/a',kind:'actor'},
   {id:'ui',label:'Interfaz web',stereo:'«boundary»'},
   {id:'api',label:'Servidor / API',stereo:'«control»'},
   {id:'v26',label:'Validador CU-26',stereo:'«control»'},
   {id:'db',label:'Base de datos',stereo:'«entity»'}
  ],
  msgs:[
   {k:'msg',from:'alu',to:'ui',label:'Abrir módulo de inscripción a cursadas',type:'sync'},
   {k:'msg',from:'alu',to:'ui',label:'Elegir materia del plan de estudios',type:'sync'},
   {k:'alt',cond:'¿Período de inscripción vigente?',then:[
     {k:'msg',from:'ui',to:'api',label:'POST /cursadas/inscribir',type:'sync'},
     {k:'msg',from:'api',to:'v26',label:'«include» validar correlatividades',type:'sync'},
     {k:'msg',from:'v26',to:'db',label:'SELECT correlativas del plan',type:'sync'},
     {k:'alt',cond:'¿Cumple todas las correlativas?',then:[
       {k:'msg',from:'v26',to:'api',label:'true · correlatividades OK',type:'reply'},
       {k:'msg',from:'api',to:'db',label:'INSERT inscripción (CURSANDO)',type:'sync'},
       {k:'msg',from:'api',to:'db',label:'UPDATE nómina de la cátedra',type:'sync'},
       {k:'msg',from:'api',to:'ui',label:'200 · inscripción registrada',type:'reply'},
       {k:'msg',from:'ui',to:'alu',label:'Mostrar "Inscripción a cursada confirmada"',type:'reply'}
     ],else:[
       {k:'msg',from:'v26',to:'api',label:'false · materias faltantes',type:'reply'},
       {k:'msg',from:'api',to:'ui',label:'409 · listar correlativas pendientes',type:'reply'},
       {k:'msg',from:'ui',to:'alu',label:'Mostrar faltantes y no inscribir',type:'reply'}
     ]}
   ],else:[
     {k:'msg',from:'api',to:'ui',label:'423 · "Período cerrado"',type:'reply'},
     {k:'msg',from:'ui',to:'alu',label:'Derivar al/a Preceptor/a (CU-25)',type:'reply'}
   ]}
  ]
 },
},
{
 id:'CU-35', title:'Programar mesa de examen final', pkg:'PK-EXAM', pkgName:'Exámenes Finales y Actas Oficiales',
 actor:'Preceptor/a', sec:'—', rf:'RF-023', inc:'—', ext:'—',
 desc:`Permite al/a preceptor/a crear una mesa de examen final indicando materia, fecha, horario, ciclo lectivo
 y el tribunal evaluador: docente titular y docente observador/a. El tribunal debe estar conformado por dos
 docentes distintos, restricción que garantiza una <code>CHECK</code> a nivel de base de datos.`,
 pre:['El/a Preceptor/a tiene una sesión activa.',
      'La materia pertenece a un plan de estudios vigente.',
      'Ambos docentes designados están dados de alta y activos.'],
 post:['La mesa queda registrada en <code>mesa_examen</code> con estado <code>ABIERTA</code>.',
       'Se habilita el período de inscripción a examen final asociado.',
       'Los alumnos/as elegibles pueden inscribirse (CU-36).'],
 steps:[
  {t:'start',text:'Inicio',next:1},
  {t:'proc',text:'El/a Preceptor/a ingresa al módulo de exámenes finales',next:2},
  {t:'proc',text:'Selecciona materia, fecha, horario y ciclo lectivo',next:3},
  {t:'proc',text:'Designa al docente titular y al docente observador/a',next:4},
  {t:'dec',text:'¿Son dos docentes distintos?',next:6,no:5},
  {t:'err',text:'Mostrar "El tribunal debe tener docentes distintos" y volver a la designación'},
  {t:'dec',text:'¿Fecha disponible y sin conflicto?',next:8,no:7},
  {t:'err',text:'Mostrar los horarios ocupados de esa materia y solicitar otra fecha'},
  {t:'proc',text:'Guardar la mesa con estado ABIERTA',next:9},
  {t:'proc',text:'Abrir la ventana de inscripción a examen final',next:10},
  {t:'end',text:'Mesa de examen programada y habilitada para inscripción'}
 ],
 alt:`Si aún no se definieron ambos docentes, el/a Preceptor/a puede dejar la mesa en estado provisional y
 completar el tribunal luego con el <b>CU-19: Asignar docente a materia</b>.`,
 exc:`No puede programarse una mesa para una materia sin ciclo lectivo abierto: el sistema bloquea la
 operación y solicita aperturar el ciclo con el <b>CU-10</b>.`,
 seq:{
  lifelines:[
   {id:'pre',label:'Preceptor/a',kind:'actor'},
   {id:'ui',label:'Interfaz web',stereo:'«boundary»'},
   {id:'api',label:'Servidor / API',stereo:'«control»'},
   {id:'db',label:'Base de datos',stereo:'«entity»'}
  ],
  msgs:[
   {k:'msg',from:'pre',to:'ui',label:'Abrir módulo de exámenes finales',type:'sync'},
   {k:'msg',from:'pre',to:'ui',label:'Cargar materia, fecha, horario y ciclo',type:'sync'},
   {k:'msg',from:'pre',to:'ui',label:'Designar docente titular y observador/a',type:'sync'},
   {k:'alt',cond:'¿Son dos docentes distintos?',then:[
     {k:'msg',from:'ui',to:'api',label:'POST /mesas',type:'sync'},
     {k:'msg',from:'api',to:'db',label:'SELECT disponibilidad de fecha y horario',type:'sync'},
     {k:'alt',cond:'¿Fecha sin conflicto?',then:[
       {k:'msg',from:'api',to:'db',label:'INSERT mesa_examen (ABIERTA)',type:'sync'},
       {k:'msg',from:'api',to:'db',label:'Abrir ventana de inscripción (CU-36)',type:'sync'},
       {k:'msg',from:'api',to:'ui',label:'200 · mesa programada',type:'reply'},
       {k:'msg',from:'ui',to:'pre',label:'Mostrar mesa confirmada',type:'reply'}
     ],else:[
       {k:'msg',from:'api',to:'ui',label:'409 · horarios ocupados',type:'reply'},
       {k:'msg',from:'ui',to:'pre',label:'Solicitar otra fecha',type:'reply'}
     ]}
   ],else:[
     {k:'msg',from:'ui',to:'pre',label:'Error: "El tribunal debe tener docentes distintos"',type:'reply'},
     {k:'msg',from:'pre',to:'ui',label:'Volver a la designación',type:'sync'}
   ]}
  ]
 },
},
{
 id:'CU-45', title:'Realizar consulta al asistente virtual', pkg:'PK-CHAT', pkgName:'Asistente Virtual / Chatbot',
 actor:'Usuario', sec:'Alumno/a, Docente, Preceptor/a, Administrador/a', rf:'RF-045',
 inc:'CU-46, CU-47, CU-49', ext:'CU-48',
 desc:`Permite a los/as usuarios/as plantear consultas en lenguaje natural al chatbot integrado en la
 plataforma. La respuesta se construye mediante una búsqueda híbrida sobre la base de datos (RAG) y
 sobre las tablas académicas, ejecutando tres inclusiones obligatorias: validación de permisos (CU-46),
 recuperación de información (CU-47) y registro de la conversación (CU-49).`,
 pre:['El/a usuario/a tiene una sesión activa con token JWT válido.',
      'Existe al menos un documento indexado o datos académicos cargados.'],
 post:['La respuesta se emite junto con las fuentes utilizadas.',
       'Queda registrada la consulta con usuario, fecha y hora (RF-048).',
       'La información entregada está acotada al rol del/a usuario/a (RF-046).'],
 steps:[
  {t:'start',text:'Inicio',next:1},
  {t:'proc',text:'El/a usuario/a escribe su consulta en lenguaje natural',next:2},
  {t:'proc',text:'La consulta se envía al endpoint /api/v1/chat/',next:3},
  {t:'proc',text:'Incluir CU-46: validar rol y permisos de consulta',next:4},
  {t:'dec',text:'¿Tiene permiso para esa información?',next:6,no:5},
  {t:'err',text:'Responder "No tiene permisos para consultar esa información" según el rol'},
  {t:'proc',text:'Incluir CU-47: recuperar información de la base de datos (RAG + tools)',next:7},
  {t:'proc',text:'Componer la respuesta citando las fuentes recuperadas',next:8},
  {t:'proc',text:'Incluir CU-49: registrar la conversación (usuario, fecha, hora)',next:9},
  {t:'end',text:'Respuesta entregada al/a usuario/a'}
 ],
 alt:`Desde el <b>CU-48: Consultar correlatividades de una materia</b> se dispara este flujo mediante una
 <code>&lt;&lt;extend&gt;&gt;</code>, inyectando un parámetro de materia que acota la búsqueda.`,
 exc:`Si el proveedor LLM no responde, el sistema devuelve la información recuperada por similitud
 vectorial sin síntesis, dejando constancia del fallo en la auditoría.`,
 seq:{
  lifelines:[
   {id:'user',label:'Usuario',kind:'actor'},
   {id:'ui',label:'Interfaz web',stereo:'«boundary»'},
   {id:'api',label:'Servidor / API',stereo:'«control»'},
   {id:'db',label:'Base de datos',stereo:'«entity»'},
   {id:'llm',label:'Proveedor LLM',stereo:'«control»'}
  ],
  msgs:[
   {k:'msg',from:'user',to:'ui',label:'Escribir consulta en lenguaje natural',type:'sync'},
   {k:'msg',from:'ui',to:'api',label:'POST /api/v1/chat/',type:'sync'},
   {k:'msg',from:'api',to:'db',label:'«include» CU-46: validar rol y permisos',type:'sync'},
   {k:'alt',cond:'¿Tiene permiso para esa información?',then:[
     {k:'msg',from:'db',to:'api',label:'true · permisos OK',type:'reply'},
     {k:'msg',from:'api',to:'db',label:'«include» CU-47: recuperar datos (RAG + tools)',type:'sync'},
     {k:'msg',from:'db',to:'api',label:'contexto académico + fuentes',type:'reply'},
     {k:'msg',from:'api',to:'llm',label:'Generar respuesta con el contexto',type:'sync'},
     {k:'msg',from:'llm',to:'api',label:'respuesta sintetizada',type:'reply'},
     {k:'msg',from:'api',to:'db',label:'«include» CU-49: registrar conversación',type:'sync'},
     {k:'msg',from:'api',to:'ui',label:'200 · respuesta + fuentes',type:'reply'},
     {k:'msg',from:'ui',to:'user',label:'Mostrar respuesta citando fuentes',type:'reply'}
   ],else:[
     {k:'msg',from:'api',to:'ui',label:'403 · "Sin permisos para esa información"',type:'reply'},
     {k:'msg',from:'ui',to:'user',label:'Responder según el rol del usuario',type:'reply'}
   ]}
  ]
 }
}];

/* ---------- render de fichas ---------- */
function renderFichas(){
  $('#fichas').innerHTML = FICHAS.map(f=>`
  <article class="ficha">
    <div class="head">
      <span class="id">${f.id}</span>
      <h3>${esc(f.title)}</h3>
      <span class="pill ${PKGPILL[f.pkg]}">${f.pkg}</span>
    </div>
    <div class="body">
      <div class="fmeta">
        <div><label>Paquete funcional</label><span>${esc(f.pkgName)}</span></div>
        <div><label>Actor primario</label><span>${esc(f.actor)}</span></div>
        <div><label>Actores secundarios</label><span>${esc(f.sec)}</span></div>
        <div><label>Requisitos</label><span class="rf">${esc(f.rf)}</span></div>
        <div><label>Incluye a</label><span>${esc(f.inc)}</span></div>
        <div><label>Extiende a</label><span>${esc(f.ext)}</span></div>
      </div>

      <h4 class="fh">Descripción</h4>
      <p class="desc">${f.desc.replace(/\s+/g,' ')}</p>

      <h4 class="fh">Precondiciones</h4>
      <ol class="flow">${f.pre.map(p=>`<li>${p}</li>`).join('')}</ol>

      <h4 class="fh">Postcondiciones</h4>
      <ol class="flow">${f.post.map(p=>`<li>${p}</li>`).join('')}</ol>

      <h4 class="fh">Flujo principal</h4>
      <ol class="flow">${f.steps.filter(s=>s.t!=='err').map((s,i)=>`<li><b>Paso ${i+1}.</b> ${esc(s.text)}</li>`).join('')}</ol>

      <h4 class="fh">Flujo alternativo</h4>
      <div class="alt"><b>Alternativo:</b> ${f.alt}</div>

      <h4 class="fh">Flujo de excepción</h4>
      <div class="exc"><b>Excepción:</b> ${f.exc}</div>

      <h4 class="fh">Diagrama de secuencia</h4>
      <div class="box" style="border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fbfcfe">
        <div class="vtoolbar" style="border-bottom:1px solid var(--line)">
          <span style="font-size:12px;color:var(--muted);font-weight:600">${f.id} — ${esc(f.title)}</span>
          <span class="hint" style="margin-left:auto;font-size:11.5px;color:var(--muted)">arrastrá el diagrama para desplazarlo · rueda = zoom</span>
          <button class="btn" data-flow="${f.id}" data-act="fit">⛶ Ajustar</button>
        </div>
        <div class="stage" id="stage-${f.id}" style="height:470px;background-size:20px 20px">
          <div class="layer" id="layer-${f.id}"><svg class="canvas" id="svg-${f.id}" width="6000" height="4000"></svg></div>
        </div>
        <div class="legend">
          <span><span class="pill p1">Síncrono (llamada)</span></span>
          <span><span class="pill p8">Respuesta</span></span>
          <span><span class="pill p5">Marco alt / else</span></span>
          <span><span class="pill" style="background:#e3f2fd;color:#1565c0">«boundary» «control» «entity»</span></span>
        </div>
      </div>
    </div>
  </article>`).join('');
}
renderFichas();

/* ---------- layout + render de diagramas de secuencia ---------- */
function wrap(text,max){
  const words=String(text).split(/\s+/); const lines=[]; let cur='';
  words.forEach(w=>{ if((cur+' '+w).trim().length>max){ if(cur)lines.push(cur); cur=w; } else cur=(cur+' '+w).trim(); });
  if(cur)lines.push(cur); return lines.length?lines:[''];
}

/* quita los marcos alt: conserva solo la rama "then" del flujo normal */
function stripAlts(msgs){
  return (msgs||[]).flatMap(it=>{
    if(it.k==='alt') return stripAlts(it.then||[]);
    return [it];
  });
}

function buildSeq(f, mode){
  const svg=document.getElementById('svg-'+f.id);
  if(!svg || !f.seq) return null;
  const seq = mode==='normal' ? Object.assign({},f.seq,{msgs:stripAlts(f.seq.msgs)}) : f.seq;
  const LL=seq.lifelines, n=LL.length;
  const GAPX=230, PADX=110, RIGHT=290, TOP=80, ROW=36, SELF=48, FST=46, ELST=30;
  const X=i=>PADX+i*GAPX;
  const W=PADX+(n-1)*GAPX+RIGHT;
  const li=x=>LL.findIndex(l=>l.id===x);

  /* ---- pase 1: posiciones verticales (recursivo para marcos alt) ---- */
  function walk(items,y){
    const out=[]; let cy=y;
    for(const it of items){
      if(it.k==='msg'){ out.push({t:'msg',y:cy,it}); cy += it.type==='self'?SELF:ROW; }
      else if(it.k==='alt'){
        const th=walk(it.then||[], cy+FST);
        let divY=null, els=[], el=null;
        if(it.else && it.else.length){ divY=th.y; el=walk(it.else, divY+ELST); els=el.out; }
        const bottom=(el?el.y:th.y)+12;
        out.push({t:'alt',y:cy,h:bottom-cy,divY,then:th.out,else:els,it});
        cy=bottom+20;
      }
    }
    return {y:cy,out};
  }
  const res=walk(seq.msgs, TOP+24);
  const H=Math.round(res.y+34);

  /* ---- activaciones ---- */
  const act=LL.map(()=>({min:1e9,max:-1e9}));
  (function each(nodes){ nodes.forEach(o=>{
    if(o.t==='msg'){
      const y1=o.it.type==='self'?o.y+SELF-16:o.y;
      [li(o.it.from),li(o.it.to)].forEach(i=>{ if(i<0) return; act[i].min=Math.min(act[i].min,o.y); act[i].max=Math.max(act[i].max,y1); });
    } else { each(o.then); each(o.else); }
  }); })(res.out);

  const P=[];

  /* ---- líneas de vida ---- */
  LL.forEach((l,i)=>P.push(`<line x1="${X(i)}" y1="76" x2="${X(i)}" y2="${H-18}" stroke="#94a3b8" stroke-width="1.6" stroke-dasharray="7 6"/>`));

  /* ---- barras de activación ---- */
  LL.forEach((l,i)=>{ if(act[i].max<0) return;
    P.push(`<rect x="${X(i)-5}" y="${act[i].min-13}" width="10" height="${act[i].max-act[i].min+26}" rx="3" fill="#dbeafe" stroke="#1565c0" stroke-width="1.4"/>`);
  });

  /* ---- marcos alt ---- */
  const FL=PADX-72, FR=X(n-1)+72;
  (function frames(nodes){ nodes.forEach(o=>{
    if(o.t!=='alt') return;
    const hdr='alt ['+o.it.cond+']', hw=Math.round(hdr.length*6.9+18);
    P.push(`<rect x="${FL}" y="${o.y}" width="${FR-FL}" height="${o.h}" rx="7" fill="#fffdf7" fill-opacity=".8" stroke="#f9a825" stroke-width="1.8"/>`);
    P.push(`<rect x="${FL+7}" y="${o.y+4}" width="${hw}" height="19" rx="4" fill="#fff8e1" stroke="#f9a825" stroke-width="1.4"/>`);
    P.push(`<text x="${FL+7+hw/2}" y="${o.y+17.5}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#5d4037">${esc(hdr)}</text>`);
    if(o.divY!=null){
      P.push(`<line x1="${FL}" y1="${o.divY}" x2="${FR}" y2="${o.divY}" stroke="#f9a825" stroke-width="1.5" stroke-dasharray="8 5"/>`);
      P.push(`<rect x="${FL+6}" y="${o.divY-9}" width="40" height="18" rx="4" fill="#fff8e1" stroke="#f9a825" stroke-width="1.2"/>`);
      P.push(`<text x="${FL+26}" y="${o.divY+4.5}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#e65100">else</text>`);
    }
    frames(o.then); frames(o.else);
  }); })(res.out);

  /* ---- mensajes ---- */
  (function msgs(nodes){ nodes.forEach(o=>{
    if(o.t==='alt'){ msgs(o.then); msgs(o.else); return; }
    if(o.t!=='msg') return;
    const it=o.it, a=li(it.from), b=li(it.to), ya=o.y;
    if(a<0||b<0) return;
    const lines=wrap(it.label,32);
    if(it.type==='self'){
      const x=X(a);
      P.push(`<path d="M${x},${ya+6} h54 v22 h-48" fill="none" stroke="#0d47a1" stroke-width="1.9" marker-end="url(#sqA-${f.id})"/>`);
      P.push(`<text x="${x+62}" y="${ya+22}" font-size="12" font-weight="600" fill="#0d47a1">${esc(it.label)}</text>`);
      return;
    }
    const x1=X(a), x2=X(b), dir=x2>x1?1:-1;
    const sx=x1+6*dir, ex=x2-6*dir, cx=(sx+ex)/2;
    const reply=it.type==='reply';
    P.push(`<line x1="${sx}" y1="${ya}" x2="${ex}" y2="${ya}" stroke="${reply?'#455a64':'#0d47a1'}" stroke-width="1.9" ${reply?'stroke-dasharray="7 5"':''} marker-end="url(#${reply?'sqR':'sqA'}-${f.id})"/>`);
    const yTop=lines.length>1? ya-21 : ya-7;
    P.push(`<text x="${cx}" y="${yTop}" text-anchor="middle" font-size="12" font-weight="600" fill="${reply?'#455a64':'#0d47a1'}">`+
      lines.map((l,k)=>`<tspan x="${cx}" dy="${k*14}">${esc(l)}</tspan>`).join('')+`</text>`);
  }); })(res.out);

  /* ---- encabezados (actores y objetos) ---- */
  LL.forEach((l,i)=>{
    const x=X(i);
    if(l.kind==='actor'){
      P.push(`<g>
        <circle cx="${x}" cy="18" r="8.5" fill="#fff" stroke="#0d47a1" stroke-width="2"/>
        <line x1="${x}" y1="27" x2="${x}" y2="43" stroke="#0d47a1" stroke-width="2"/>
        <line x1="${x-10}" y1="33" x2="${x+10}" y2="33" stroke="#0d47a1" stroke-width="2"/>
        <line x1="${x}" y1="43" x2="${x-10}" y2="56" stroke="#0d47a1" stroke-width="2"/>
        <line x1="${x}" y1="43" x2="${x+10}" y2="56" stroke="#0d47a1" stroke-width="2"/>
        <text x="${x}" y="71" text-anchor="middle" font-size="13.5" font-weight="700" fill="#0d47a1">${esc(l.label)}</text>
      </g>`);
    } else {
      P.push(`<g>
        <rect x="${x-97}" y="10" width="194" height="48" rx="9" fill="#e3f2fd" stroke="#1565c0" stroke-width="1.8"/>
        <text x="${x}" y="28" text-anchor="middle" font-size="10.5" fill="#1565c0">${esc(l.stereo||'')}</text>
        <text x="${x}" y="47" text-anchor="middle" font-size="13" font-weight="700" fill="#0d47a1">${esc(l.label)}</text>
      </g>`);
    }
  });

  svg.setAttribute('width',W);
  svg.setAttribute('height',H);
  svg.innerHTML=`<defs>
    <marker id="sqA-${f.id}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#0d47a1"/></marker>
    <marker id="sqR-${f.id}" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0.5 L9,4 L0,7.5" fill="none" stroke="#455a64" stroke-width="1.6" stroke-linecap="round"/></marker>
  </defs>
  <g id="fg-${f.id}">${P.join('')}</g>`;
  return {w:W,h:H};
}

/* ---------- visor genérico de flujos (pan/zoom) ---------- */
function attachFlowView(id){
  const stage=document.getElementById('stage-'+id), layer=document.getElementById('layer-'+id);
  if(!stage) return {fit(){},userMoved:false};
  let k=1,tx=40,ty=20,drag=null,userMoved=false;
  const apply=()=>layer.style.transform=`translate(${tx}px,${ty}px) scale(${k})`;
  stage.addEventListener('wheel',e=>{
    e.preventDefault();
    userMoved=true;
    const r=stage.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
    const nk=Math.min(2.4,Math.max(.25,k*(e.deltaY<0?1.12:.89)));
    tx=mx-(mx-tx)*(nk/k); ty=my-(my-ty)*(nk/k); k=nk; apply();
  },{passive:false});
  stage.addEventListener('pointerdown',e=>{
    drag={x:e.clientX,y:e.clientY,tx,ty}; stage.setPointerCapture(e.pointerId);
    stage.classList.add('grabbing');
  });
  stage.addEventListener('pointermove',e=>{
    if(!drag) return;
    const dx=e.clientX-drag.x, dy=e.clientY-drag.y;
    if(Math.abs(dx)+Math.abs(dy)>3) userMoved=true;
    tx=drag.tx+dx; ty=drag.ty+dy; apply();
  });
  const up=()=>{drag=null;stage.classList.remove('grabbing');};
  stage.addEventListener('pointerup',up); stage.addEventListener('pointercancel',up);
  const group=()=>document.getElementById('fg-'+id);   /* el <g> real del SVG */
  return {
    get userMoved(){ return userMoved; },
    fit(){
      const r=stage.getBoundingClientRect();
      if(!r.width||!r.height) return;                  /* pestaña oculta: no ajustar aún */
      const g=group(); if(!g||!g.getBBox) return;
      let b; try{ b=g.getBBox(); }catch(e){ return; }
      if(!b.width||!b.height) return;
      k=Math.min((r.width-70)/b.width,(r.height-70)/b.height,1.3);
      tx=(r.width-b.width*k)/2-b.x*k; ty=(r.height-b.height*k)/2-b.y*k;
      userMoved=false; apply();
    }
  };
}

/* ============================================================
   VISOR UML INTERACTIVO
   ============================================================ */
const COLORS = {actor:'#5c6bc0',uc:'#1e88e5',class:'#1e88e5',enum:'#8e24aa',note:'#f9a825'};

class Viewer{
  constructor(o){
    Object.assign(this,o);
    this.stage=$('#'+o.stageId); this.layer=$('#'+o.layerId); this.svg=$('#'+o.svgId);
    this.side=$('#'+o.sideId);
    this.k=1; this.tx=40; this.ty=30;
    this.userMoved=false;
    this.hidden=new Set(); this.flags={}; this.query='';
    this.layoutMode='hier';
    this.static=!!o.staticLayout;   /* diseño fijo: sin drag de nodos ni posiciones guardadas */
    this.nodes=[]; this.edges=[]; this.notes=[];
    this._bind();
  }

  /* ---------- datos ---------- */
  setCU(d){
    this.diagram=d.file; this.mode='cu';
    const n=[],e=[];
    d.actors.forEach(a=>n.push({id:'a:'+a.id,kind:'actor',name:a.name,x:0,y:0,w:110,h:86}));
    d.usecases.forEach(u=>n.push({id:'u:'+u.id,kind:'uc',name:(u.code?u.code+': ':'')+u.name,x:0,y:0,w:196,h:74}));
    d.actor_links.forEach(l=>e.push({from:'a:'+l.from,to:'u:'+l.to,kind:'assoc'}));
    d.uc_links.forEach(l=>e.push({from:'u:'+l.from,to:'u:'+l.to,kind:l.kind}));
    this.nodes=n; this.edges=e; this.notes=[]; this.title=d.title;
    this.hidden.clear(); this.query='';
    this.buildSide();
    this.reset(true);
  }
  setClases(d,group){
    this.diagram=(group||'')+'/'+d.file; this.mode='cl';
    const n=[],e=[];
    d.classes.forEach(c=>n.push({
      id:'c:'+c.name, kind:c.stereo==='enum'?'enum':'class', name:c.name,
      attrs:c.attrs||[], methods:c.methods||[], color:c.color, x:0,y:0,w:210,h:60
    }));
    d.rels.forEach(r=>e.push({from:'c:'+r.from,to:'c:'+r.to,kind:r.kind,cf:r.cf||'',ct:r.ct||'',label:r.label||''}));
    (d.notes||[]).forEach((nt,i)=>n.push({id:'n:'+i,kind:'note',target:nt.target? 'c:'+nt.target:'',name:nt.text,x:0,y:0,w:250,h:90}));
    this.nodes=n; this.edges=e; this.notes=[]; this.title=d.file;
    this.hidden.clear(); this.query='';
    this.buildSide();
    this.reset(true);
  }

  /* ---------- geometría ---------- */
  measure(){
    this.nodes.forEach(n=>{
      if(n.kind==='actor'){ n.w=112; n.h=92; return; }
      if(n.kind==='uc'){ n.w=Math.max(180,Math.min(250,Math.ceil(n.name.length*6.6)+34)); n.h=76; return; }
      if(n.kind==='note'){ n.w=264; n.h=Math.max(72,26+wrap(n.name,34).length*15); return; }
      const showA=this.flags.attrs!==false, showM=this.flags.methods!==false;
      const aw=Math.max(...n.attrs.map(a=>(a.name+' : '+(a.type||'')).length),10);
      const mw=Math.max(...n.methods.map(m=>(m.name+'('+m.params+')'+(m.ret?': '+m.ret:'')).length),10);
      n.w=Math.max(210,Math.ceil(Math.max(aw,mw)*6.35)+30);
      let h=34;
      if(showA) h+=n.attrs.length*15.5+6;
      if(showM) h+=n.methods.length*15.5+6;
      n.h=Math.max(46,h);
    });
  }

  /* ---------- auto-ordenado ---------- */
  auto(){
    this.measure();
    if(this.mode==='cu'){
      const acts=this.nodes.filter(n=>n.kind==='actor');
      const ucs =this.nodes.filter(n=>n.kind==='uc');
      const ah=Math.max(...acts.map(a=>a.h),90);
      const total=acts.length*ah; let y=-total/2;
      acts.forEach(a=>{ a.x=-420; a.y=y; y+=ah; });
      const cols=3, cw=290, rh=118;
      ucs.forEach((u,i)=>{ u.x=(i%cols)*cw; u.y=Math.floor(i/cols)*rh - (Math.ceil(ucs.length/cols)*rh)/2; });
    } else if(this.layoutMode==='grid'){
      const cs=this.nodes.filter(n=>n.kind==='class'||n.kind==='enum');
      const nt=this.nodes.filter(n=>n.kind==='note');
      const cols=Math.max(2,Math.ceil(Math.sqrt(cs.length)));
      cs.forEach((c,i)=>{ c.x=(i%cols)*320; c.y=Math.floor(i/cols)*230; });
      nt.forEach((n,i)=>{ const t=this.nodes.find(x=>x.id===n.target);
        if(t){ n.x=t.x+30; n.y=t.y+t.h+18; } else { n.x=(i%cols)*320+40; n.y=520+i*40; } });
    } else {
      this.layoutHier();
    }
    this.render(); this.fit();
  }

  /* ---------- layout jerárquico vertical ----------
     Raíz = clase sin padre (herencia/composición) con más conexiones
     (Usuario en el diagrama general). Desciende nivel por nivel vía BFS;
     los hijos quedan agrupados debajo de su padre (tidy tree horizontal). */
  layoutHier(){
    const cs=this.nodes.filter(n=>n.kind==='class'||n.kind==='enum');
    const nt=this.nodes.filter(n=>n.kind==='note');
    if(!cs.length) return;
    const byId=Object.fromEntries(this.nodes.map(n=>[n.id,n]));
    const idx=Object.fromEntries(cs.map((c,i)=>[c.id,i]));
    const nameTo=Object.fromEntries(cs.map(c=>[c.name,c]));

    /* grafo no dirigido entre clases: relaciones + tipos de atributos (rol : Rol) */
    const adj=new Map(cs.map(c=>[c.id,[]]));
    const link=(a,b)=>{
      if(!a||!b||a.id===b.id) return;                 /* sin self-loops en el árbol */
      if(!adj.get(a.id).includes(b.id)) adj.get(a.id).push(b.id);
      if(!adj.get(b.id).includes(a.id)) adj.get(b.id).push(a.id);
    };
    this.edges.forEach(e=>{
      const a=byId[e.from], b=byId[e.to];
      if(a&&b&&(a.kind==='class'||a.kind==='enum')&&(b.kind==='class'||b.kind==='enum')) link(a,b);
    });
    cs.forEach(c=>(c.attrs||[]).forEach(at=>{
      const t=(at.type||'').trim();
      if(nameTo[t]) link(c,nameTo[t]);               /* enum colgado de su clase */
    }));

    /* candidatos a raíz: sin padre por herencia/composición; gana el más conectado */
    const hasParent=new Set();
    this.edges.forEach(e=>{
      if(e.kind==='inherit') hasParent.add(e.from);      /* el hijo tiene padre */
      else if(e.kind==='compose') hasParent.add(e.to);   /* la parte tiene dueño */
    });
    const deg=id=>adj.get(id).length;
    const cands=cs.filter(c=>!hasParent.has(c.id))
                  .sort((a,b)=>deg(b.id)-deg(a.id)||idx[a.id]-idx[b.id]);

    /* BFS por componentes (raíz primero, luego el resto) */
    const level=new Map(), kids=new Map(cs.map(c=>[c.id,[]])), roots=[];
    const bfs=r=>{
      roots.push(r.id); level.set(r.id,0);
      const q=[r.id];
      while(q.length){
        const u=q.shift();
        adj.get(u).filter(v=>!level.has(v)).sort((a,b)=>idx[a]-idx[b])
          .forEach(v=>{ level.set(v,level.get(u)+1); kids.get(u).push(v); q.push(v); });
      }
    };
    cands.forEach(c=>{ if(!level.has(c.id)) bfs(c); });
    cs.forEach(c=>{ if(!level.has(c.id)) bfs(c); });

    /* tidy tree: ancho de subárbol y colocación de izquierda a derecha */
    const GAPX=54, width=new Map();
    const wOf=id=>{
      const ch=kids.get(id);
      if(!ch.length){ width.set(id,byId[id].w); return byId[id].w; }
      let s=0; ch.forEach((c,i)=>{ s+=wOf(c)+(i?GAPX:0); });
      const w=Math.max(s, byId[id].w+40);
      width.set(id,w); return w;
    };
    const place=(id,left)=>{
      const n=byId[id], ch=kids.get(id), W=width.get(id);
      n.x=left+W/2;
      if(!ch.length) return;
      let sum=0; ch.forEach((c,i)=>{ sum+=width.get(c)+(i?GAPX:0); });
      let cur=left+(W-sum)/2;
      ch.forEach(c=>{ place(c,cur); cur+=width.get(c)+GAPX; });
    };
    roots.forEach(r=>wOf(r));
    let cursor=0;
    roots.forEach(r=>{ place(r,cursor); cursor+=width.get(r)+170; });

    /* y por niveles, con hueco extra cuando cuelga una nota */
    const rows=[];
    cs.forEach(c=>{ const l=level.get(c.id); (rows[l]=rows[l]||[]).push(c); });
    const noteOf=new Map();
    nt.forEach(n=>{ if(n.target&&byId[n.target]) noteOf.set(n.target,n); });
    let y=0, prevH=0, prevExtra=0;
    rows.forEach((arr,l)=>{
      const h=Math.max(...arr.map(n=>n.h));
      if(l===0) y=h/2; else y+=prevH/2+prevExtra+115+h/2;
      arr.forEach(n=>n.y=y);
      prevH=h;
      prevExtra=Math.max(0,...arr.map(n=>{ const t=noteOf.get(n.id); return t?t.h+22:0; }));
    });

    /* notas debajo de su clase */
    nt.forEach(n=>{
      const t=n.target?byId[n.target]:null;
      if(t){ n.x=t.x; n.y=t.y+t.h/2+16+n.h/2; }
      else { n.x=0; n.y=y+260; }
    });

    /* centrar todo en x=0 */
    const all=cs.concat(nt);
    const mid=(Math.min(...all.map(n=>n.x-n.w/2))+Math.max(...all.map(n=>n.x+n.w/2)))/2;
    all.forEach(n=>n.x-=mid);
  }

  /* ---------- filtros ---------- */
  visible(n){
    if(this.hidden.has(n.id)) return false;
    if(this.query){
      const q=this.query.toLowerCase();
      const hay=(n.name||'').toLowerCase()+(n.kind==='note'?' '+n.target.toLowerCase():'');
      if(!hay.includes(q)) return false;
    }
    if(n.kind==='note' && this.flags.notes===false) return false;
    if((n.kind==='class'||n.kind==='enum') && this.flags.nodes===false) return false;
    return true;
  }
  edgeVisible(e){
    const a=this.nodes.find(n=>n.id===e.from), b=this.nodes.find(n=>n.id===e.to);
    if(!a||!b) return false;
    if(!this.visible(a)||!this.visible(b)) return false;
    if(e.kind==='include'&&this.flags.include===false) return false;
    if(e.kind==='extend'&&this.flags.extend===false) return false;
    if(e.kind==='assoc'&&this.mode==='cu'&&this.flags.links===false) return false;
    if(['inherit','assoc','compose','depend'].includes(e.kind)&&this.mode==='cl'&&this.flags[e.kind]===false) return false;
    if(this.query){
      const q=this.query.toLowerCase();
      const hit=(a.name||'').toLowerCase().includes(q)||(b.name||'').toLowerCase().includes(q);
      if(!hit) return false;
    }
    return true;
  }

  /* ---------- panel de filtros ---------- */
  buildSide(){
    const F=this.flags;
    const box=(t,inner)=>`<div class="box"><div style="font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;color:#64748b;font-weight:700;margin-bottom:6px">${t}</div>${inner}</div>`;
    let h=`<input class="search" id="${this.sideId}-q" placeholder="🔍 Buscar en el diagrama…" value="${esc(this.query)}">`;

    if(this.mode==='cu'){
      const acts=this.nodes.filter(n=>n.kind==='actor');
      const ucs =this.nodes.filter(n=>n.kind==='uc');
      h+=`<h5>Actores (${acts.length})</h5>`+acts.map(a=>
        `<label><input type="checkbox" data-id="${a.id}" ${this.hidden.has(a.id)?'':'checked'}><span class="swatch" style="background:${COLORS.actor}"></span>${esc(a.name)}</label>`).join('');
      h+=`<h5>Casos de uso (${ucs.length})</h5><div style="max-height:230px;overflow:auto">`+ucs.map(u=>
        `<label><input type="checkbox" data-id="${u.id}" ${this.hidden.has(u.id)?'':'checked'}><span class="swatch" style="background:${COLORS.uc}"></span><span style="font-size:11.8px">${esc(u.name)}</span></label>`).join('')+`</div>`;
      h+=`<h5>Relaciones</h5>`+
        `<label><input type="checkbox" data-flag="links" ${F.links===false?'':'checked'}>Asociación actor → CU</label>`+
        `<label><input type="checkbox" data-flag="include" ${F.include===false?'':'checked'}>&lt;&lt;include&gt;&gt;</label>`+
        `<label><input type="checkbox" data-flag="extend" ${F.extend===false?'':'checked'}>&lt;&lt;extend&gt;&gt;</label>`;
      h+=`<h5>Selección rápida</h5>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn" data-sel="all" style="font-size:11.5px;padding:5px 9px">Todo</button>
          <button class="btn" data-sel="none" style="font-size:11.5px;padding:5px 9px">Nada</button>
          <button class="btn" data-sel="actors" style="font-size:11.5px;padding:5px 9px">Solo actores</button>
          <button class="btn" data-sel="ucs" style="font-size:11.5px;padding:5px 9px">Solo CU</button>
        </div>`;
    } else {
      const cs=this.nodes.filter(n=>n.kind==='class'||n.kind==='enum');
      const nt=this.nodes.filter(n=>n.kind==='note');
      h+=box('Nodos',
        `<label><input type="checkbox" data-flag="nodes" ${F.nodes===false?'':'checked'}>Mostrar clases (${cs.length})</label>`+
        `<label><input type="checkbox" data-flag="attrs" ${F.attrs===false?'':'checked'}>Mostrar atributos</label>`+
        `<label><input type="checkbox" data-flag="methods" ${F.methods===false?'':'checked'}>Mostrar métodos</label>`+
        (nt.length?`<label><input type="checkbox" data-flag="notes" ${F.notes===false?'':'checked'}>Mostrar notas (${nt.length})</label>`:''));
      h+=box('Relaciones',
        `<label><input type="checkbox" data-flag="inherit" ${F.inherit===false?'':'checked'}><span class="swatch" style="background:#43a047"></span>Herencia</label>`+
        `<label><input type="checkbox" data-flag="assoc" ${F.assoc===false?'':'checked'}><span class="swatch" style="background:#78909c"></span>Asociación</label>`+
        `<label><input type="checkbox" data-flag="compose" ${F.compose===false?'':'checked'}><span class="swatch" style="background:#8e24aa"></span>Composición</label>`+
        `<label><input type="checkbox" data-flag="depend" ${F.depend===false?'':'checked'}><span class="swatch" style="background:#ef6c00"></span>Dependencia</label>`);
      h+=box('Clases',`<div style="max-height:250px;overflow:auto">`+cs.map(c=>
        `<label><input type="checkbox" data-id="${c.id}" ${this.hidden.has(c.id)?'':'checked'}><span class="swatch" style="background:${c.kind==='enum'?COLORS.enum:COLORS.class}"></span><span style="font-size:11.8px">${esc(c.name)}</span></label>`).join('')+`</div>`);
      h+=box('Selección rápida',
        `<div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn" data-sel="all" style="font-size:11.5px;padding:5px 9px">Todo</button>
          <button class="btn" data-sel="none" style="font-size:11.5px;padding:5px 9px">Nada</button>
          <button class="btn" data-sel="core" style="font-size:11.5px;padding:5px 9px">Solo entidades</button>
        </div>`);
    }
    this.side.innerHTML=h;

    const q=$('#'+this.sideId+'-q');
    q.oninput=()=>{ this.query=q.value.trim(); this.render(); };
    $$('input[data-id]',this.side).forEach(cb=>cb.onchange=()=>{
      cb.checked?this.hidden.delete(cb.dataset.id):this.hidden.add(cb.dataset.id); this.render();
    });
    $$('input[data-flag]',this.side).forEach(cb=>cb.onchange=()=>{
      this.flags[cb.dataset.flag]=cb.checked;
      if(cb.dataset.flag==='attrs'||cb.dataset.flag==='methods'){ this.measure(); this.render(); }
      else this.render();
    });
    $$('button[data-sel]',this.side).forEach(b=>b.onclick=()=>{
      const m=b.dataset.sel;
      this.nodes.forEach(n=>{
        if(n.kind==='note') return;
        let show=true;
        if(m==='none') show=false;
        else if(m==='actors') show=(n.kind==='actor');
        else if(m==='ucs') show=(n.kind==='uc');
        else if(m==='core') show=(n.kind==='class'||n.kind==='enum');
        show?this.hidden.delete(n.id):this.hidden.add(n.id);
      });
      this.buildSide(); this.render();
    });
  }

  /* geometría de una arista (soporta self-loops: Materia --> Materia) */
  edgeGeom(e,byId){
    const a=byId[e.from], b=byId[e.to];
    if(e.from===e.to){
      const hw=a.w/2, hh=a.h/2;
      const A={x:a.x+hw*.6,y:a.y-hh*.5}, B={x:a.x+hw*.6,y:a.y+hh*.5};
      return {A,B,mx:a.x+hw+62,my:a.y,
        path:`M${A.x},${A.y} C${a.x+hw+76},${a.y-hh} ${a.x+hw+76},${a.y+hh} ${B.x},${B.y}`};
    }
    const A=this.anchor(a,b), B=this.anchor(b,a);
    return {A,B,mx:(A.x+B.x)/2,my:(A.y+B.y)/2,path:`M${A.x},${A.y} L${B.x},${B.y}`};
  }

  /* ---------- render ---------- */
  render(){
    this.measure();
    const NS='http://www.w3.org/2000/svg';
    this.svg.innerHTML=`<defs>
      <marker id="m-${this.sideId}-assoc" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
        <path d="M0,0 L10,5 L0,10" fill="none" stroke="#78909c" stroke-width="1.6"/></marker>
      <marker id="m-${this.sideId}-inherit" markerWidth="13" markerHeight="13" refX="12" refY="6.5" orient="auto">
        <path d="M0,0 L13,6.5 L0,13 z" fill="#fff" stroke="#43a047" stroke-width="1.6"/></marker>
      <marker id="m-${this.sideId}-include" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
        <path d="M0,0 L10,5 L0,10" fill="none" stroke="#43a047" stroke-width="1.8"/></marker>
      <marker id="m-${this.sideId}-extend" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
        <path d="M0,0 L10,5 L0,10" fill="none" stroke="#fb8c00" stroke-width="1.8"/></marker>
      <marker id="m-${this.sideId}-compose" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto">
        <path d="M1,1 L1,11 L11,6 z" fill="#8e24aa"/></marker>
      <marker id="m-${this.sideId}-depend" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto">
        <path d="M0,0 L10,5 L0,10" fill="none" stroke="#ef6c00" stroke-width="1.7"/></marker>
    </defs><g id="edges-${this.sideId}"></g><g id="nodes-${this.sideId}"></g>`;

    const eg=this.svg.querySelector('#edges-'+this.sideId);
    const ng=this.svg.querySelector('#nodes-'+this.sideId);
    const byId=Object.fromEntries(this.nodes.map(n=>[n.id,n]));

    /* --- aristas --- */
    this.edges.forEach((e,i)=>{
      if(!this.edgeVisible(e)) return;
      const a=byId[e.from], b=byId[e.to];
      const {A,B,mx,my,path}=this.edgeGeom(e,byId);
      const dx=B.x-A.x, dy=B.y-A.y, len=Math.hypot(dx,dy)||1;
      const curve = (e.kind==='assoc'||e.kind==='inherit')?0:0;
      const color = e.kind==='include'?'#43a047': e.kind==='extend'?'#fb8c00':
                    e.kind==='inherit'?'#43a047': e.kind==='compose'?'#8e24aa':
                    e.kind==='depend'?'#ef6c00':'#78909c';
      const dash = (e.kind==='extend'||e.kind==='depend')?'stroke-dasharray="7 5"':'';
      const mk = ['inherit','compose','depend'].includes(e.kind)?e.kind:(e.kind==='assoc'&&this.mode==='cu'?'assoc':(e.kind==='assoc'?'assoc':e.kind));
      let s=`<path class="hit" d="${path}" stroke="${color}" stroke-width="1.9" fill="none" ${dash} marker-end="url(#m-${this.sideId}-${mk==='assoc'&&this.mode==='cl'?'assoc':mk})"/>`;
      if(e.kind==='inherit'){ s=s.replace(/marker-end="[^"]*"/,`marker-end="url(#m-${this.sideId}-inherit)"`); }
      if(e.label||['include','extend'].includes(e.kind)){
        const lab = e.label || ('<<'+e.kind+'>>');
        const w=lab.length*6.2+12;
        s+=`<g transform="translate(${mx},${my})"><rect x="${-w/2}" y="-9" width="${w}" height="17" rx="4" fill="#fff" stroke="${color}" stroke-opacity=".35"/>
            <text x="0" y="3.5" text-anchor="middle" font-size="10.6" font-weight="700" fill="${color}">${esc(lab)}</text></g>`;
      }
      if(e.cf) s+=`<text x="${A.x+dx*.18}" y="${A.y+dy*.18-5}" font-size="10.5" fill="#64748b" text-anchor="middle">${esc(e.cf)}</text>`;
      if(e.ct) s+=`<text x="${A.x+dx*.82}" y="${A.y+dy*.82-5}" font-size="10.5" fill="#64748b" text-anchor="middle">${esc(e.ct)}</text>`;
      eg.insertAdjacentHTML('beforeend',s);
    });

    /* --- nodos --- */
    this.nodes.forEach(n=>{
      if(!this.visible(n)) return;
      ng.insertAdjacentHTML('beforeend',this.nodeSVG(n));
    });

    /* --- drag de nodos --- */
    $$('g.uml-node',ng).forEach(g=>{
      g.addEventListener('pointerdown',ev=>{
        ev.stopPropagation();
        const n=this.nodes.find(x=>x.id===g.dataset.id); if(!n) return;
        const sx=ev.clientX, sy=ev.clientY, ox=n.x, oy=n.y;
        g.setPointerCapture(ev.pointerId);
        const mv=e2=>{ n.x=ox+(e2.clientX-sx)/this.k; n.y=oy+(e2.clientY-sy)/this.k;
          g.setAttribute('transform',`translate(${n.x},${n.y})`); this.drawEdges(); };
        const up=()=>{ g.removeEventListener('pointermove',mv); g.removeEventListener('pointerup',up);
          this.save(true); };
        g.addEventListener('pointermove',mv); g.addEventListener('pointerup',up);
      });
      g.addEventListener('dblclick',ev=>{ ev.stopPropagation();
        const n=this.nodes.find(x=>x.id===g.dataset.id); if(n) this.center(n); });
    });

    this.apply();
    const visN=this.nodes.filter(n=>this.visible(n)).length;
    const visE=this.edges.filter(e=>this.edgeVisible(e)).length;
    $('#'+this.countId).textContent=`${visN} nodos · ${visE} relaciones`;
  }

  drawEdges(){
    /* redesibuja solo las aristas tras mover un nodo */
    const eg=this.svg.querySelector('#edges-'+this.sideId);
    if(!eg) return;
    const keep=eg.innerHTML;
    const tmp=this.edges.slice();
    eg.innerHTML='';
    const byId=Object.fromEntries(this.nodes.map(n=>[n.id,n]));
    /* reutiliza la misma lógica invocando render completo ligero */
    const visN=this.nodes.filter(n=>this.visible(n));
    this.edges.forEach(e=>{
      if(!this.edgeVisible(e)) return;
      const a=byId[e.from], b=byId[e.to]; if(!a||!b) return;
      const {A,B,mx,my,path}=this.edgeGeom(e,byId);
      const color = e.kind==='include'?'#43a047': e.kind==='extend'?'#fb8c00':
                    e.kind==='inherit'?'#43a047': e.kind==='compose'?'#8e24aa':
                    e.kind==='depend'?'#ef6c00':'#78909c';
      const dash=(e.kind==='extend'||e.kind==='depend')?'stroke-dasharray="7 5"':'';
      const mk = e.kind==='inherit'?'inherit':e.kind==='compose'?'compose':e.kind==='depend'?'depend':
                 (e.kind==='assoc'&&this.mode==='cu')?'assoc':(e.kind==='assoc'?'assoc':e.kind);
      let s=`<path class="hit" d="${path}" stroke="${color}" stroke-width="1.9" fill="none" ${dash} marker-end="url(#m-${this.sideId}-${mk})"/>`;
      if(e.label||['include','extend'].includes(e.kind)){
        const lab=e.label||('<<'+e.kind+'>>'); const w=lab.length*6.2+12;
        s+=`<g transform="translate(${mx},${my})"><rect x="${-w/2}" y="-9" width="${w}" height="17" rx="4" fill="#fff" stroke="${color}" stroke-opacity=".35"/>
            <text x="0" y="3.5" text-anchor="middle" font-size="10.6" font-weight="700" fill="${color}">${esc(lab)}</text></g>`;
      }
      if(e.cf) s+=`<text x="${A.x+(B.x-A.x)*.18}" y="${A.y+(B.y-A.y)*.18-5}" font-size="10.5" fill="#64748b" text-anchor="middle">${esc(e.cf)}</text>`;
      if(e.ct) s+=`<text x="${A.x+(B.x-A.x)*.82}" y="${A.y+(B.y-A.y)*.82-5}" font-size="10.5" fill="#64748b" text-anchor="middle">${esc(e.ct)}</text>`;
      eg.insertAdjacentHTML('beforeend',s);
    });
  }

  nodeSVG(n){
    const x=n.x,y=n.y;
    if(n.kind==='actor'){
      return `<g class="uml-node hit" data-id="${n.id}" transform="translate(${x},${y})" style="cursor:move">
        <circle cx="0" cy="-24" r="12" fill="#e8eaf6" stroke="${COLORS.actor}" stroke-width="2.4"/>
        <path d="M0,-12 L0,14 M-17,0 L17,0 M0,14 L-15,38 M0,14 L15,38" stroke="${COLORS.actor}" stroke-width="2.4" fill="none" stroke-linecap="round"/>
        <text x="0" y="58" text-anchor="middle" font-size="12.4" font-weight="700" fill="#283593">${esc(n.name)}</text></g>`;
    }
    if(n.kind==='uc'){
      return `<g class="uml-node hit" data-id="${n.id}" transform="translate(${x},${y})" style="cursor:move">
        <ellipse cx="0" cy="0" rx="${n.w/2}" ry="${n.h/2}" fill="#e3f2fd" stroke="${COLORS.uc}" stroke-width="2.2"/>
        <text x="0" y="${n.name.length>30?-2:4}" text-anchor="middle" font-size="11.8" fill="#0d3270" font-weight="600">${
          wrap(n.name,30).map((l,i)=>`<tspan x="0" dy="${i?14:0}">${esc(l)}</tspan>`).join('')}</text></g>`;
    }
    if(n.kind==='note'){
      const lines=wrap(n.name,34);
      return `<g class="uml-node hit" data-id="${n.id}" transform="translate(${x},${y})" style="cursor:move">
        <g transform="translate(${-n.w/2},${-n.h/2})">
        <path d="M0,0 H${n.w-14} L${n.w},14 V${n.h} H0 Z" fill="#fffde7" stroke="#f9a825" stroke-width="1.6"/>
        <path d="M${n.w-14},0 V14 H${n.w}" fill="none" stroke="#f9a825" stroke-width="1.6"/>
        <text x="12" y="24" font-size="11.2" fill="#5d4037">${lines.map((l,i)=>`<tspan x="12" dy="${i?15:0}">${esc(l)}</tspan>`).join('')}</text></g></g>`;
    }
    /* clase / enum */
    const showA=this.flags.attrs!==false, showM=this.flags.methods!==false;
    const isEnum=n.kind==='enum';
    const head=isEnum?'#8e24aa':(n.color||'#1e88e5');
    let yy=34, rows='';
    if(showA){
      rows+=`<line x1="0" y1="${yy-8}" x2="${n.w}" y2="${yy-8}" stroke="#cfd8dc" stroke-width="1"/>`;
      n.attrs.forEach(a=>{
        const t=(a.vis&&a.vis.trim()?a.vis:'')+' '+a.name+(a.type?' : '+a.type:'');
        rows+=`<text x="11" y="${yy+4}" font-size="11.3" fill="#37474f" font-family="Consolas,monospace">${esc(t.trim())}</text>`;
        yy+=15.5;
      });
    }
    if(showM && n.methods.length){
      yy+=6;
      rows+=`<line x1="0" y1="${yy-8}" x2="${n.w}" y2="${yy-8}" stroke="#cfd8dc" stroke-width="1"/>`;
      n.methods.forEach(m=>{
        const t=(m.vis||'+')+' '+m.name+'('+(m.params||'')+')'+(m.ret?': '+m.ret:'');
        rows+=`<text x="11" y="${yy+4}" font-size="11.3" fill="#1b5e20" font-family="Consolas,monospace">${esc(t)}</text>`;
        yy+=15.5;
      });
    }
    return `<g class="uml-node hit" data-id="${n.id}" transform="translate(${x},${y})" style="cursor:move">
      <g transform="translate(${-n.w/2},${-n.h/2})">
      <rect x="0" y="0" width="${n.w}" height="${n.h}" rx="7" fill="#fff" stroke="${head}" stroke-width="2"/>
      <rect x="0" y="0" width="${n.w}" height="30" rx="7" fill="${head}"/>
      <rect x="0" y="16" width="${n.w}" height="14" fill="${head}"/>
      <text x="${n.w/2}" y="20" text-anchor="middle" font-size="12.6" font-weight="700" fill="#fff">${esc(n.name)}</text>
      ${isEnum?'<text x="'+(n.w-9)+'" y="20" text-anchor="end" font-size="9.4" fill="#ffffffaa">«enum»</text>':''}
      ${rows}</g></g>`;
  }

  anchor(n,t){
    const cx=n.x, cy=n.y;
    if(n.kind==='actor') return {x:cx, y:cy+34};
    if(n.kind==='uc'){
      const tx=t.x, ty=t.y; const dx=tx-cx, dy=ty-cy;
      const rx=n.w/2, ry=n.h/2; const d=Math.hypot(dx,dy)||1;
      return {x:cx+dx/d*rx, y:cy+dy/d*ry};
    }
    /* rectángulo: intersección con el borde */
    const hw=n.w/2, hh=n.h/2, dx=t.x-cx, dy=t.y-cy;
    if(!dx&&!dy) return {x:cx,y:cy+hh};
    const sx=dx?hw/Math.abs(dx):Infinity, sy=dy?hh/Math.abs(dy):Infinity;
    const s=Math.min(sx,sy);
    return {x:cx+dx*s, y:cy+dy*s};
  }

  /* ---------- transform ---------- */
  apply(){
    this.layer.style.transform=`translate(${this.tx}px,${this.ty}px) scale(${this.k})`;
    $('#'+this.zoomId).textContent=Math.round(this.k*100)+'%';
  }
  fit(){
    const vis=this.nodes.filter(n=>this.visible(n)); if(!vis.length) return;
    const minX=Math.min(...vis.map(n=>n.x-(n.kind==='actor'?60:n.w/2)));
    const maxX=Math.max(...vis.map(n=>n.x+(n.kind==='actor'?60:n.w/2)));
    const minY=Math.min(...vis.map(n=>n.y-(n.kind==='actor'?50:n.h/2)));
    const maxY=Math.max(...vis.map(n=>n.y+(n.kind==='actor'?45:n.h/2)));
    const r=this.stage.getBoundingClientRect();
    if(!r.width||!r.height) return;          /* pestaña oculta: no ajustar aún */
    const w=maxX-minX+80, h=maxY-minY+80;
    this.k=Math.max(.18,Math.min(1.5,Math.min(r.width/w,r.height/h)));
    this.tx=(r.width-(maxX-minX)*this.k)/2-minX*this.k;
    this.ty=(r.height-(maxY-minY)*this.k)/2-minY*this.k;
    this.userMoved=false;
    this.apply();
  }
  center(n){
    const r=this.stage.getBoundingClientRect();
    this.tx=r.width/2-n.x*this.k; this.ty=r.height/2-n.y*this.k;
    this.userMoved=true; this.apply();
  }

  /* ---------- persistencia ---------- */
  key(){ return 'umlpos_'+this.diagram.replace(/[^\w]/g,'_'); }
  save(silent){
    const p={}; this.nodes.forEach(n=>p[n.id]=[Math.round(n.x),Math.round(n.y)]);
    try{ localStorage.setItem(this.key(),JSON.stringify(p)); if(!silent) this.toast('Posiciones guardadas ✓'); }catch(e){}
  }
  load(silent){
    try{
      const raw=localStorage.getItem(this.key());
      if(!raw){ if(!silent) this.toast('No hay posiciones guardadas'); return false; }
      const p=JSON.parse(raw); let ok=0;
      this.nodes.forEach(n=>{ if(p[n.id]){ n.x=p[n.id][0]; n.y=p[n.id][1]; ok++; } });
      this.render(); if(!silent) this.toast(`${ok} elementos restaurados ✓`); return true;
    }catch(e){ return false; }
  }
  clear(){ try{localStorage.removeItem(this.key());}catch(e){} this.auto(); this.toast('Posiciones borradas'); }
  reset(auto){
    if(!this.load(true)) this.auto(); else this.render();
  }
  toast(msg){
    let t=document.getElementById('toast');
    if(!t){ t=document.createElement('div'); t.id='toast';
      t.style.cssText='position:fixed;top:18px;left:50%;transform:translateX(-50%);background:#0d47a1;color:#fff;padding:9px 20px;border-radius:9px;font-size:13px;z-index:999;pointer-events:none;box-shadow:0 6px 24px rgba(0,0,0,.25);transition:.3s';
      document.body.appendChild(t); }
    t.textContent=msg; t.style.opacity='1';
    clearTimeout(t._h); t._h=setTimeout(()=>t.style.opacity='0',1700);
  }

  /* ---------- interacción lienzo ---------- */
  _bind(){
    this.stage.addEventListener('wheel',e=>{
      e.preventDefault();
      this.userMoved=true;
      const r=this.stage.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
      const nk=Math.min(3,Math.max(.15,this.k*(e.deltaY<0?1.13:.885)));
      this.tx=mx-(mx-this.tx)*(nk/this.k); this.ty=my-(my-this.ty)*(nk/this.k);
      this.k=nk; this.apply();
    },{passive:false});

    this.stage.addEventListener('pointerdown',e=>{
      if(e.target.closest('.uml-node')) return;
      this.userMoved=true;
      const sx=e.clientX, sy=e.clientY, tx=this.tx, ty=this.ty;
      this.stage.classList.add('grabbing'); this.stage.setPointerCapture(e.pointerId);
      const mv=e2=>{ this.tx=tx+(e2.clientX-sx); this.ty=ty+(e2.clientY-sy); this.apply(); };
      const up=()=>{ this.stage.classList.remove('grabbing');
        this.stage.removeEventListener('pointermove',mv); this.stage.removeEventListener('pointerup',up); };
      this.stage.addEventListener('pointermove',mv); this.stage.addEventListener('pointerup',up);
    });
  }
}

/* ============================================================
   ARMADO DE LOS DOS VISORES
   ============================================================ */
const vCU = new Viewer({stageId:'cuStage',layerId:'cuLayer',svgId:'cuSvg',sideId:'cuSide',
                        zoomId:'cuZoom',countId:'cuVisible'});
const vCL = new Viewer({stageId:'clStage',layerId:'clLayer',svgId:'clSvg',sideId:'clSide',
                        zoomId:'clZoom',countId:'clVisible',staticLayout:true});

/* --- selector de diagramas CU --- */
(()=>{
  const sel=$('#cuDiagram');
  sel.innerHTML=DATA.cu.map((d,i)=>`<option value="${i}">${esc(d.file.replace('.puml',''))} — ${esc(d.title)}</option>`).join('');
  const load=()=>{ vCU.setCU(DATA.cu[+sel.value]); };
  sel.onchange=load; load();
})();

/* --- selector de diagramas de clases --- */
(()=>{
  const grp=$('#clGroup'), sel=$('#clDiagram');
  const fill=()=>{
    const list = grp.value==='paquete'?DATA.clases:DATA.detalle;
    sel.innerHTML=list.map((d,i)=>`<option value="${i}">${esc(d.file.replace('.puml',''))}</option>`).join('');
    vCL.setClases(list[+sel.value||0],grp.value);
  };
  grp.onchange=fill; sel.onchange=()=>{ const list=grp.value==='paquete'?DATA.clases:DATA.detalle; vCL.setClases(list[+sel.value],grp.value); };
  fill();
})();

/* --- selector de diseño (jerárquico / rejilla) --- */
(()=>{
  const lay=$('#clLayout');
  if(!lay) return;
  lay.onchange=()=>{ vCL.layoutMode=lay.value; vCL.auto(); };
})();

/* --- botones de herramientas --- */
$$('button[data-act]').forEach(b=>{
  b.onclick=()=>{
    const v = b.dataset.v==='cu'?vCU:vCL;
    const a = b.dataset.act;
    if(a==='auto') v.auto();
    else if(a==='fit') v.fit();
    else if(a==='save') v.save(false);
    else if(a==='load') v.load();
    else if(a==='clear') v.clear();
  };
});

/* --- botones de los flujos (una vez renderizadas las fichas) --- */
$$('button[data-flow]').forEach(b=>{ b.onclick=()=>{ const fv=FLOWVIEWS[b.dataset.flow]; if(fv) fv.fit(); }; });

/* --- enlazar visores de secuencia (con filtro normal / alternativas) --- */
const FLOWVIEWS={};
let SEQMODE='full';
function rebuildSeq(){
  FICHAS.forEach(f=>{ buildSeq(f, SEQMODE); });
  FICHAS.forEach(f=>{ const v=FLOWVIEWS[f.id]; if(v){ v.fit(); } else { FLOWVIEWS[f.id]=attachFlowView(f.id); FLOWVIEWS[f.id].fit(); } });
}
FICHAS.forEach(f=>{ if(buildSeq(f, SEQMODE)) FLOWVIEWS[f.id]=attachFlowView(f.id); });
const seqSel=$('#seqMode');
if(seqSel) seqSel.onchange=()=>{ SEQMODE=seqSel.value; rebuildSeq(); };
requestAnimationFrame(()=>{ FICHAS.forEach(f=>{ const v=FLOWVIEWS[f.id]; if(v) v.fit(); }); vCU.fit(); vCL.fit(); });

/* ============================================================
   ASISTENTE VIRTUAL — consultas a la BD vía backend RAG (JWT+RBAC)
   Modo por defecto: POST /api/v1/chat/ (RAG pgvector + tools instituto)
   Modo alternativo: Groq directo con contexto del documento (demo)
   ============================================================ */
const CHAT = (()=>{
  const log=$('#chatLog'), input=$('#chatInput'), send=$('#chatSend'),
        net=$('#chatNet'), netTxt=$('#chatNetTxt'), modeLbl=$('#chatMode'),
        prov=$('#chatProv'), modelSel=$('#chatModel'), keyIn=$('#chatKey'),
        localBox=$('#localBox'), groqBox=$('#groqBox'), hint=$('#chatHint'),
        userLbl=$('#chatUser'), docsUrl=$('#chatDocsUrl');

  const LS_KEY='isft189_groq_key', LS_MODEL='isft189_groq_model',
        LS_TOKEN='isft189_jwt', LS_USER='isft189_user', LS_API='isft189_api';
  const GROQ_URL='https://api.groq.com/openai/v1/chat/completions';
  let busy=false, history=[], session=null;   /* session: {full_name, role, file_number} */

  const getKey = ()=> (localStorage.getItem(LS_KEY)||'').trim() || (GROQ_KEY_DEFAULT||'').trim();
  const getModel = ()=> localStorage.getItem(LS_MODEL) || modelSel.value;
  const apiBase = ()=> ($('#chatApi').value||'http://127.0.0.1:8000').replace(/\/$/,'');
  const isLocal = ()=> prov.value==='local';

  /* ---------- contexto del documento (solo modo demo Groq) ---------- */
  const CONTEXT = (()=>{
    const pkgs={};
    CATALOG.forEach(c=>{ (pkgs[c.pkg]=pkgs[c.pkg]||{n:0,name:c.pkgName}); pkgs[c.pkg].n++; });
    const pkgTxt=Object.entries(pkgs).map(([k,v])=>`${k} — ${v.name} (${v.n} CU)`).join('\n');
    const cuTxt=CATALOG.map(c=>`${c.code} ${c.name} [${c.pkg}] actor:${c.actor} RF:${c.rf}`).join('\n');
    const fichaTxt=FICHAS.map(f=>{
      const steps=f.steps.map((s,i)=>`  ${i+1}. ${s.text}`).join('\n');
      return `${f.id} — ${f.title} (${f.pkgName})\nActor: ${f.actor} · RF: ${f.rf}\n${f.desc.replace(/\s+/g,' ').trim()}\nFlujo:\n${steps}`;
    }).join('\n\n');
    const classNames=[...new Set(DATA.clases.flatMap(d=>d.classes.map(c=>c.name)))].sort();
    return {pkgTxt,cuTxt,fichaTxt,classNames};
  })();

  const SYSTEM = `Sos el asistente virtual académico del Instituto Superior de Formación Técnica N° 189 (ISFT 189), dentro de un documento interactivo de casos de uso y UML.
Respondé en español, claro, conciso y formal. Fundamentá en el CONTEXTO de abajo (catálogo de casos de uso, fichas descriptivas y modelo de clases). Si la respuesta no está en el contexto, aclará que no disponés de esa información en el documento y recomendá consultar en Secretaría. Mencioná los códigos (CU-xx, RF-xxx, PK-xxx) cuando corresponda.

=== PAQUETES FUNCIONALES ===
${CONTEXT.pkgTxt}

=== CATÁLOGO COMPLETO (49 casos de uso) ===
${CONTEXT.cuTxt}

=== FICHAS DESCRIPTIVAS (con flujo) ===
${CONTEXT.fichaTxt}

=== CLASES DEL MODELO ===
${CONTEXT.classNames.join(', ')}`;

  /* ---------- UI ---------- */
  function addMsg(role, html, cls){
    const d=document.createElement('div');
    d.className='msg '+(role==='u'?'u':('a '+(cls||'')));
    d.innerHTML=html;
    log.appendChild(d); log.scrollTop=log.scrollHeight;
    return d;
  }
  const typing=()=>addMsg('a','<span class="typing"><i></i><i></i><i></i></span>');
  const escMd = s => esc(s);

  /* render mínimo: negrita, código, tablas, listas, headings, citas, saltos */
  function md(t){
    let h=esc(t)
      .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
      .replace(/(^|[^*])\*([^*\n]+)\*/g,'$1<i>$2</i>')
      .replace(/`([^`]+)`/g,'<code>$1</code>');
    const lines=h.split('\n');
    let out='', inL=false, nL=false, tbl=null;

    const flushL=()=>{
      if(inL){out+='</ul>';inL=false;}
      if(nL){out+='</ol>';nL=false;}
    };
    const flushTbl=()=>{
      if(!tbl) return;
      const rows=tbl.filter(r=>!/^\s*\|[\s\-:|]+\|\s*$/.test(r))
        .map(r=>r.replace(/^\s*\||\|\s*$/g,'').split('|').map(c=>c.trim()));
      if(rows.length){
        out+='<table style="margin:6px 0;font-size:12.4px"><thead><tr>'+
          rows[0].map(c=>`<th style="padding:4px 9px;background:#0d47a1;color:#fff;border:0">${c}</th>`).join('')+
          '</tr></thead><tbody>'+
          rows.slice(1).map(r=>'<tr>'+r.map(c=>`<td style="padding:4px 9px;border-bottom:1px solid #e2e8f0">${c}</td>`).join('')+'</tr>').join('')+
          '</tbody></table>';
      }
      tbl=null;
    };

    for(const raw of lines){
      const ln=raw.trimEnd();
      if(/^\s*\|.*\|\s*$/.test(ln)){          /* fila de tabla */
        flushL();
        (tbl=tbl||[]).push(ln);
        continue;
      }
      flushTbl();
      if(/^\s*(---+|\*\*\*+|___+)\s*$/.test(ln)){ flushL(); out+='<hr style="border:0;border-top:1px solid #e2e8f0;margin:9px 0">'; continue; }
      const hd=ln.match(/^\s*(#{1,6})\s+(.*)$/);
      if(hd){ flushL(); const sz=Math.max(12.6,15.2-hd[1].length*0.9);
        out+=`<p style="font-size:${sz}px;margin:9px 0 4px"><b>${hd[2]}</b></p>`; continue; }
      const bq=ln.match(/^\s*&gt;\s?(.*)$/);
      if(bq){ flushL(); out+=`<p style="border-left:3px solid #90caf9;padding-left:9px;color:#455a64;margin:5px 0"><i>${bq[1]}</i></p>`; continue; }
      const om=ln.match(/^\s*(\d+)[.)]\s+(.*)$/);
      if(om){ if(inL){out+='</ul>';inL=false;} if(!nL){out+='<ol style="margin:5px 0 3px;padding-left:21px">';nL=true;}
        out+=`<li>${om[2]}</li>`; continue; }
      const m=ln.match(/^\s*[-•]\s+(.*)$/);
      if(m){ if(nL){out+='</ol>';nL=false;} if(!inL){out+='<ul>';inL=true;} out+=`<li>${m[1]}</li>`; continue; }
      flushL();
      if(ln.trim()) out+='<p>'+ln+'</p>';
    }
    flushL();
    flushTbl();
    return out.replace(/<p><\/p>/g,'');
  }

  function setNet(ok,txt){ net.classList.toggle('off',!ok); netTxt.textContent=txt; }
  function setMode(){
    modeLbl.textContent = isLocal()
      ? 'RAG + BD institucional · JWT + RBAC'
      : `Groq directo · ${getModel()} · contexto del documento`;
  }

  /* ---------- sesión JWT en el backend ---------- */
  async function login(silent){
    const base=apiBase();
    const r=await fetch(base+'/api/v1/auth/login',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email:$('#chatEmail').value.trim(),password:$('#chatPass').value})
    });
    if(!r.ok) throw new Error('Login rechazado ('+r.status+') — verificá email/contraseña o el backend.');
    const j=await r.json();
    localStorage.setItem(LS_TOKEN,j.access_token);
    localStorage.setItem(LS_USER,JSON.stringify(j.user));
    localStorage.setItem(LS_API,base);
    session=j.user;
    userLbl.innerHTML=`<b>${esc(j.user.full_name)}</b> · ${esc(j.user.role)}`+
      (j.user.file_number? ` · Legajo ${j.user.file_number}`:'')+
      ` <span style="opacity:.7">(JWT activo)</span>`;
    setNet(true, 'bd: '+j.user.role.toLowerCase());
    if(!silent) addMsg('a',md(
      `**Sesión iniciada** como ${j.user.full_name} (\`${j.user.role}\`).\n`+
      'Ahora mis consultas se resuelven contra la **base de datos real** con tus permisos: '+
      'carreras y planes, materias, correlatividades, mesas de examen, historial y asistencias.'));
    return j;
  }

  async function health(){
    try{
      const r=await fetch(apiBase()+'/health',{cache:'no-store'});
      if(!r.ok) return false;
      const j=await r.json();
      return j.status==='healthy';
    }catch(e){ return false; }
  }

  /* ---------- Backend: RAG pgvector + tools académicos sobre la BD ---------- */
  async function askLocal(question, bub){
    const base=apiBase();
    let tok=localStorage.getItem(LS_TOKEN);
    const call=async(t)=>{
      const r=await fetch(base+'/api/v1/chat/',{
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer '+t},
        body:JSON.stringify({question,top_k:4})
      });
      if(r.status===401) return null;
      if(!r.ok){
        let d=''; try{ d=(await r.json()).detail||''; }catch(e){}
        throw new Error(`Backend respondió ${r.status}. ${typeof d==='string'?d:JSON.stringify(d)}`);
      }
      return r.json();
    };
    let j = tok? await call(tok) : null;
    if(!j){ await login(true); tok=localStorage.getItem(LS_TOKEN); j=await call(tok); }
    if(!j) throw new Error('Sesión rechazada por el backend. Volvé a iniciar sesión.');

    /* fuentes: tablas académicas consultadas + documentos RAG recuperados */
    const acad=(j.academic_sources||[]);
    const docs=[...new Set((j.retrieved_chunks||[]).map(c=>{
      const m=c.metadata||{};
      const bits=[m.tipo,m.carrera,m.materia,m.articulo,m.requisito].filter(Boolean);
      return bits.length? bits.join(' · ') : null;
    }).filter(Boolean))].slice(0,4);
    const bits=[
      acad.length? `<b>Tablas BD:</b> ${esc(acad.join(' · '))}`:'',
      docs.length? `<b>Docs RAG:</b> ${esc(docs.join(' || '))}`:'',
      j.model? `<b>Modelo:</b> ${esc(j.model)} vía ${esc(j.llm_provider||'groq')}`:''
    ].filter(Boolean);
    const suffix = bits.length? '\n\n<small class="src">'+bits.join('<br>')+'</small>' : '';
    bub.innerHTML=md(j.answer)+suffix;
    log.scrollTop=log.scrollHeight;
    return j.answer;
  }

  /* ---------- Groq directo con streaming (modo demo, sin BD) ---------- */
  async function askGroq(question, bub){
    const key=getKey();
    if(!key){ throw new Error('Falta la API key de Groq. Pegala en el panel derecho y guardá.'); }
    const msgs=[{role:'system',content:SYSTEM},
                ...history.slice(-10),
                {role:'user',content:question}];

    const res=await fetch(GROQ_URL,{
      method:'POST',
      headers:{'Content-Type':'application/json','Authorization':'Bearer '+key},
      body:JSON.stringify({model:getModel(),messages:msgs,temperature:0.3,
                           max_tokens:6000,stream:true})
    });
    if(!res.ok){
      let d=''; try{ d=(await res.json()).error?.message||''; }catch(e){}
      if(res.status===401) throw new Error('API key inválida o revocada. ' + d);
      if(res.status===429) throw new Error('Límite de uso de Groq alcanzado, probá en unos minutos. ' + d);
      throw new Error(`Error Groq (${res.status}). ${d}`);
    }

    /* SSE de OpenAI-compatible: la respuesta crece en la misma burbuja */
    bub.innerHTML='';
    let acc='';
    const reader=res.body.getReader(), dec=new TextDecoder();
    let buf='';
    while(true){
      const {done,value}=await reader.read(); if(done) break;
      buf+=dec.decode(value,{stream:true});
      const parts=buf.split('\n'); buf=parts.pop();
      for(const line of parts){
        const m=/^data:\s*(.*)$/.exec(line.trim()); if(!m) continue;
        if(m[1]==='[DONE]') continue;
        try{
          const j=JSON.parse(m[1]);
          const d=j.choices?.[0]?.delta?.content;
          if(d){ acc+=d; bub.innerHTML=md(acc); log.scrollTop=log.scrollHeight; }
        }catch(e){}
      }
    }
    if(!acc){ bub.remove(); throw new Error('Groq devolvió una respuesta vacía. Probá con otro modelo.'); }
    return acc;
  }

  /* ---------- flujo de envío ---------- */
  async function ask(text){
    if(busy||!text.trim()) return;
    busy=true; send.disabled=true; input.value='';
    addMsg('u',escMd(text).replace(/\n/g,'<br>'));
    const t=typing();
    try{
      setMode();
      const ans = isLocal()? await askLocal(text,t) : await askGroq(text,t);
      history.push({role:'user',content:text},{role:'assistant',content:ans});
      if(history.length>20) history=history.slice(-20);
      if(isLocal()) setNet(true,'bd en línea'); else setNet(true,'groq en línea');
    }catch(err){
      t.remove();
      addMsg('a','⚠️ '+esc(err.message||String(err)),'err');
      setNet(false,isLocal()?'backend caído':'sin conexión');
    }finally{
      busy=false; send.disabled=false; input.focus();
    }
  }

  /* ---------- eventos ---------- */
  send.onclick=()=>ask(input.value);
  input.addEventListener('keydown',e=>{
    if(e.key==='Enter'&&!e.shiftKey){ e.preventDefault(); ask(input.value); }
  });
  $$('#chatChips .chipq').forEach(b=>b.onclick=()=>ask(b.textContent.trim()));
  $('#chatClear').onclick=()=>{ history=[]; log.innerHTML=''; greet(); };

  prov.onchange=()=>{
    const loc=isLocal();
    groqBox.classList.toggle('apioff',loc);
    localBox.classList.toggle('apioff',!loc);
    setMode();
    hint.innerHTML = loc
      ? 'Cada consulta llama a <code>POST /api/v1/chat/</code>: recuperación vectorial (pgvector) + tools académicos sobre las tablas <code>instituto.*</code>, con el rol del JWT. Mismo flujo que el Swagger.'
      : 'Modo demo: el HTML consulta <code>api.groq.com</code> directamente con el contexto de este documento (49 CU, fichas, clases). <b>No toca la base de datos.</b>';
    if(loc) probeBackend(); else probeGroq();
  };
  modelSel.onchange=()=>{ localStorage.setItem(LS_MODEL,modelSel.value); setMode(); };
  keyIn.value=getKey();
  $('#chatKeySave').onclick=()=>{
    const k=keyIn.value.trim();
    if(!k){ localStorage.removeItem(LS_KEY); setNet(false,'sin key'); return; }
    localStorage.setItem(LS_KEY,k);
    setNet(true,'key guardada ✓');
    setTimeout(()=>probeGroq(),600);
  };
  $('#chatLogin').onclick=async()=>{
    const btn=$('#chatLogin'); btn.disabled=true; btn.textContent='⏳ Iniciando…';
    try{ await login(false); }
    catch(err){
      setNet(false,'backend caído');
      addMsg('a','⚠️ '+esc(err.message)+' — levantá el stack: Docker (<code>tpi-isft189</code>) + <code>uvicorn app.main:app --port 8000</code>.','err');
    }finally{ btn.disabled=false; btn.textContent='🔑 Iniciar sesión'; }
  };
  $('#chatApi').addEventListener('change',()=>{ if(isLocal()) probeBackend(); });

  async function probeGroq(){
    const key=getKey();
    if(!key){ setNet(false,'sin key'); return; }
    try{
      const r=await fetch('https://api.groq.com/openai/v1/models',
        {headers:{'Authorization':'Bearer '+key}});
      setNet(r.ok, r.ok?'groq en línea':'key rechazada');
    }catch(e){ setNet(false,'sin conexión'); }
  }

  async function probeBackend(){
    setNet(false,'verificando…');
    if(!(await health())){
      setNet(false,'backend caído');
      userLbl.innerHTML='Backend no responde en <code>'+esc(apiBase())+'</code>. Levantá Docker + uvicorn.';
      return;
    }
    /* ¿hay JWT guardado todavía válido? */
    const tok=localStorage.getItem(LS_TOKEN);
    if(tok){
      try{
        const r=await fetch(apiBase()+'/api/v1/auth/me',{headers:{'Authorization':'Bearer '+tok}});
        if(r.ok){
          const u=await r.json();
          session=u;
          userLbl.innerHTML=`<b>${esc(u.full_name||u.email)}</b> · ${esc(u.role||'')}`+
            (u.file_number? ` · Legajo ${u.file_number}`:'')+
            ` <span style="opacity:.7">(JWT activo)</span>`;
          setNet(true,'bd: '+(u.role||'').toLowerCase());
          return;
        }
      }catch(e){}
      localStorage.removeItem(LS_TOKEN);
    }
    try{ await login(true); }catch(e){
      setNet(false,'sin sesión');
      userLbl.innerHTML='Backend en línea pero sin sesión. Cargá credenciales y tocá <b>Iniciar sesión</b>.';
    }
  }

  function greet(){
    addMsg('a',md(
      '**Hola 👋 Soy el asistente virtual del ISFT 189.**\n'+
      'Consulto la **base de datos real** del sistema (igual que el Swagger): carreras y planes de estudio, materias y correlatividades, mesas de examen, historial académico, asistencias y avisos.\n'+
      'Todo se resuelve con **JWT + RBAC**: veo solo lo que tu rol permite.\n\n'+
      'Probá una de las consultas sugeridas abajo o escribí la tuya.'));
  }

  /* init: recordar URL del backend, sincronizar UI y levantar sesión */
  const savedApi=localStorage.getItem(LS_API); if(savedApi) $('#chatApi').value=savedApi;
  if(docsUrl) docsUrl.innerHTML=`<a href="${esc(apiBase())}/docs" target="_blank" rel="noopener">${esc(apiBase())}/docs</a>`;
  $('#chatApi').addEventListener('change',()=>{ if(docsUrl) docsUrl.innerHTML=`<a href="${esc(apiBase())}/docs" target="_blank" rel="noopener">${esc(apiBase())}/docs</a>`; });
  prov.value='local';
  prov.onchange();
  greet();
  probeBackend();
  return {ask};
})();
