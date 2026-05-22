import { useState, useEffect } from 'react';
import { Settings, Building2, Globe, Phone, MapPin, Image, Loader2, CheckCircle2, Save } from 'lucide-react';
import { configuracionService } from '../services/configuracion';
import styles from './Configuracion.module.css';

export default function Configuracion() {
  const [data, setData]     = useState(null);
  const [form, setForm]     = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved]   = useState(false);
  const [error, setError]   = useState('');

  useEffect(() => {
    configuracionService.get().then(res => {
      const d = res.data.data;
      setData(d);
      setForm({
        giro:              d.giro || '',
        num_trabajadores:  d.num_trabajadores || 0,
        logo_url:          d.logo_url || '',
        sitio_web:         d.sitio_web || '',
        telefono_contacto: d.telefono_contacto || '',
        direccion:         d.direccion || '',
      });
    }).finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const res = await configuracionService.update(form);
      setData(res.data.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      const d = err.response?.data;
      setError(d?.errors ? Object.values(d.errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingWrap}><Loader2 size={24} className="nom-spin" /></div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Configuracion de empresa</h1>
          <p className={styles.subtitle}>Personaliza la informacion y marca de tu empresa en NOM-035</p>
        </div>
      </div>

      <div className={styles.layout}>
        {/* Info card */}
        <div className={`nom-glass ${styles.infoCard}`}>
          <div className={styles.infoHeader}>
            <div className={styles.infoIconWrap}>
              {data?.logo_url ? (
                <img src={data.logo_url} alt="Logo" className={styles.logoPreview} />
              ) : (
                <Building2 size={28} color="var(--nom-accent)" />
              )}
            </div>
            <div>
              <div className={styles.infoNombre}>{data?.nombre}</div>
              <div className={styles.infoRfc}>{data?.rfc}</div>
            </div>
          </div>
          <div className={styles.infoDivider} />
          <div className={styles.infoMeta}>
            {data?.sitio_web && (
              <div className={styles.infoMetaItem}>
                <Globe size={13} color="var(--nom-text-muted)" />
                <span>{data.sitio_web}</span>
              </div>
            )}
            {data?.telefono_contacto && (
              <div className={styles.infoMetaItem}>
                <Phone size={13} color="var(--nom-text-muted)" />
                <span>{data.telefono_contacto}</span>
              </div>
            )}
            {data?.direccion && (
              <div className={styles.infoMetaItem}>
                <MapPin size={13} color="var(--nom-text-muted)" />
                <span>{data.direccion}</span>
              </div>
            )}
            {!data?.sitio_web && !data?.telefono_contacto && !data?.direccion && (
              <p className={styles.infoEmpty}>Completa tu perfil de empresa</p>
            )}
          </div>
        </div>

        {/* Form */}
        <div className={`nom-glass ${styles.formCard}`}>
          <div className={styles.formCardHeader}>
            <Settings size={18} color="var(--nom-accent)" />
            <span className={styles.formCardTitle}>Informacion de la empresa</span>
          </div>

          <form onSubmit={handleSave} className={styles.form}>
            <div className={styles.formSection}>
              <div className={styles.sectionLabel}>Datos generales</div>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Giro o actividad</label>
                  <input
                    type="text"
                    className="nom-input"
                    placeholder="Ej. Manufactura automotriz"
                    value={form.giro}
                    onChange={e => setForm(f => ({ ...f, giro: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Num. trabajadores</label>
                  <input
                    type="number"
                    className="nom-input"
                    min={1}
                    value={form.num_trabajadores}
                    onChange={e => setForm(f => ({ ...f, num_trabajadores: Number(e.target.value) }))}
                  />
                </div>
              </div>
            </div>

            <div className={styles.formSection}>
              <div className={styles.sectionLabel}>Marca e identidad</div>
              <div className={styles.field}>
                <label className={styles.label}>
                  <Image size={13} /> URL del logo
                </label>
                <input
                  type="url"
                  className="nom-input"
                  placeholder="https://tuempresa.com/logo.png"
                  value={form.logo_url}
                  onChange={e => setForm(f => ({ ...f, logo_url: e.target.value }))}
                />
                {form.logo_url && (
                  <div className={styles.logoPreviewWrap}>
                    <img src={form.logo_url} alt="Vista previa" className={styles.logoPreviewSm} onError={e => e.target.style.display = 'none'} />
                  </div>
                )}
              </div>
              <div className={styles.field}>
                <label className={styles.label}>
                  <Globe size={13} /> Sitio web
                </label>
                <input
                  type="url"
                  className="nom-input"
                  placeholder="https://tuempresa.com"
                  value={form.sitio_web}
                  onChange={e => setForm(f => ({ ...f, sitio_web: e.target.value }))}
                />
              </div>
            </div>

            <div className={styles.formSection}>
              <div className={styles.sectionLabel}>Contacto y ubicacion</div>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>
                    <Phone size={13} /> Telefono
                  </label>
                  <input
                    type="text"
                    className="nom-input"
                    placeholder="(55) 1234-5678"
                    value={form.telefono_contacto}
                    onChange={e => setForm(f => ({ ...f, telefono_contacto: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>
                    <MapPin size={13} /> Direccion
                  </label>
                  <input
                    type="text"
                    className="nom-input"
                    placeholder="Calle, Colonia, Ciudad, CP"
                    value={form.direccion}
                    onChange={e => setForm(f => ({ ...f, direccion: e.target.value }))}
                  />
                </div>
              </div>
            </div>

            {error && <p className={styles.formError}>{error}</p>}

            <div className={styles.formActions}>
              {saved && (
                <div className={styles.savedMsg}>
                  <CheckCircle2 size={15} color="var(--nom-success)" />
                  Cambios guardados
                </div>
              )}
              <button type="submit" className="nom-btn-pill nom-btn-primary" disabled={saving}>
                {saving ? <Loader2 size={14} className="nom-spin" /> : <Save size={14} />}
                Guardar cambios
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
