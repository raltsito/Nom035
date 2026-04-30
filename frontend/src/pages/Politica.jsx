import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  FileText, Plus, FileDown, Loader2, X,
  ChevronDown, Pencil, CheckCircle2, Clock,
  Archive, ShieldCheck, AlertTriangle,
} from 'lucide-react';
import { politicaService } from '../services/politica';
import { ciclosService } from '../services/trabajadores';
import styles from './Politica.module.css';

const ESTADO_CFG = {
  borrador:  { label: 'Borrador',  icon: Clock,         color: '#d97706',             bg: 'rgba(245,158,11,0.10)' },
  vigente:   { label: 'Vigente',   icon: CheckCircle2,  color: 'var(--nom-success)',  bg: 'var(--nom-success-subtle)' },
  archivada: { label: 'Archivada', icon: Archive,       color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
};

const PLANTILLA = `La empresa [NOMBRE DE LA EMPRESA], con fundamento en la Norma Oficial Mexicana NOM-035-STPS-2018, Factores de Riesgo Psicosocial en el Trabajo - Identificación, Análisis y Prevención, se compromete a:

1. Promover un entorno organizacional favorable que prevenga los factores de riesgo psicosocial en el trabajo.

2. Identificar y analizar los factores de riesgo psicosocial y el entorno organizacional, con la participación de los trabajadores.

3. Adoptar las medidas para prevenir y controlar los factores de riesgo psicosocial, así como para promover el entorno organizacional favorable.

4. Realizar evaluaciones periódicas de los factores de riesgo psicosocial y del entorno organizacional.

5. Difundir y proporcionar información a los trabajadores sobre los factores de riesgo psicosocial identificados y las medidas de prevención adoptadas.

6. Atender las prácticas opuestas al entorno organizacional favorable y los actos de violencia laboral que se detecten en el centro de trabajo.

7. Proporcionar atención psicológica preventiva a los trabajadores que lo requieran.

La presente política entrará en vigor a partir de su firma y tendrá vigencia durante el ciclo de evaluación correspondiente.`;

const EMPTY_FORM = {
  ciclo:            '',
  titulo:           'Política de Prevención de Factores de Riesgo Psicosocial',
  contenido:        PLANTILLA,
  firmante_nombre:  '',
  firmante_puesto:  '',
  fecha_aprobacion: '',
};

function EstadoChip({ estado }) {
  const c    = ESTADO_CFG[estado] || ESTADO_CFG.borrador;
  const Icon = c.icon;
  return (
    <span className={styles.estadoChip} style={{ color: c.color, background: c.bg }}>
      <Icon size={11} strokeWidth={2.5} />
      {c.label}
    </span>
  );
}

export default function Politica() {
  const [ciclos, setCiclos]     = useState([]);
  const [cicloId, setCicloId]   = useState('');
  const [politica, setPolitica] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [previewing, setPreviewing] = useState(false);

  const [modal, setModal]         = useState(null); // null | 'edit' | 'confirm-aprobar'
  const [form, setForm]           = useState(EMPTY_FORM);
  const [saving, setSaving]       = useState(false);
  const [formErr, setFormErr]     = useState('');
  const [aprobando, setAprobando] = useState(false);

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchPolitica = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    try {
      const res = await politicaService.list({ ciclo_id: cicloId });
      setPolitica(res.data.data[0] || null);
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { fetchPolitica(); }, [fetchPolitica]);

  const openCreate = () => {
    setForm({ ...EMPTY_FORM, ciclo: cicloId });
    setFormErr('');
    setModal('edit');
  };

  const openEdit = () => {
    setForm({
      ciclo:            String(politica.ciclo),
      titulo:           politica.titulo,
      contenido:        politica.contenido,
      firmante_nombre:  politica.firmante_nombre || '',
      firmante_puesto:  politica.firmante_puesto || '',
      fecha_aprobacion: politica.fecha_aprobacion || '',
    });
    setFormErr('');
    setModal('edit');
  };

  const closeModal = () => { setModal(null); setFormErr(''); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true); setFormErr('');
    try {
      const payload = { ...form, ciclo: Number(form.ciclo) };
      if (politica) {
        await politicaService.update(politica.id, payload);
      } else {
        await politicaService.create(payload);
      }
      closeModal();
      fetchPolitica();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormErr(errors ? Object.values(errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const handleAprobar = async () => {
    setAprobando(true);
    try {
      await politicaService.aprobar(politica.id);
      setModal(null);
      fetchPolitica();
    } finally {
      setAprobando(false);
    }
  };

  const handleDescargar = () => {
    if (!politica) return;
    const token = localStorage.getItem('access_token') || '';
    fetch(`/api/v1/politica/${politica.id}/pdf/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => {
      const ct = r.headers.get('content-type') || '';
      const cd = r.headers.get('content-disposition') || '';
      if (ct.includes('text/html')) {
        return r.text().then(html => {
          const w = window.open('', '_blank');
          w.document.write(html); w.document.close();
        });
      }
      return r.blob().then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = cd.match(/filename="?([^";]+)"?/)?.[1] || `politica_nom035_${cicloId}.pdf`;
        a.click();
        URL.revokeObjectURL(a.href);
      });
    }).catch(() => alert('Error al generar el PDF.'));
  };

  const cicloAnio = ciclos.find(c => String(c.id) === cicloId)?.anio || cicloId;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Politica de Prevencion</h1>
          <p className={styles.subtitle}>Politica de prevencion de factores de riesgo psicosocial NOM-035</p>
        </div>
        <div className={styles.headerActions}>
          {ciclos.length > 0 && (
            <div className={styles.selectWrap}>
              <ChevronDown size={14} className={styles.selectIcon} />
              <select className={styles.select} value={cicloId} onChange={e => setCicloId(e.target.value)}>
                {ciclos.map(c => <option key={c.id} value={c.id}>Ciclo {c.anio}</option>)}
              </select>
            </div>
          )}
          {politica && (
            <button className="nom-btn nom-btn-ghost" onClick={handleDescargar}>
              <FileDown size={15} strokeWidth={2} /> Descargar PDF
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : !politica ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}><FileText size={36} strokeWidth={1.25} /></div>
          <h2 className={styles.emptyTitle}>Sin politica registrada</h2>
          <p className={styles.emptyText}>
            Redacta la politica de prevencion de riesgos psicosociales para el ciclo {cicloAnio}.
            Puedes usar la plantilla predefinida como punto de partida.
          </p>
          <button className="nom-btn nom-btn-primary" onClick={openCreate} disabled={!cicloId}>
            <Plus size={15} /> Redactar politica
          </button>
        </div>
      ) : (
        <div className={styles.content}>
          {/* Status bar */}
          <div className={`${styles.statusBar} nom-card`}>
            <div className={styles.statusLeft}>
              <div className={styles.statusIcon}>
                <ShieldCheck size={20} strokeWidth={1.75} />
              </div>
              <div>
                <div className={styles.statusTitle}>{politica.titulo}</div>
                <div className={styles.statusMeta}>
                  <EstadoChip estado={politica.estado} />
                  {politica.fecha_aprobacion && (
                    <span className={styles.metaDot}>
                      Aprobada el {new Date(politica.fecha_aprobacion + 'T00:00:00').toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })}
                    </span>
                  )}
                  {politica.firmante_nombre && (
                    <span className={styles.metaDot}>Firmante: {politica.firmante_nombre}</span>
                  )}
                </div>
              </div>
            </div>
            <div className={styles.statusActions}>
              {politica.estado === 'borrador' && (
                <button
                  className="nom-btn nom-btn-primary"
                  onClick={() => setModal('confirm-aprobar')}
                >
                  <CheckCircle2 size={14} /> Aprobar y publicar
                </button>
              )}
              <button className={styles.editBtn} onClick={openEdit}>
                <Pencil size={13} strokeWidth={1.75} /> Editar
              </button>
            </div>
          </div>

          {/* Preview toggle */}
          <div className={styles.previewToggle}>
            <button
              className={`${styles.tabBtn} ${!previewing ? styles.tabBtnActive : ''}`}
              onClick={() => setPreviewing(false)}
            >
              Contenido
            </button>
            <button
              className={`${styles.tabBtn} ${previewing ? styles.tabBtnActive : ''}`}
              onClick={() => setPreviewing(true)}
            >
              Vista previa
            </button>
          </div>

          {/* Body */}
          {previewing ? (
            <div className={`${styles.previewCard} nom-card`}>
              <div className={styles.previewHeader}>
                <div className={styles.previewTitle}>{politica.titulo}</div>
                <div className={styles.previewMeta}>{politica.firmante_nombre || '—'} · Ciclo {politica.ciclo_anio}</div>
              </div>
              <div className={styles.previewBody}>{politica.contenido}</div>
              {(politica.firmante_nombre || politica.firmante_puesto) && (
                <div className={styles.previewSig}>
                  <div className={styles.sigLine} />
                  <div className={styles.sigName}>{politica.firmante_nombre}</div>
                  {politica.firmante_puesto && <div className={styles.sigPuesto}>{politica.firmante_puesto}</div>}
                </div>
              )}
            </div>
          ) : (
            <div className={`${styles.contentCard} nom-card`}>
              <div className={styles.contentText}>{politica.contenido}</div>
            </div>
          )}
        </div>
      )}

      {/* ---- Modal editar/crear ---- */}
      {modal === 'edit' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} ${styles.modalXl} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{politica ? 'Editar politica' : 'Redactar politica'}</h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSave} className={styles.modalForm}>
              <div className={styles.field}>
                <label className={styles.label}>Titulo del documento</label>
                <input
                  className="nom-input"
                  value={form.titulo}
                  onChange={e => setForm(f => ({ ...f, titulo: e.target.value }))}
                  required
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Contenido de la politica *</label>
                <textarea
                  className={`nom-input ${styles.contentArea}`}
                  value={form.contenido}
                  onChange={e => setForm(f => ({ ...f, contenido: e.target.value }))}
                  rows={14}
                  required
                />
              </div>

              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Nombre del firmante</label>
                  <input
                    className="nom-input"
                    placeholder="Representante legal o responsable"
                    value={form.firmante_nombre}
                    onChange={e => setForm(f => ({ ...f, firmante_nombre: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Puesto del firmante</label>
                  <input
                    className="nom-input"
                    placeholder="Director General, RRHH..."
                    value={form.firmante_puesto}
                    onChange={e => setForm(f => ({ ...f, firmante_puesto: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha de aprobacion</label>
                  <input
                    className="nom-input"
                    type="date"
                    value={form.fecha_aprobacion}
                    onChange={e => setForm(f => ({ ...f, fecha_aprobacion: e.target.value }))}
                  />
                </div>
              </div>

              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : 'Guardar politica'}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* ---- Confirm aprobar ---- */}
      {modal === 'confirm-aprobar' && (
        <Overlay onClick={() => setModal(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Aprobar y publicar politica</h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={18} /></button>
            </div>
            <div className={styles.confirmWrap}>
              <CheckCircle2 size={30} className={styles.confirmIconOk} />
              <p className={styles.confirmText}>
                La politica pasara a estado <strong>Vigente</strong>. Asegurate de que el contenido
                y los datos del firmante sean correctos antes de aprobar.
              </p>
            </div>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setModal(null)}>Cancelar</button>
              <button className="nom-btn nom-btn-primary" onClick={handleAprobar} disabled={aprobando}>
                {aprobando ? <Loader2 size={14} className="nom-spin" /> : <CheckCircle2 size={14} />}
                {aprobando ? 'Aprobando...' : 'Confirmar aprobacion'}
              </button>
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}
