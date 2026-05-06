import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { publicService } from '../services/cuestionarios';
import styles from './Responder.module.css';

const OPCIONES = [
  { valor: 0, label: 'Nunca' },
  { valor: 1, label: 'Casi nunca' },
  { valor: 2, label: 'Algunas veces' },
  { valor: 3, label: 'Casi siempre' },
  { valor: 4, label: 'Siempre' },
];

const OPCIONES_SI_NO = [
  { valor: 1, label: 'Sí' },
  { valor: 0, label: 'No' },
];

const hasAnswer = (value) => value !== undefined && value !== '';

const GUIA_LABEL = { V: 'Guía V', III: 'Guía III', I: 'Guía I' };
const GUIA_SIGUIENTE = { V: 'III', III: 'I' };

export default function Responder() {
  const { token } = useParams();
  const navigate  = useNavigate();
  const [data, setData]                   = useState(null);
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState('');
  const [answers, setAnswers]             = useState({});
  const [step, setStep]                   = useState(-1);   // -1 = intro
  const [saving, setSaving]               = useState(false);
  const [saveError, setSaveError]         = useState('');
  const [completed, setCompleted]         = useState(false);
  const [siguienteToken, setSiguienteToken] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await publicService.getAplicacion(token);
        const apl = res.data.data;
        setData(apl);
        const restored = {};
        Object.entries(apl.respuestas_guardadas || {}).forEach(([k, v]) => {
          restored[k] = v;
        });
        setAnswers(restored);
        if (apl.estado === 'completado') setCompleted(true);
      } catch {
        setError('No se encontró el cuestionario. El enlace puede ser inválido o haber expirado.');
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  const dominios       = data?.cuestionario?.dominios || [];
  const isPreguntaVisible = (pregunta, answerMap = answers) => {
    const ids = [
      pregunta.condicion_pregunta,
      ...(pregunta.condicion_preguntas || []),
    ].filter(Boolean);
    if (ids.length === 0) return true;
    const checks = ids.map(id => answerMap[String(id)] === pregunta.condicion_valor);
    return pregunta.condicion_operador === 'any' ? checks.some(Boolean) : checks.every(Boolean);
  };
  const getVisiblePreguntas = (dom, answerMap = answers) =>
    dom.preguntas.filter(p => isPreguntaVisible(p, answerMap));

  const totalPreguntas = dominios.flatMap(d => getVisiblePreguntas(d)).length;
  const answeredCount  = dominios
    .flatMap(d => getVisiblePreguntas(d))
    .filter(p => hasAnswer(answers[String(p.id)]))
    .length;
  const currentDominio = step >= 0 && step < dominios.length ? dominios[step] : null;

  const isDominioComplete = (dom) =>
    getVisiblePreguntas(dom).every(p => hasAnswer(answers[String(p.id)]));

  const canGoNext = currentDominio ? isDominioComplete(currentDominio) : true;
  const pct = totalPreguntas > 0 ? Math.round((answeredCount / totalPreguntas) * 100) : 0;

  const handleAnswer = (preguntaId, valor) => {
    setAnswers(prev => {
      const next = { ...prev, [String(preguntaId)]: valor };
      dominios.flatMap(d => d.preguntas).forEach(p => {
        if (!isPreguntaVisible(p, next)) {
          delete next[String(p.id)];
        }
      });
      return next;
    });
  };

  const handleNext = async () => {
    if (!canGoNext || saving) return;
    setSaveError('');

    if (currentDominio) {
      setSaving(true);
      try {
        const respuestas = getVisiblePreguntas(currentDominio).map(p => {
          const value = answers[String(p.id)];
          return typeof value === 'number'
            ? { pregunta_id: p.id, valor: value }
            : { pregunta_id: p.id, valor_texto: value };
        });
        const res = await publicService.responder(token, { respuestas });
        if (res.data.data?.estado === 'completado') {
          setSiguienteToken(res.data.data.siguiente_guia_token || null);
          setCompleted(true);
          return;
        }
      } catch {
        setSaveError('Error al guardar las respuestas. Por favor intenta de nuevo.');
        setSaving(false);
        return;
      } finally {
        setSaving(false);
      }
    }

    if (step + 1 >= dominios.length) {
      setCompleted(true);
    } else {
      setStep(s => s + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrev = () => {
    setStep(s => s <= 0 ? -1 : s - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /* ---- Loading ---- */
  if (loading) {
    return (
      <div className={styles.screen}>
        <div className={styles.center}>
          <Loader2 size={36} className={styles.spin} />
          <p className={styles.centerText}>Cargando cuestionario...</p>
        </div>
      </div>
    );
  }

  /* ---- Error ---- */
  if (error) {
    return (
      <div className={styles.screen}>
        <div className={styles.center}>
          <div className={styles.errorIcon}><AlertCircle size={44} /></div>
          <h2 className={styles.centerTitle}>Cuestionario no disponible</h2>
          <p className={styles.centerText}>{error}</p>
        </div>
      </div>
    );
  }

  /* ---- Completado ---- */
  if (completed) {
    const claveActual    = data?.cuestionario?.clave;
    const claveSiguiente = GUIA_SIGUIENTE[claveActual];
    const haysiguiente   = !!siguienteToken;

    return (
      <div className={styles.screen}>
        <div className={styles.center}>
          <div className={styles.successIcon}><CheckCircle2 size={52} /></div>
          <h2 className={styles.centerTitle}>
            {claveActual ? `${GUIA_LABEL[claveActual]} completada` : 'Cuestionario completado'}
          </h2>
          <p className={styles.centerText}>
            Gracias, <strong>{data.trabajador_nombre}</strong>. Tus respuestas han sido registradas exitosamente.
          </p>
          {haysiguiente ? (
            <>
              <p className={styles.centerText} style={{ marginTop: 0 }}>
                Ahora debes completar la <strong>{GUIA_LABEL[claveSiguiente]}</strong>.
              </p>
              <button
                className={styles.startBtn}
                style={{ marginTop: 8 }}
                onClick={() => navigate(`/guia/${siguienteToken}`)}
              >
                Continuar a {GUIA_LABEL[claveSiguiente]}
                <ChevronRight size={18} />
              </button>
            </>
          ) : (
            <p className={styles.closeHint}>Has completado todas las guías. Puedes cerrar esta ventana.</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.screen}>
      {/* Top bar */}
      <header className={styles.topbar}>
        <div className={styles.topbarInner}>
          <img src="/logo-nom035.jpg" alt="NOM-035" className={styles.logo} />
          <div className={styles.topbarInfo}>
            <span className={styles.topbarName}>{data.trabajador_nombre}</span>
            <span className={styles.topbarSep} />
            <span className={styles.topbarQ}>{data.cuestionario.nombre}</span>
          </div>
          <span className={styles.topbarPct}>{pct}%</span>
        </div>
        <div className={styles.topbarNotices}>
          <span className={styles.topbarNotice}>
            <span className={styles.noticeNum}>1</span>
            Contesta cada una de las preguntas de manera honesta, considerando tus actividades laborales los últimos 2 meses en tu actual empleo.
          </span>
          <span className={styles.noticeDivider} />
          <span className={styles.topbarNotice}>
            <span className={styles.noticeNum}>2</span>
            Considera solo actividades dentro del lugar del trabajo y los trayectos al mismo.
          </span>
        </div>
        <div className={styles.progressOuter}>
          <div className={styles.progressInner} style={{ width: `${pct}%` }} />
        </div>
      </header>

      <main className={styles.main}>
        {step === -1 ? (
          /* ---- Intro ---- */
          <div className={styles.card}>
            <span className={styles.normChip}>NOM-035-STPS-2018</span>
            <h1 className={styles.introTitle}>{data.cuestionario.nombre}</h1>
            <p className={styles.introDesc}>
              Este cuestionario forma parte del proceso de identificación y evaluación de factores de riesgo psicosocial en el trabajo, conforme a la NOM-035-STPS-2018.
            </p>
            <ul className={styles.introList}>
              <li>Responde según tu experiencia laboral reciente y real</li>
              <li>No hay respuestas correctas ni incorrectas</li>
              <li>Tus respuestas son estrictamente confidenciales</li>
              <li>
                El cuestionario tiene <strong>{totalPreguntas} preguntas</strong> en{' '}
                <strong>{dominios.length} secciones</strong>
              </li>
            </ul>
            <div className={styles.introMeta}>
              <span>Bienvenido/a, <strong>{data.trabajador_nombre}</strong></span>
              {answeredCount > 0 && (
                <span className={styles.resumeNote}>
                  Tienes {answeredCount} respuestas guardadas. Puedes continuar donde dejaste.
                </span>
              )}
            </div>
            <button className={styles.startBtn} onClick={() => setStep(0)}>
              {answeredCount > 0 ? 'Continuar cuestionario' : 'Comenzar cuestionario'}
              <ChevronRight size={18} />
            </button>
          </div>
        ) : (
          /* ---- Domain Questions ---- */
          <div className={styles.card}>
            <div className={styles.domainMeta}>
              <span className={styles.domainBadge}>
                Sección {step + 1} de {dominios.length}
              </span>
              <div className={styles.domainDots}>
                {dominios.map((d, i) => (
                  <span
                    key={d.id}
                    className={`${styles.dot} ${i === step ? styles.dotActive : ''} ${isDominioComplete(d) ? styles.dotDone : ''}`}
                  />
                ))}
              </div>
            </div>
            <h2 className={styles.domainTitle}>{currentDominio.nombre}</h2>
            <p className={styles.instructions}>
              {getVisiblePreguntas(currentDominio).some(p => p.tipo_respuesta === 'frecuencia')
                ? 'Selecciona la frecuencia con la que se presentan las siguientes situaciones en tu trabajo:'
                : 'Responde la informacion solicitada para continuar:'}
            </p>

            {/* Scale legend */}
            {getVisiblePreguntas(currentDominio).some(p => p.tipo_respuesta === 'frecuencia') && (
              <div className={styles.legend}>
                {OPCIONES.map(o => (
                  <span key={o.valor} className={styles.legendItem}>
                    {o.label}
                  </span>
                ))}
              </div>
            )}

            {/* Questions list */}
            <div className={styles.questions}>
              {getVisiblePreguntas(currentDominio).map((pregunta, idx) => {
                const val = answers[String(pregunta.id)];
                const answered = hasAnswer(val);
                const opciones = pregunta.tipo_respuesta === 'si_no' ? OPCIONES_SI_NO : OPCIONES;
                return (
                  <div
                    key={pregunta.id}
                    className={`${styles.qItem} ${answered ? styles.qAnswered : ''}`}
                  >
                    <span className={styles.qNum}>{idx + 1}</span>
                    <div className={styles.qBody}>
                      <p className={styles.qText}>{pregunta.texto}</p>
                      {pregunta.tipo_respuesta === 'texto' ? (
                        <input
                          className={styles.textAnswer}
                          value={val || ''}
                          onChange={e => handleAnswer(pregunta.id, e.target.value)}
                        />
                      ) : pregunta.tipo_respuesta === 'opcion' ? (
                        <select
                          className={styles.selectAnswer}
                          value={val || ''}
                          onChange={e => handleAnswer(pregunta.id, e.target.value)}
                        >
                          <option value="">Selecciona una opción</option>
                          {(pregunta.opciones || []).map(opcion => (
                            <option key={opcion} value={opcion}>{opcion}</option>
                          ))}
                        </select>
                      ) : (
                        <div className={styles.options}>
                          {opciones.map(opcion => {
                            const sel = val === opcion.valor;
                            return (
                              <button
                                key={opcion.valor}
                                className={`${styles.optBtn} ${sel ? styles.optSelected : ''}`}
                                onClick={() => handleAnswer(pregunta.id, opcion.valor)}
                              >
                                <span className={styles.optCircle} />
                                <span className={styles.optLabel}>{opcion.label}</span>
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {saveError && (
              <div className={styles.saveError}>
                <AlertCircle size={14} />
                {saveError}
              </div>
            )}

            <div className={styles.navRow}>
              <button className={styles.btnBack} onClick={handlePrev} disabled={saving}>
                <ChevronLeft size={16} />
                {step === 0 ? 'Inicio' : 'Anterior'}
              </button>
              <button
                className={styles.btnNext}
                onClick={handleNext}
                disabled={!canGoNext || saving}
              >
                {saving
                  ? <Loader2 size={16} className={styles.spin} />
                  : <>
                      {step === dominios.length - 1 ? 'Finalizar' : 'Siguiente'}
                      <ChevronRight size={16} />
                    </>
                }
              </button>
            </div>
            {!canGoNext && (
              <p className={styles.validationNote}>
                Responde todas las preguntas de esta sección para continuar.
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
