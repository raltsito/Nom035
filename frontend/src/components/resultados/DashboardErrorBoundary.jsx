import { Component } from 'react';

export default class DashboardErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('[Dashboard Error]', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          padding: '24px',
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: '12px',
          color: '#EF4444',
          fontSize: '13px',
          lineHeight: 1.6,
        }}>
          <strong>Error al renderizar el dashboard:</strong>
          <pre style={{ marginTop: 8, whiteSpace: 'pre-wrap', fontSize: 11, opacity: 0.8 }}>
            {this.state.error.message}
          </pre>
          <button
            onClick={() => this.setState({ error: null })}
            style={{
              marginTop: 12, padding: '6px 16px', borderRadius: 8,
              background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)',
              color: '#EF4444', cursor: 'pointer', fontSize: 12,
            }}
          >
            Reintentar
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
