import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  Megaphone, Plus, FileDown, Loader2, X,
  ChevronDown, Pencil, Trash2, Users,
  AlertTriangle,
} from 'lucide-react';
import { difusionService } from '../services/difusion';
import { ciclosService } from '../services/trabajadores';
import styles from './Difusion.module.css';

const TIPO_OPTS = [
  { value: 'platica',  label: 'Platica / Capacitacion' },
  { value: 'correo',   label: 'Correo electronico' },
  { value: 'cartel',   label: 'Cartel / Material impreso' },
  { value: 'reunion',  label: 'Reunion de trabajo' },
  { value: 'intranet', label: 'Intranet / Portal interno' },
  { value: 'otro',     label: 'Otro' },
];

const TIPO_CFG = {
  platica:  { color: 'var(--nom-accent)',   bg: 'var(--nom-accent-subtle)' },
  correo:   { color: 'var(--nom-success)',  bg: 'var(--nom-success-subtle)' },
  cartel:   { color: '#7c3aed',             bg: 'rgba(124,58,237,0.10)' },
  reunion:  { color: '#d97706',             bg: 'rgba(245,158,11,0.10)' },
  intranet: { color: '#2563eb',             bg: 'rgba(59,130,246,0.10)' },
  otro:     { color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
};

const EMPTY_FORM = {
  ciclo: '', tipo: 'platica', titulo: '', descripcion: '',
  fecha: '', num_participantes: 0, responsable: '',
};

function TipoChip({ tipo, label }) {
  const c = TIPO_CFG[tipo] || TIPO_CFG.otro;
  return (
    <span className={styles.chip} style={{ color: c.color, background: c.bg }}>
      {label || tipo}
    </span>
  );
}

export default function Difusion() {
  const [ciclos, setCiclos]   = useState([]);
  const [cicloId, setCicloId] = useState('');
  const [items, setItems]     = useState([]);
  const [meta, setMeta]       = useState({ count: 0, total_participantes: 0, por_tipo: {} });
  const [loading, setLoading] = useState(false);

  const [tipoFilter, setTipoFilter] = useState('');

  const [modal, setModal]         = useState(null); // null | 'form' | 'del'
  const [editTarget, setEditTarget] = useState(null);
  const [confirmDel, setConfirmDel] = useState(null); // { id, titulo }

  const [form, setForm]       = useState(EMPTY_FORM);
  const [saving, setSaving]   = useState(false);
  const [formErr, setFormErr] = useState('');

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchItems = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    try {
      const params = { ciclo_id: cicloId };
      if (tipoFilter) params.tipo = tipoFilter;
      const res = await difusionService.list(params);
      setItems(res.data.data);
      setMeta(res.data.meta || { count: 0, total_participantes: 0, por_tipo: {} });
    } finally {
      setLoading(false);
    }
  }, [cicloId, tipoFilter]);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const openCreate = () => {
    setEditTarget(null);
    setForm({ ...EMPTY_FORM, ciclo: cicloId });
    setFormErr('');
    setModal('form');
  };

  const openEdit = (item) => {
    setEditTarget(item);
    setForm({
      ciclo:            String(item.ciclo),
      tipo:             item.tipo,
      titulo:           item.titulo,
      descripcion:      item.descripcion || '',
      fecha:            item.fecha,
      num_participantes: item.num_participantes,
      responsable:      item.responsable || '',
    });
    setFormErr('');
    setModal('form');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setFormErr('');
    setSaving(true);
    try {
      if (editTarget) {
        await difusionService.update(editTarget.id, form);
      } else {
        await difusionService.create(form);
      }
      setModal(null);
      fetchItems();
    } catch (err) {
      const d = err.response?.data;
      const msg = d?.errors
        ? Object.values(d.errors).flat().join(' ')
        : 'Error al guardar.';
      setFormErr(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    setSaving(true);
    try {
      await difusionService.delete(confirmDel.id);
      setModal(null);
      setConfirmDel(null);
      fetchItems();
    } finally {
      setSaving(false);
    }
  };

  const handleReporte = async () => {
    if (!cicloId) return;
    const token = localStorage.getItem('access_token');
    const base  = import.meta.env.VITE_API_URL || '/api/v1';
    const url   = `${base}/actividades-difusion/reporte/?ciclo_id=${cicloId}`;
    const res   = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) return;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('pdf')) {
      const blob = await res.blob();
      const burl = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      const ciclo = ciclos.find(c => String(c.id) === cicloId);
      a.href = burl; a.download = `difusion_nom035_${ciclo?.anio || cicloId}.pdf`;
      a.click(); URL.revokeObjectURL(burl);
    } else {
      const html = await res.text();
      const w    = window.open('', '_blank');
      w.document.write(html); w.document.close();
    }
  };

  const displayedItems = tipoFilter
    ? items.filter(i => i.tipo === tipoFilter)
    : items;

  const kpiTipos = TIPO_OPTS.filter(t => (meta.por_tipo || {})[t.value] > 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Centro de Difusion</h1>
          <p className={styles.subtitle}>Actividades de difusion NOM-035 &mdash; Art. 16</p>
        </div>
        <div className={styles.headerActions}>
          <div className={styles.selectWrap}>
            <select
              className={styles.select}
              value={cicloId}
              onChange={e => { setCicloId(e.target.value); setTipoFilter(''); }}
            >
              {ciclos.map(c => (
                <option key={c.id} value={c.id}>{c.anio}</option>
              ))}
            </select>
            <ChevronDown size={14} className={styles.selectIcon} />
          </div>
          <button className="nom-btn-pill nom-btn-ghost" onClick={handleReporte} disabled={!cicloId}>
            <FileDown size={15} />
            Reporte
          </button>
          <button className="nom-btn-pill nom-btn-primary" onClick={openCreate} disabled={!cicloId}>
            <Plus size={15} />
            Nueva actividad
          </button>
        </div>
      </div>

      {loading && (
        <div className={styles.loadingWrap}>
          <Loader2 size={24} className="nom-spin" />
        </div>
      )}

      {!loading && !cicloId && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}><Megaphone size={28} /></div>
          <p className={styles.emptyTitle}>Sin ciclos registrados</p>
          <p className={styles.emptyText}>Crea un ciclo NOM-035 para comenzar a registrar actividades de difusion.</p>
        </div>
      )}

      {!loading && cicloId && (
        <div className={styles.content}>

          {/* KPIs */}
          <div className={styles.kpiRow}>
            <div
              className={`${styles.kpiCard} ${!tipoFilter ? styles.kpiCardActive : ''}`}
              style={{ '--kpi-color': 'var(--nom-accent)' }}
              onClick={() => setTipoFilter('')}
            >
              <span className={styles.kpiNum}>{meta.count ?? items.length}</span>
              <span className={styles.kpiLabel}>Actividades</span>
            </div>
            <div className={styles.kpiCard} style={{ '--kpi-color': 'var(--nom-success)', cursor: 'default' }}>
              <span className={styles.kpiNum}>{meta.total_participantes ?? 0}</span>
              <span className={styles.kpiLabel}>Participantes</span>
            </div>
            {kpiTipos.map(t => {
              const c = TIPO_CFG[t.value] || TIPO_CFG.otro;
              return (
                <div
                  key={t.value}
                  className={`${styles.kpiCard} ${tipoFilter === t.value ? styles.kpiCardActive : ''}`}
                  style={{ '--kpi-color': c.color }}
                  onClick={() => setTipoFilter(tipoFilter === t.value ? '' : t.value)}
                >
                  <span className={styles.kpiNum} style={{ color: c.color }}>
                    {meta.por_tipo[t.value]}
                  </span>
                  <span className={styles.kpiLabel}>{t.label}</span>
                </div>
              );
            })}
          </div>

          {/* Section header */}
          <div className={styles.sectionHeader}>
            <div className={styles.sectionTitle}>
              <Users size={18} />
              Actividades registradas
            </div>
            {tipoFilter && (
              <button className={styles.clearFilter} onClick={() => setTipoFilter('')}>
                <X size={11} /> Limpiar filtro
              </button>
            )}
          </div>

          {/* Table or empty */}
          {displayedItems.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}><Megaphone size={28} /></div>
              <p className={styles.emptyTitle}>Sin actividades</p>
              <p className={styles.emptyText}>
                {tipoFilter
                  ? 'No hay actividades del tipo seleccionado.'
                  : 'Registra la primera actividad de difusion para este ciclo.'}
              </p>
            </div>
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead className={styles.thead}>
                  <tr>
                    <th>Tipo</th>
                    <th>Titulo / Descripcion</th>
                    <th>Fecha</th>
                    <th style={{ textAlign: 'center' }}>Participantes</th>
                    <th>Responsable</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {displayedItems.map(item => (
                    <tr key={item.id} className={styles.tr}>
                      <td>
                        <TipoChip tipo={item.tipo} label={item.tipo_label} />
                      </td>
                      <td className={styles.tdTitulo}>
                        <div className={styles.tituloText}>{item.titulo}</div>
                        {item.descripcion && (
                          <div className={styles.descText}>{item.descripcion}</div>
                        )}
                      </td>
                      <td className={styles.tdMuted}>{item.fecha}</td>
                      <td className={styles.tdCenter}>{item.num_participantes}</td>
                      <td className={styles.tdMuted}>{item.responsable || '—'}</td>
                      <td>
                        <div className={styles.rowActions}>
                          <button className={styles.rowBtn} onClick={() => openEdit(item)} title="Editar">
                            <Pencil size={14} />
                          </button>
                          <button
                            className={`${styles.rowBtn} ${styles.rowBtnDanger}`}
                            onClick={() => { setConfirmDel({ id: item.id, titulo: item.titulo }); setModal('del'); }}
                            title="Eliminar"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Form modal */}
      {modal === 'form' && (
        <Overlay onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className={`nom-glass ${styles.modal}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {editTarget ? 'Editar actividad' : 'Nueva actividad'}
              </h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <form className={styles.modalForm} onSubmit={handleSave}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Tipo *</label>
                  <select
                    className="nom-input"
                    value={form.tipo}
                    onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}
                    required
                  >
                    {TIPO_OPTS.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha *</label>
                  <input
                    type="date"
                    className="nom-input"
                    value={form.fecha}
                    onChange={e => setForm(f => ({ ...f, fecha: e.target.value }))}
                    required
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Titulo *</label>
                  <input
                    type="text"
                    className="nom-input"
                    placeholder="Ej. Platica informativa NOM-035 para personal operativo"
                    value={form.titulo}
                    onChange={e => setForm(f => ({ ...f, titulo: e.target.value }))}
                    required
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Descripcion</label>
                  <textarea
                    className="nom-input"
                    rows={3}
                    placeholder="Descripcion breve de la actividad..."
                    value={form.descripcion}
                    onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Num. participantes</label>
                  <input
                    type="number"
                    className="nom-input"
                    min={0}
                    value={form.num_participantes}
                    onChange={e => setForm(f => ({ ...f, num_participantes: Number(e.target.value) }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Responsable</label>
                  <input
                    type="text"
                    className="nom-input"
                    placeholder="Nombre del responsable"
                    value={form.responsable}
                    onChange={e => setForm(f => ({ ...f, responsable: e.target.value }))}
                  />
                </div>
              </div>
              {formErr && <p className={styles.formError}>{formErr}</p>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)}>
                  Cancelar
                </button>
                <button type="submit" className="nom-btn-pill nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {editTarget ? 'Guardar cambios' : 'Registrar actividad'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirm delete modal */}
      {modal === 'del' && confirmDel && (
        <Overlay onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className={`nom-glass ${styles.modal} ${styles.modalSm}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Eliminar actividad</h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <div className={styles.confirmWrap}>
              <AlertTriangle size={20} className={styles.confirmIcon} />
              <p className={styles.confirmText}>
                Esta accion es permanente. Se eliminara la actividad{' '}
                <strong>&ldquo;{confirmDel.titulo}&rdquo;</strong> y no podra recuperarse.
              </p>
            </div>
            <div className={styles.modalActions}>
              <button className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)}>Cancelar</button>
              <button className={styles.btnDanger} onClick={handleDelete} disabled={saving}>
                {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
