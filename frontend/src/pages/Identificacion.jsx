import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, AlertCircle, ChevronRight, User, ArrowLeft, Lock } from 'lucide-react';
import { publicService } from '../services/cuestionarios';
import styles from './Identificacion.module.css';

const GUIA_LABEL = { V: 'Guía V', III: 'Guía III', I: 'Guía I' };

export default function Identificacion() {
  const { token }   = useParams();
  const navigate    = useNavigate();

  const [guia,        setGuia]        = useState(null);
  const [loadingGuia, setLoadingGuia] = useState(true);
  const [linkError,   setLinkError]   = useState('');

  const [step,        setStep]        = useState('form');   // 'form' | 'confirm' | 'blocked'
  const [bloqueo,     setBloqueo]     = useState(null);
  const [numEmpleado, setNumEmpleado] = useState('');
  const [buscando,    setBuscando]    = useState(false);
  const [formError,   setFormError]   = useState('');

  const [trabajador,  setTrabajador]  = useState(null);
  const [confirmando, setConfirmando] = useState(false);

  const inputRef = useRef(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await publicService.getGuiaLink(token);
        setGuia(res.data.data);
      } catch {
        setLinkError('Este enlace no es válido o ya no está disponible.');
      } finally {
        setLoadingGuia(false);
      }
    })();
  }, [token]);

  useEffect(() => {
    if (step === 'form' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [step]);

  const handleBuscar = async (e) => {
    e.preventDefault();
    if (!numEmpleado.trim()) return;
    setBuscando(true);
    setFormError('');
    try {
      const res = await publicService.identificar(token, { num_empleado: numEmpleado.trim() });
      setTrabajador(res.data.data);
      setStep('confirm');
    } catch (err) {
      const e = err.response?.data?.errors;
      setFormError(
        e?.num_empleado?.[0] || e?.detail || 'Número no encontrado. Verifica e intenta de nuevo.'
      );
    } finally {
      setBuscando(false);
    }
  };

  const handleConfirmar = async () => {
    setConfirmando(true);
    try {
      const res = await publicService.confirmar(token, { trabajador_id: trabajador.trabajador_id });
      navigate(`/responder/${res.data.data.aplicacion_token}`, { replace: true });
    } catch (err) {
      const errors = err.response?.data?.errors;
      if (errors?.bloqueado) {
        setBloqueo(errors);
        setStep('blocked');
      } else {
        setStep('form');
        setFormError('Ocurrió un error. Intenta de nuevo.');
      }
      setConfirmando(false);
    }
  };

  /* ---- Cargando el link ---- */
  if (loadingGuia) {
    return (
      <div className={styles.screen}>
        <div className={styles.center}>
          <Loader2 size={36} className={styles.spin} />
        </div>
      </div>
    );
  }

  /* ---- Link inválido ---- */
  if (linkError) {
    return (
      <div className={styles.screen}>
        <div className={styles.center}>
          <div className={styles.errorIcon}><AlertCircle size={40} /></div>
          <h2 className={styles.centerTitle}>Enlace no disponible</h2>
          <p className={styles.centerText}>{linkError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.screen}>
      <header className={styles.topbar}>
        <div className={styles.topbarInner}>
          <img src="/logo-nom035.jpg" alt="NOM-035" className={styles.logo} />
          <span className={styles.topbarGuia}>
            NOM-035 · {guia.cuestionario_nombre}
          </span>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.card}>

          {step === 'blocked' ? (
            <>
              <div className={styles.iconWrap} style={{ background: 'rgba(229,62,62,0.1)', color: '#E53E3E' }}>
                <Lock size={26} strokeWidth={1.75} />
              </div>
              <h1 className={styles.title}>Guía bloqueada</h1>
              <p className={styles.desc}>
                Para contestar esta guía primero debes completar la{' '}
                <strong>{GUIA_LABEL[bloqueo?.guia_requerida]}</strong>.
              </p>
              <div className={styles.bloqueoBox}>
                <div className={styles.bloqueoOrden}>
                  {['V', 'III', 'I'].map((g, i) => {
                    const esCurrent = g === guia?.cuestionario_clave;
                    const esReq     = g === bloqueo?.guia_requerida;
                    return (
                      <div key={g} className={`${styles.bloqueoStep} ${esCurrent ? styles.bloqueoStepCurrent : ''} ${esReq ? styles.bloqueoStepReq : ''}`}>
                        {esReq && <span className={styles.bloqueoTag}>Completa primero</span>}
                        <span className={styles.bloqueoGuia}>{GUIA_LABEL[g]}</span>
                        {i < 2 && <span className={styles.bloqueoArrow}>→</span>}
                      </div>
                    );
                  })}
                </div>
              </div>
              <button
                className={styles.btnGhost}
                onClick={() => { setStep('form'); setTrabajador(null); setBloqueo(null); }}
                style={{ width: '100%', marginTop: 4 }}
              >
                <ArrowLeft size={15} />
                Volver
              </button>
            </>
          ) : step === 'form' ? (
            <>
              <div className={styles.iconWrap}>
                <User size={28} strokeWidth={1.75} />
              </div>
              <h1 className={styles.title}>Identifícate</h1>
              <p className={styles.desc}>
                Ingresa tu número de trabajador para comenzar el cuestionario.
              </p>

              <form onSubmit={handleBuscar} className={styles.form}>
                <label className={styles.label} htmlFor="num_empleado">
                  Número de trabajador
                </label>
                <input
                  ref={inputRef}
                  id="num_empleado"
                  type="text"
                  className={styles.input}
                  placeholder="Ej. 001234"
                  value={numEmpleado}
                  onChange={e => { setNumEmpleado(e.target.value); setFormError(''); }}
                  autoComplete="off"
                  disabled={buscando}
                />

                {formError && (
                  <div className={styles.errorBox}>
                    <AlertCircle size={14} />
                    <span>{formError}</span>
                  </div>
                )}

                <button
                  type="submit"
                  className={styles.btnPrimary}
                  disabled={buscando || !numEmpleado.trim()}
                >
                  {buscando
                    ? <Loader2 size={16} className={styles.spin} />
                    : <>Continuar <ChevronRight size={16} /></>
                  }
                </button>
              </form>
            </>
          ) : (
            <>
              <div className={styles.iconWrap} style={{ background: 'rgba(14,168,112,0.1)', color: '#0EA870' }}>
                <User size={28} strokeWidth={1.75} />
              </div>
              <h1 className={styles.title}>¿Eres tú?</h1>
              <p className={styles.desc}>
                Confirma que los siguientes datos son los tuyos antes de continuar.
              </p>

              <div className={styles.workerCard}>
                <div className={styles.workerNum}>No. {trabajador.num_empleado}</div>
                <div className={styles.workerName}>{trabajador.nombre_completo}</div>
                {trabajador.puesto && (
                  <div className={styles.workerPuesto}>{trabajador.puesto}</div>
                )}
              </div>

              <div className={styles.confirmActions}>
                <button
                  className={styles.btnGhost}
                  onClick={() => { setStep('form'); setTrabajador(null); }}
                  disabled={confirmando}
                >
                  <ArrowLeft size={15} />
                  No soy yo
                </button>
                <button
                  className={styles.btnPrimary}
                  onClick={handleConfirmar}
                  disabled={confirmando}
                >
                  {confirmando
                    ? <Loader2 size={16} className={styles.spin} />
                    : <>Sí, soy yo <ChevronRight size={16} /></>
                  }
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
