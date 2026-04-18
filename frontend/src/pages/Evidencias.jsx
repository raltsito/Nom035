import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  FolderOpen, Upload, Loader2, X, Trash2,
  Download, FileText, FileSpreadsheet, Image,
  Film, Archive, File, ChevronDown, AlertTriangle,
} from 'lucide-react';
import { evidenciasService } from '../services/evidencias';
import { ciclosService } from '../services/trabajadores';
import styles from './Evidencias.module.css';

const MODULO_OPTS = [
  { value: 'comite',     label: 'Comite NOM-035',          color: 'var(--nom-accent)',   bg: 'var(--nom-accent-subtle)' },
  { value: 'plan',       label: 'Plan de Accion',           color: '#d97706',             bg: 'rgba(245,158,11,0.10)' },
  { value: 'politica',   label: 'Politica de Prevencion',   color: 'var(--nom-success)',  bg: 'var(--nom-success-subtle)' },
  { value: 'difusion',   label: 'Difusion',                 color: '#7c3aed',             bg: 'rgba(124,58,237,0.10)' },
  { value: 'aplicacion', label: 'Aplicacion de Cuestionarios', color: '#2563eb',          bg: 'rgba(59,130,246,0.10)' },
  { value: 'otro',       label: 'Otro',                     color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
];

const MODULO_MAP = Object.fromEntries(MODULO_OPTS.map(m => [m.value, m]));

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(mime) {
  if (!mime) return { Icon: File, color: '#6B7280', bg: 'var(--nom-bg-subtle)' };
  if (mime.includes('pdf'))        return { Icon: FileText,        color: '#E53E3E', bg: 'rgba(229,62,62,0.10)' };
  if (mime.includes('spreadsheet') || mime.includes('excel') || mime.includes('csv'))
    return { Icon: FileSpreadsheet, color: '#0EA870', bg: 'var(--nom-success-subtle)' };
  if (mime.includes('word') || mime.includes('document') || mime.includes('text'))
    return { Icon: FileText,        color: '#2563eb', bg: 'rgba(59,130,246,0.10)' };
  if (mime.startsWith('image/'))   return { Icon: Image,           color: '#7c3aed', bg: 'rgba(124,58,237,0.10)' };
  if (mime.startsWith('video/'))   return { Icon: Film,            color: '#d97706', bg: 'rgba(245,158,11,0.10)' };
  if (mime.includes('zip') || mime.includes('rar') || mime.includes('tar'))
    return { Icon: Archive,         color: 'var(--nom-accent)', bg: 'var(--nom-accent-subtle)' };
  return { Icon: File, color: '#6B7280', bg: 'var(--nom-bg-subtle)' };
}

const EMPTY_FORM = { modulo: 'otro', nombre: '', descripcion: '' };

export default function Evidencias() {
  const [ciclos, setCiclos]     = useState([]);
  const [cicloId, setCicloId]   = useState('');
  const [items, setItems]       = useState([]);
  const [meta, setMeta]         = useState({ count: 0, total_bytes: 0, por_modulo: {} });
  const [loading, setLoading]   = useState(false);
  const [moduloFilter, setModuloFilter] = useState('');

  const [modal, setModal]           = useState(null); // null | 'upload' | 'del'
  const [selectedFile, setSelectedFile] = useState(null);
  const [form, setForm]             = useState(EMPTY_FORM);
  const [saving, setSaving]         = useState(false);
  const [formErr, setFormErr]       = useState('');
  const [uploadPct, setUploadPct]   = useState(0);
  const [confirmDel, setConfirmDel] = useState(null);
  const [dragOver, setDragOver]     = useState(false);

  const fileInputRef = useRef(null);

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
      if (moduloFilter) params.modulo = moduloFilter;
      const res = await evidenciasService.list(params);
      setItems(res.data.data);
      setMeta(res.data.meta || { count: 0, total_bytes: 0, por_modulo: {} });
    } finally {
      setLoading(false);
    }
  }, [cicloId, moduloFilter]);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const openUploadModal = (file = null) => {
    setSelectedFile(file);
    setForm({ ...EMPTY_FORM, nombre: file ? file.name.replace(/\.[^.]+$/, '') : '' });
    setFormErr('');
    setUploadPct(0);
    setModal('upload');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) openUploadModal(file);
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) openUploadModal(file);
    e.target.value = '';
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) { setFormErr('Selecciona un archivo.'); return; }
    setFormErr('');
    setSaving(true);
    setUploadPct(0);
    try {
      const fd = new FormData();
      fd.append('archivo', selectedFile);
      fd.append('ciclo', cicloId);
      fd.append('modulo', form.modulo);
      fd.append('nombre', form.nombre || selectedFile.name);
      fd.append('descripcion', form.descripcion);

      const token = localStorage.getItem('access_token');
      const base  = import.meta.env.VITE_API_URL || '/api/v1';
      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${base}/evidencias/`);
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        xhr.upload.onprogress = (ev) => {
          if (ev.lengthComputable) setUploadPct(Math.round((ev.loaded / ev.total) * 100));
        };
        xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(xhr.responseText)));
        xhr.onerror = () => reject(new Error('Error de red.'));
        xhr.send(fd);
      });

      setModal(null);
      fetchItems();
    } catch (err) {
      try {
        const d = JSON.parse(err.message);
        setFormErr(d?.errors ? Object.values(d.errors).flat().join(' ') : 'Error al subir archivo.');
      } catch {
        setFormErr('Error al subir archivo.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = async (item) => {
    const token = localStorage.getItem('access_token');
    const base  = import.meta.env.VITE_API_URL || '/api/v1';
    const res   = await fetch(`${base}/evidencias/${item.id}/download/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const blob  = await res.blob();
    const url   = URL.createObjectURL(blob);
    const a     = document.createElement('a');
    a.href = url;
    a.download = item.nombre;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    setSaving(true);
    try {
      await evidenciasService.delete(confirmDel.id);
      setModal(null);
      setConfirmDel(null);
      fetchItems();
    } finally {
      setSaving(false);
    }
  };

  const displayedItems = items;
  const activeModulos  = MODULO_OPTS.filter(m => (meta.por_modulo || {})[m.value] > 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Gestion de Evidencias</h1>
          <p className={styles.subtitle}>Repositorio documental NOM-035 por ciclo</p>
        </div>
        <div className={styles.headerActions}>
          <div className={styles.selectWrap}>
            <select
              className={styles.select}
              value={cicloId}
              onChange={e => { setCicloId(e.target.value); setModuloFilter(''); }}
            >
              {ciclos.map(c => (
                <option key={c.id} value={c.id}>{c.anio}</option>
              ))}
            </select>
            <ChevronDown size={14} className={styles.selectIcon} />
          </div>
          <button
            className="nom-btn-pill nom-btn-primary"
            onClick={() => fileInputRef.current?.click()}
            disabled={!cicloId}
          >
            <Upload size={15} />
            Subir archivo
          </button>
          <input
            ref={fileInputRef}
            type="file"
            style={{ display: 'none' }}
            onChange={handleFileInput}
          />
        </div>
      </div>

      {loading && (
        <div className={styles.loadingWrap}>
          <Loader2 size={24} className="nom-spin" />
        </div>
      )}

      {!loading && !cicloId && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}><FolderOpen size={28} /></div>
          <p className={styles.emptyTitle}>Sin ciclos registrados</p>
          <p className={styles.emptyText}>Crea un ciclo NOM-035 para comenzar a subir evidencias.</p>
        </div>
      )}

      {!loading && cicloId && (
        <div className={styles.content}>

          {/* KPIs */}
          <div className={styles.kpiRow}>
            <div
              className={`${styles.kpiCard} ${!moduloFilter ? styles.kpiCardActive : ''}`}
              style={{ '--kpi-color': 'var(--nom-accent)' }}
              onClick={() => setModuloFilter('')}
            >
              <span className={styles.kpiNum}>{meta.count ?? items.length}</span>
              <span className={styles.kpiLabel}>Documentos</span>
            </div>
            <div className={styles.kpiCard} style={{ '--kpi-color': 'var(--nom-success)', cursor: 'default' }}>
              <span className={styles.kpiNum}>{formatBytes(meta.total_bytes)}</span>
              <span className={styles.kpiLabel}>Almacenados</span>
            </div>
            {activeModulos.map(m => (
              <div
                key={m.value}
                className={`${styles.kpiCard} ${moduloFilter === m.value ? styles.kpiCardActive : ''}`}
                style={{ '--kpi-color': m.color }}
                onClick={() => setModuloFilter(moduloFilter === m.value ? '' : m.value)}
              >
                <span className={styles.kpiNum} style={{ color: m.color }}>
                  {meta.por_modulo[m.value]}
                </span>
                <span className={styles.kpiLabel}>{m.label}</span>
              </div>
            ))}
          </div>

          {/* Drop zone */}
          <div
            className={`${styles.dropZone} ${dragOver ? styles.dropZoneOver : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <Upload size={28} className={styles.dropIcon} />
            <p className={styles.dropTitle}>Arrastra archivos aqui o haz clic para seleccionar</p>
            <p className={styles.dropSub}>PDF, Word, Excel, imagenes y mas — max 50 MB</p>
          </div>

          {/* Section header */}
          <div className={styles.sectionHeader}>
            <div className={styles.sectionTitle}>
              <FolderOpen size={18} />
              Archivos del ciclo
            </div>
            {moduloFilter && (
              <button className={styles.clearFilter} onClick={() => setModuloFilter('')}>
                <X size={11} /> Limpiar filtro
              </button>
            )}
          </div>

          {/* Files grid or empty */}
          {displayedItems.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}><FolderOpen size={28} /></div>
              <p className={styles.emptyTitle}>Sin documentos</p>
              <p className={styles.emptyText}>
                {moduloFilter
                  ? 'No hay documentos en este modulo.'
                  : 'Sube el primer documento de evidencia para este ciclo.'}
              </p>
            </div>
          ) : (
            <div className={styles.filesGrid}>
              {displayedItems.map(item => {
                const fi  = fileIcon(item.tipo_mime);
                const mod = MODULO_MAP[item.modulo];
                const Icon = fi.Icon;
                return (
                  <div key={item.id} className={styles.fileCard}>
                    <div className={styles.fileTop}>
                      <div className={styles.fileIconWrap} style={{ background: fi.bg }}>
                        <Icon size={18} color={fi.color} />
                      </div>
                      <div className={styles.fileInfo}>
                        <div className={styles.fileName}>{item.nombre}</div>
                        {item.descripcion && (
                          <div className={styles.fileDesc}>{item.descripcion}</div>
                        )}
                      </div>
                    </div>
                    <div className={styles.fileMeta}>
                      {mod && (
                        <span className={styles.chip} style={{ color: mod.color, background: mod.bg }}>
                          {mod.label}
                        </span>
                      )}
                      <span className={styles.fileMetaItem}>{formatBytes(item.tamanio)}</span>
                      {item.subido_por_nombre && (
                        <>
                          <span className={styles.fileMetaDot}>·</span>
                          <span className={styles.fileMetaItem}>{item.subido_por_nombre}</span>
                        </>
                      )}
                    </div>
                    <div className={styles.fileActions}>
                      <button
                        className={`${styles.fileBtn} ${styles.fileBtnDownload}`}
                        onClick={() => handleDownload(item)}
                      >
                        <Download size={13} />
                        Descargar
                      </button>
                      <button
                        className={`${styles.fileBtn} ${styles.fileBtnDel}`}
                        style={{ flex: '0 0 36px' }}
                        onClick={() => { setConfirmDel({ id: item.id, nombre: item.nombre }); setModal('del'); }}
                        title="Eliminar"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Upload modal */}
      {modal === 'upload' && (
        <Overlay onClick={e => e.target === e.currentTarget && !saving && setModal(null)}>
          <div className={`nom-glass ${styles.modal}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Subir documento</h2>
              <button className={styles.modalClose} onClick={() => !saving && setModal(null)} disabled={saving}>
                <X size={16} />
              </button>
            </div>
            <form className={styles.modalForm} onSubmit={handleUpload}>
              {selectedFile && (
                <div className={styles.selectedFile}>
                  <FileText size={16} color="var(--nom-accent)" />
                  <span className={styles.selectedFileName}>{selectedFile.name}</span>
                  <span className={styles.selectedFileSize}>{formatBytes(selectedFile.size)}</span>
                </div>
              )}
              <div className={styles.field}>
                <label className={styles.label}>Modulo</label>
                <select
                  className="nom-input"
                  value={form.modulo}
                  onChange={e => setForm(f => ({ ...f, modulo: e.target.value }))}
                >
                  {MODULO_OPTS.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>
              <div className={styles.field}>
                <label className={styles.label}>Nombre del documento *</label>
                <input
                  type="text"
                  className="nom-input"
                  placeholder="Nombre descriptivo del documento"
                  value={form.nombre}
                  onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))}
                  required
                />
              </div>
              <div className={styles.field}>
                <label className={styles.label}>Descripcion</label>
                <textarea
                  className="nom-input"
                  rows={2}
                  placeholder="Breve descripcion del contenido..."
                  value={form.descripcion}
                  onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
                />
              </div>
              {saving && uploadPct > 0 && (
                <div className={styles.uploadBar}>
                  <div className={styles.uploadBarTrack}>
                    <div className={styles.uploadBarFill} style={{ width: `${uploadPct}%` }} />
                  </div>
                  <span className={styles.uploadBarText}>{uploadPct}%</span>
                </div>
              )}
              {formErr && <p className={styles.formError}>{formErr}</p>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)} disabled={saving}>
                  Cancelar
                </button>
                <button type="submit" className="nom-btn-pill nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : <Upload size={14} />}
                  {saving ? `Subiendo ${uploadPct}%` : 'Subir archivo'}
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
              <h2 className={styles.modalTitle}>Eliminar documento</h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <div className={styles.confirmWrap}>
              <AlertTriangle size={20} className={styles.confirmIcon} />
              <p className={styles.confirmText}>
                Se eliminara permanentemente el archivo{' '}
                <strong>&ldquo;{confirmDel.nombre}&rdquo;</strong> del servidor. Esta accion no puede deshacerse.
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
