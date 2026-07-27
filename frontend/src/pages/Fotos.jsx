import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Loader2, Camera, X, ChevronLeft, ChevronRight, AlertTriangle, FileDown,
} from 'lucide-react';
import { fotosService } from '../services/resultados';
import styles from './Fotos.module.css';

const POR_PAGINA = 60;

export default function Fotos() {
  const [params]   = useSearchParams();
  const navigate   = useNavigate();
  const cicloId    = params.get('ciclo') || '';

  const [items, setItems]     = useState([]);
  const [meta, setMeta]       = useState(null);
  const [pagina, setPagina]   = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  // Foto abierta en grande: la imagen de 640 px se descarga solo aquí.
  const [visor, setVisor]     = useState(null);
  const [descargandoAnexo, setDescargandoAnexo] = useState(false);

  const cargar = useCallback(async (page) => {
    if (!cicloId) { setError('No se indicó el ciclo.'); return; }
    setLoading(true);
    setError('');
    try {
      const res = await fotosService.listado(cicloId, page, POR_PAGINA);
      setItems(res.data.data || []);
      setMeta(res.data.meta || null);
    } catch (err) {
      const detalle = err?.response?.data?.errors?.detalle?.[0];
      setError(detalle || 'No se pudo cargar el informe fotográfico.');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { cargar(pagina); }, [cargar, pagina]);

  const abrirFoto = async (item) => {
    setVisor({ ...item, url: null });
    try {
      const res = await fotosService.imagen(item.id);
      setVisor(v => (v && v.id === item.id ? { ...v, url: URL.createObjectURL(res.data) } : v));
    } catch {
      setVisor(v => (v && v.id === item.id ? { ...v, fallo: true } : v));
    }
  };

  const descargarAnexo = async () => {
    if (!cicloId || descargandoAnexo) return;
    setDescargandoAnexo(true);
    try {
      const res = await fotosService.anexo(cicloId);
      const nombre = /filename="([^"]+)"/.exec(res.headers['content-disposition'] || '')?.[1]
        || `Anexo_Fotografico_NOM035_ciclo_${cicloId}.docx`;
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert('No se pudo generar el anexo de fotos.');
    } finally {
      setDescargandoAnexo(false);
    }
  };

  const cerrarVisor = () => {
    setVisor(v => {
      if (v?.url) URL.revokeObjectURL(v.url);
      return null;
    });
  };

  useEffect(() => {
    const onKey = e => { if (e.key === 'Escape') cerrarVisor(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const totalPaginas = meta?.total_pages || 1;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <button className="nom-btn nom-btn-ghost" onClick={() => navigate('/resultados')}>
            <ArrowLeft size={15} strokeWidth={2} />
            Volver a resultados
          </button>
          <h1 className={styles.title}>Informe de fotografías</h1>
          <p className={styles.subtitle}>
            {meta
              ? `${meta.planta} — Ciclo ${meta.anio} · ${meta.capturadas} de ${meta.muestra} trabajadores con fotografía (${meta.cobertura_pct}%)`
              : 'Evidencia fotográfica de la aplicación de la Guía III'}
          </p>
        </div>
        <div className={styles.headerActions}>
          <button
            className="nom-btn nom-btn-ghost"
            onClick={descargarAnexo}
            disabled={!cicloId || descargandoAnexo || items.length === 0}
            title="Descargar un documento Word con una muestra de 20 fotografías"
          >
            {descargandoAnexo
              ? <Loader2 size={15} className="nom-spin" />
              : <FileDown size={15} strokeWidth={2} />}
            Descargar anexo de fotos
          </button>
        </div>
      </div>

      {error && (
        <div className={styles.aviso}>
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className={styles.centro}>
          <Loader2 size={22} className="nom-spin" />
          <span>Cargando fotografías…</span>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className={styles.centro}>
          <Camera size={22} />
          <span>No hay fotografías en este ciclo.</span>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          <div className={styles.grid}>
            {items.map(item => (
              <button
                key={item.id}
                className={styles.card}
                onClick={() => abrirFoto(item)}
                title="Ver fotografía en grande"
              >
                {item.miniatura
                  ? <img src={item.miniatura} alt="" className={styles.thumb} loading="lazy" />
                  : <div className={styles.sinThumb}><Camera size={18} /></div>}
                <div className={styles.cardInfo}>
                  <span className={styles.numEmpleado}>{item.num_empleado}</span>
                  <span className={styles.area}>{item.area}</span>
                </div>
              </button>
            ))}
          </div>

          {totalPaginas > 1 && (
            <div className={styles.paginacion}>
              <button
                className="nom-btn nom-btn-ghost"
                disabled={pagina <= 1}
                onClick={() => setPagina(p => Math.max(1, p - 1))}
              >
                <ChevronLeft size={15} /> Anterior
              </button>
              <span className={styles.paginaTexto}>
                Página {meta?.page || pagina} de {totalPaginas} · {meta?.total} fotografías
              </span>
              <button
                className="nom-btn nom-btn-ghost"
                disabled={pagina >= totalPaginas}
                onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
              >
                Siguiente <ChevronRight size={15} />
              </button>
            </div>
          )}
        </>
      )}

      {visor && (
        <div className={styles.visorFondo} onClick={cerrarVisor}>
          <div className={styles.visor} onClick={e => e.stopPropagation()}>
            <button className={styles.cerrar} onClick={cerrarVisor} title="Cerrar">
              <X size={18} />
            </button>
            {visor.fallo
              ? <div className={styles.centro}>No se pudo cargar la fotografía.</div>
              : visor.url
                ? <img src={visor.url} alt="" className={styles.visorImg} />
                : <div className={styles.centro}><Loader2 size={22} className="nom-spin" /></div>}
            <div className={styles.visorInfo}>
              <strong>{visor.num_empleado}</strong>
              <span>{visor.area}</span>
              {visor.fecha && <span>{visor.fecha}</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
